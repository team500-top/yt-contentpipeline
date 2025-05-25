from fastapi import APIRouter, HTTPException, Query, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, desc, func, and_
from sqlalchemy.orm import selectinload
import json
import csv
import io
import zipfile
import os

from database import get_session, DatabaseManager
from models import Video, Task, Channel, SearchQuery, Analytics
from tasks import (
    parse_youtube_search,
    parse_youtube_channel,
    analyze_video_content,
    pause_task as celery_pause_task,
    resume_task as celery_resume_task,
    cancel_task as celery_cancel_task
)

# Создание роутера
api_router = APIRouter()

# ==================== Videos API ====================

@api_router.get("/videos")
async def get_videos(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    video_type: Optional[str] = None,
    sort: str = Query("date", regex="^(date|views|engagement)$")
):
    """Получение списка видео с фильтрацией и пагинацией"""
    async with get_session() as session:
        query = select(Video).where(Video.parse_status == "completed")
        
        # Фильтрация
        if search:
            query = query.where(
                Video.title.ilike(f"%{search}%") | 
                Video.description.ilike(f"%{search}%")
            )
        
        if video_type == "shorts":
            query = query.where(Video.is_short == True)
        elif video_type == "long":
            query = query.where(Video.is_short == False)
        
        # Сортировка
        if sort == "views":
            query = query.order_by(desc(Video.views))
        elif sort == "engagement":
            query = query.order_by(desc(Video.engagement_rate))
        else:
            query = query.order_by(desc(Video.publish_date))
        
        # Пагинация
        result = await DatabaseManager.paginate(session, query, page, per_page)
        
        return {
            "videos": [video.to_dict() for video in result["items"]],
            "pagination": {
                "total": result["total"],
                "page": result["page"],
                "per_page": result["per_page"],
                "pages": result["pages"]
            }
        }

@api_router.get("/videos/{video_id}")
async def get_video(video_id: int):
    """Получение детальной информации о видео"""
    async with get_session() as session:
        stmt = select(Video).where(Video.id == video_id)
        result = await session.execute(stmt)
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(status_code=404, detail="Видео не найдено")
        
        return video.to_dict()

@api_router.post("/videos/{video_id}/analyze")
async def analyze_video(video_id: int, background_tasks: BackgroundTasks):
    """Запуск глубокого анализа видео"""
    async with get_session() as session:
        stmt = select(Video).where(Video.id == video_id)
        result = await session.execute(stmt)
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(status_code=404, detail="Видео не найдено")
        
        # Создание задачи анализа
        task = Task(
            task_id=f"analysis_{video_id}_{datetime.now().timestamp()}",
            task_type="analysis",
            parameters={"video_id": video_id, "video_url": video.video_url},
            status="pending"
        )
        session.add(task)
        await session.commit()
        
        # Запуск Celery задачи
        celery_task = analyze_video_content.delay(task.id, video_id)
        task.task_id = celery_task.id
        await session.commit()
        
        return {"task_id": task.id, "status": "started"}

@api_router.get("/videos/export")
async def export_videos(format: str = Query("csv", regex="^(csv|json)$")):
    """Экспорт видео в CSV или JSON"""
    async with get_session() as session:
        stmt = select(Video).where(Video.parse_status == "completed")
        result = await session.execute(stmt)
        videos = result.scalars().all()
        
        if format == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "video_url", "title", "channel_url", "views", "likes", "comments",
                "engagement_rate", "publish_date", "is_short", "video_category",
                "top_5_keywords"
            ])
            writer.writeheader()
            
            for video in videos:
                writer.writerow({
                    "video_url": video.video_url,
                    "title": video.title,
                    "channel_url": video.channel_url,
                    "views": video.views,
                    "likes": video.likes,
                    "comments": video.comments,
                    "engagement_rate": video.engagement_rate,
                    "publish_date": video.publish_date.isoformat() if video.publish_date else "",
                    "is_short": "Yes" if video.is_short else "No",
                    "video_category": video.video_category or "",
                    "top_5_keywords": ", ".join(video.top_5_keywords or [])
                })
            
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=videos_{datetime.now().strftime('%Y%m%d')}.csv"}
            )
        else:
            data = [video.to_dict() for video in videos]
            return JSONResponse(content=data)

# ==================== Parsing API ====================

@api_router.post("/parse")
async def start_parsing(request_data: Dict[str, Any]):
    """Запуск парсинга YouTube"""
    query = request_data.get("query", "").strip()
    search_type = request_data.get("type", "keyword")
    
    if not query:
        raise HTTPException(status_code=400, detail="Запрос не может быть пустым")
    
    async with get_session() as session:
        # Создание задачи
        task = Task(
            task_id=f"{search_type}_{datetime.now().timestamp()}",
            task_type="search" if search_type == "keyword" else "channel_parse",
            parameters=request_data,
            status="pending"
        )
        session.add(task)
        await session.commit()
        
        # Сохранение поискового запроса
        search_query = SearchQuery(
            query=query,
            search_type=search_type,
            filters=request_data
        )
        session.add(search_query)
        await session.commit()
        
        # Запуск Celery задачи
        if search_type == "keyword":
            celery_task = parse_youtube_search.delay(task.id, request_data)
        else:
            celery_task = parse_youtube_channel.delay(task.id, request_data)
        
        task.task_id = celery_task.id
        await session.commit()
        
        return task.to_dict()

# ==================== Tasks API ====================

@api_router.get("/tasks")
async def get_tasks(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100)
):
    """Получение списка задач"""
    async with get_session() as session:
        query = select(Task).order_by(desc(Task.created_at)).limit(limit)
        
        if status:
            query = query.where(Task.status == status)
        
        result = await session.execute(query)
        tasks = result.scalars().all()
        
        return [task.to_dict() for task in tasks]

@api_router.post("/tasks/{task_id}/pause")
async def pause_task(task_id: int):
    """Приостановка задачи"""
    async with get_session() as session:
        stmt = select(Task).where(Task.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        if task.status != "running":
            raise HTTPException(status_code=400, detail="Задача не выполняется")
        
        # Приостановка Celery задачи
        celery_pause_task(task.task_id)
        
        task.status = "paused"
        task.paused_at = datetime.now()
        await session.commit()
        
        return {"status": "paused"}

@api_router.post("/tasks/{task_id}/resume")
async def resume_task(task_id: int):
    """Возобновление задачи"""
    async with get_session() as session:
        stmt = select(Task).where(Task.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        if task.status != "paused":
            raise HTTPException(status_code=400, detail="Задача не приостановлена")
        
        # Возобновление Celery задачи
        celery_resume_task(task.task_id)
        
        task.status = "running"
        await session.commit()
        
        return {"status": "resumed"}

@api_router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: int):
    """Отмена задачи"""
    async with get_session() as session:
        stmt = select(Task).where(Task.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Задача не найдена")
        
        # Отмена Celery задачи
        celery_cancel_task(task.task_id)
        
        task.status = "cancelled"
        await session.commit()
        
        return {"status": "cancelled"}

@api_router.post("/tasks/pause-all")
async def pause_all_tasks():
    """Приостановка всех активных задач"""
    async with get_session() as session:
        stmt = select(Task).where(Task.status == "running")
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        
        for task in tasks:
            celery_pause_task(task.task_id)
            task.status = "paused"
            task.paused_at = datetime.now()
        
        await session.commit()
        
        return {"paused_count": len(tasks)}

@api_router.post("/tasks/resume-all")
async def resume_all_tasks():
    """Возобновление всех приостановленных задач"""
    async with get_session() as session:
        stmt = select(Task).where(Task.status == "paused")
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        
        for task in tasks:
            celery_resume_task(task.task_id)
            task.status = "running"
        
        await session.commit()
        
        return {"resumed_count": len(tasks)}

@api_router.delete("/tasks/completed")
async def clear_completed_tasks():
    """Удаление завершенных задач"""
    async with get_session() as session:
        stmt = select(Task).where(
            Task.status.in_(["completed", "failed", "cancelled"])
        )
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        
        for task in tasks:
            await session.delete(task)
        
        await session.commit()
        
        return {"deleted_count": len(tasks)}

# ==================== Analytics API ====================

@api_router.get("/analytics/stats")
async def get_analytics_stats():
    """Получение статистики для дашборда"""
    async with get_session() as session:
        # Общая статистика
        total_videos = await session.scalar(
            select(func.count(Video.id)).where(Video.parse_status == "completed")
        )
        
        total_channels = await session.scalar(
            select(func.count(func.distinct(Video.channel_url)))
        )
        
        # Средняя вовлеченность
        avg_engagement = await session.scalar(
            select(func.avg(Video.engagement_rate)).where(Video.engagement_rate > 0)
        )
        
        # Видео за последнюю неделю
        week_ago = datetime.now() - timedelta(days=7)
        videos_this_week = await session.scalar(
            select(func.count(Video.id)).where(
                and_(
                    Video.created_at >= week_ago,
                    Video.parse_status == "completed"
                )
            )
        )
        
        # Топ категория
        top_category_result = await session.execute(
            select(
                Video.video_category,
                func.count(Video.id).label("count")
            )
            .where(Video.video_category.isnot(None))
            .group_by(Video.video_category)
            .order_by(desc("count"))
            .limit(1)
        )
        top_category = top_category_result.first()
        
        # Топ видео по вовлеченности
        top_videos_stmt = select(Video).order_by(
            desc(Video.engagement_rate)
        ).limit(10)
        top_videos_result = await session.execute(top_videos_stmt)
        top_videos = top_videos_result.scalars().all()
        
        return {
            "stats": {
                "totalVideos": total_videos or 0,
                "totalChannels": total_channels or 0,
                "avgEngagement": round(avg_engagement or 0, 2),
                "topCategory": top_category[0] if top_category else "Не определено",
                "videosThisWeek": videos_this_week or 0
            },
            "topVideos": [video.to_dict() for video in top_videos]
        }

@api_router.get("/search-queries")
async def get_search_queries(limit: int = Query(10, ge=1, le=50)):
    """Получение последних поисковых запросов"""
    async with get_session() as session:
        stmt = select(SearchQuery).order_by(desc(SearchQuery.created_at)).limit(limit)
        result = await session.execute(stmt)
        queries = result.scalars().all()
        
        return [
            {
                "id": q.id,
                "query": q.query,
                "type": q.search_type,
                "results": q.total_results,
                "date": q.created_at.isoformat() if q.created_at else None
            }
            for q in queries
        ]

# ==================== Settings API ====================

@api_router.get("/settings")
async def get_settings():
    """Получение настроек приложения"""
    return {
        "youtubeApiKey": os.getenv("YOUTUBE_API_KEY", ""),
        "autoRetry": True,
        "requestDelay": 3
    }

@api_router.post("/settings")
async def save_settings(settings: Dict[str, Any]):
    """Сохранение настроек приложения"""
    # В реальном приложении настройки сохранялись бы в БД
    # Здесь просто возвращаем успех
    return {"status": "saved"}

# ==================== Export/Import API ====================

@api_router.get("/export/database")
async def export_database():
    """Экспорт базы данных"""
    # Создание ZIP архива с базой данных и экспортами
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Добавление базы данных
        db_path = os.getenv("DATABASE_PATH", "youtube_data.db")
        if os.path.exists(db_path):
            zip_file.write(db_path, "youtube_data.db")
        
        # Добавление файлов из папки exports
        exports_dir = os.getenv("EXPORT_DIR", "exports")
        if os.path.exists(exports_dir):
            for filename in os.listdir(exports_dir):
                file_path = os.path.join(exports_dir, filename)
                if os.path.isfile(file_path):
                    zip_file.write(file_path, f"exports/{filename}")
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=youtube_analyzer_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        }
    )

@api_router.post("/import/database")
async def import_database(file: UploadFile = File(...)):
    """Импорт базы данных"""
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Файл должен быть ZIP архивом")
    
    # Сохранение и распаковка архива
    temp_dir = os.getenv("TEMP_DIR", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_path = os.path.join(temp_dir, file.filename)
    
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Распаковка
    with zipfile.ZipFile(temp_path, "r") as zip_file:
        zip_file.extractall(temp_dir)
    
    # Замена базы данных
    new_db_path = os.path.join(temp_dir, "youtube_data.db")
    if os.path.exists(new_db_path):
        db_path = os.getenv("DATABASE_PATH", "youtube_data.db")
        os.replace(new_db_path, db_path)
    
    # Очистка временных файлов
    os.remove(temp_path)
    
    return {"status": "imported"}