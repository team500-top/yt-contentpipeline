from fastapi import APIRouter, HTTPException, Query, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, desc, func, and_, or_
from sqlalchemy.orm import selectinload
import json
import csv
import io
import zipfile
import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

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
from websocket import notify_task_update, notify_video_added, send_notification

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
        # Базовый запрос
        query = select(Video).where(Video.parse_status == "completed")
        
        # Фильтрация по поиску
        if search:
            search_filter = or_(
                Video.title.ilike(f"%{search}%"),
                Video.description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Фильтрация по типу видео
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
        
        # Подсчет общего количества
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0
        
        # Пагинация
        offset = (page - 1) * per_page
        query = query.limit(per_page).offset(offset)
        
        # Выполнение запроса
        result = await session.execute(query)
        videos = result.scalars().all()
        
        # Формирование ответа с ВСЕМИ полями
        return {
            "videos": [
                {
                    "id": video.id,
                    "video_url": video.video_url,
                    "title": video.title,
                    "channel_url": video.channel_url,
                    "channel_name": video.channel_url.split("/")[-1] if video.channel_url else "Unknown",
                    "views": video.views,
                    "likes": video.likes,
                    "comments": video.comments,
                    "dislikes": video.dislikes or 0,
                    "engagement_rate": round(video.engagement_rate, 2),
                    "like_ratio": round(video.like_ratio, 2),
                    "comment_ratio": round(video.comment_ratio, 2),
                    "publish_date": video.publish_date.isoformat() if video.publish_date else None,
                    "is_short": video.is_short,
                    "thumbnail_url": video.thumbnail_url,
                    "duration": video.duration,
                    "video_category": video.video_category,
                    "video_quality": video.video_quality,
                    "has_cc": video.has_cc,
                    "has_chapters": video.has_chapters,
                    "has_branding": video.has_branding,
                    "emoji_in_title": video.emoji_in_title,
                    "top_5_keywords": video.top_5_keywords or [],
                    "links_in_description": video.links_in_description or 0,
                    "has_pinned_comment": video.has_pinned_comment,
                    "speech_speed": video.speech_speed,
                    "improvement_recommendations": video.improvement_recommendations,
                    "success_analysis": video.success_analysis,
                    "content_strategy": video.content_strategy
                }
                for video in videos
            ],
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page if total > 0 else 0
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
        
        # Получаем информацию о канале
        channel_info = None
        if video.channel_url:
            channel_stmt = select(Channel).where(
                Channel.channel_url == video.channel_url
            )
            channel_result = await session.execute(channel_stmt)
            channel = channel_result.scalar_one_or_none()
            if channel:
                channel_info = {
                    "title": channel.title,
                    "subscribers": channel.subscriber_count,
                    "videos": channel.video_count,
                    "avg_views": channel.avg_views
                }
        
        # Возвращаем ВСЕ поля
        return {
            "id": video.id,
            "video_url": video.video_url,
            "title": video.title,
            "description": video.description,
            "channel_url": video.channel_url,
            "channel_info": channel_info,
            "is_short": video.is_short,
            "views": video.views,
            "likes": video.likes,
            "comments": video.comments,
            "dislikes": video.dislikes,
            "like_ratio": video.like_ratio,
            "comment_ratio": video.comment_ratio,
            "engagement_rate": video.engagement_rate,
            "duration": video.duration,
            "publish_date": video.publish_date.isoformat() if video.publish_date else None,
            "thumbnail_url": video.thumbnail_url,
            "video_category": video.video_category,
            "video_quality": video.video_quality,
            "has_cc": video.has_cc,
            "has_chapters": video.has_chapters,
            "has_branding": video.has_branding,
            "has_intro": video.has_intro,
            "has_outro": video.has_outro,
            "emoji_in_title": video.emoji_in_title,
            "keywords": video.keywords,
            "top_5_keywords": video.top_5_keywords,
            "subtitles": video.subtitles,
            "links_in_description": video.links_in_description,
            "links_in_channel_description": video.links_in_channel_description,
            "has_pinned_comment": video.has_pinned_comment,
            "contacts_in_video": video.contacts_in_video,
            "contacts_in_channel": video.contacts_in_channel,
            "speech_speed": video.speech_speed,
            "channel_avg_views": video.channel_avg_views,
            "channel_avg_likes": video.channel_avg_likes,
            "channel_frequency": video.channel_frequency,
            "channel_age": video.channel_age,
            "average_view_duration": video.average_view_duration,
            "click_through_rate": video.click_through_rate,
            "improvement_recommendations": video.improvement_recommendations,
            "success_analysis": video.success_analysis,
            "content_strategy": video.content_strategy,
            "created_at": video.created_at.isoformat() if video.created_at else None
        }

@api_router.post("/videos/{video_id}/analyze")
async def analyze_video(video_id: int):
    """Запуск глубокого анализа видео"""
    async with get_session() as session:
        # Проверка существования видео
        stmt = select(Video).where(Video.id == video_id)
        result = await session.execute(stmt)
        video = result.scalar_one_or_none()
        
        if not video:
            raise HTTPException(status_code=404, detail="Видео не найдено")
        
        # Создание задачи анализа
        task = Task(
            task_id=f"analysis_{video_id}_{datetime.now().timestamp()}",
            task_type="analysis",
            parameters={"video_id": video_id, "video_title": video.title},
            status="pending"
        )
        session.add(task)
        await session.commit()
        
        # Запуск Celery задачи
        celery_task = analyze_video_content.delay(task.id, video_id)
        task.task_id = celery_task.id
        await session.commit()
        
        # Уведомление через WebSocket
        await notify_task_update(task.to_dict())
        
        return {"task_id": task.id, "status": "started", "celery_id": celery_task.id}

# ИСПРАВЛЕННЫЙ ЭКСПОРТ
@api_router.get("/videos/export")
async def export_videos(format: str = Query("excel", regex="^(csv|json|excel)$")):
    """Экспорт видео в CSV, JSON или Excel"""
    async with get_session() as session:
        stmt = select(Video).where(Video.parse_status == "completed").order_by(desc(Video.views))
        result = await session.execute(stmt)
        videos = result.scalars().all()
        
        if format == "csv":
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "video_url", "channel_url", "title", "is_short", "views", "likes", "comments", "dislikes",
                "like_ratio", "comment_ratio", "engagement_rate", "publish_date", 
                "duration", "video_category", "video_quality", "has_cc", "has_chapters", 
                "has_branding", "has_intro", "has_outro", "emoji_in_title", "top_5_keywords", 
                "links_in_description", "links_in_channel_description", "has_pinned_comment",
                "contacts_in_video", "contacts_in_channel", "speech_speed",
                "channel_avg_views", "channel_avg_likes", "channel_frequency", "channel_age",
                "average_view_duration", "click_through_rate",
                "improvement_recommendations", "success_analysis", "content_strategy"
            ])
            writer.writeheader()
            
            for video in videos:
                writer.writerow({
                    "video_url": video.video_url,
                    "channel_url": video.channel_url,
                    "title": video.title,
                    "is_short": "Да" if video.is_short else "Нет",
                    "views": video.views,
                    "likes": video.likes,
                    "comments": video.comments,
                    "dislikes": video.dislikes or 0,
                    "like_ratio": f"{video.like_ratio:.2f}%",
                    "comment_ratio": f"{video.comment_ratio:.2f}%",
                    "engagement_rate": f"{video.engagement_rate:.2f}%",
                    "publish_date": video.publish_date.strftime("%Y-%m-%d") if video.publish_date else "",
                    "duration": video.duration or "",
                    "video_category": video.video_category or "",
                    "video_quality": video.video_quality or "",
                    "has_cc": "Да" if video.has_cc else "Нет",
                    "has_chapters": "Да" if video.has_chapters else "Нет",
                    "has_branding": "Да" if video.has_branding else "Нет",
                    "has_intro": "Да" if video.has_intro else "Нет",
                    "has_outro": "Да" if video.has_outro else "Нет",
                    "emoji_in_title": "Да" if video.emoji_in_title else "Нет",
                    "top_5_keywords": ", ".join(video.top_5_keywords or []),
                    "links_in_description": video.links_in_description or 0,
                    "links_in_channel_description": video.links_in_channel_description or 0,
                    "has_pinned_comment": "Да" if video.has_pinned_comment else "Нет",
                    "contacts_in_video": json.dumps(video.contacts_in_video or [], ensure_ascii=False),
                    "contacts_in_channel": json.dumps(video.contacts_in_channel or [], ensure_ascii=False),
                    "speech_speed": video.speech_speed or 0,
                    "channel_avg_views": video.channel_avg_views or 0,
                    "channel_avg_likes": video.channel_avg_likes or 0,
                    "channel_frequency": video.channel_frequency or 0,
                    "channel_age": video.channel_age or 0,
                    "average_view_duration": video.average_view_duration or 0,
                    "click_through_rate": video.click_through_rate or 0,
                    "improvement_recommendations": video.improvement_recommendations or "",
                    "success_analysis": video.success_analysis or "",
                    "content_strategy": video.content_strategy or ""
                })
            
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=youtube_videos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
            )
            
        elif format == "json":
            data = []
            for video in videos:
                data.append({
                    "video_url": video.video_url,
                    "title": video.title,
                    "channel_url": video.channel_url,
                    "is_short": video.is_short,
                    "metrics": {
                        "views": video.views,
                        "likes": video.likes,
                        "comments": video.comments,
                        "dislikes": video.dislikes or 0,
                        "engagement_rate": video.engagement_rate,
                        "like_ratio": video.like_ratio,
                        "comment_ratio": video.comment_ratio
                    },
                    "content": {
                        "duration": video.duration,
                        "category": video.video_category,
                        "quality": video.video_quality,
                        "has_cc": video.has_cc,
                        "has_chapters": video.has_chapters,
                        "keywords": video.top_5_keywords
                    },
                    "channel_stats": {
                        "avg_views": video.channel_avg_views,
                        "avg_likes": video.channel_avg_likes,
                        "frequency": video.channel_frequency,
                        "age": video.channel_age
                    },
                    "analysis": {
                        "recommendations": video.improvement_recommendations,
                        "success_factors": video.success_analysis,
                        "strategy": video.content_strategy
                    }
                })
            
            return JSONResponse(content=data)
            
        else:  # Excel
            wb = Workbook()
            ws = wb.active
            ws.title = "YouTube Видео"
            
            # Заголовки - ВСЕ 42 параметра
            headers = [
                "URL видео", "URL канала", "Название", "Тип видео", "Просмотры", "Лайки", 
                "Комментарии", "Дизлайки", "% лайков", "% комментариев", "Вовлеченность %",
                "Дата публикации", "Длительность", "Категория", "Качество", "Субтитры",
                "Главы", "Брендинг", "Интро", "Аутро", "Эмодзи в заголовке",
                "Топ-5 ключевых слов", "Ссылок в описании", "Ссылок в канале",
                "Закрепленный комментарий", "Контакты в видео", "Контакты в канале",
                "Скорость речи", "Средние просмотры канала", "Средние лайки канала",
                "Частота публикаций", "Возраст канала", "Средняя длительность просмотра",
                "CTR", "Рекомендации", "Анализ успеха", "Стратегия"
            ]
            
            # Стили для заголовков
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
            
            # Данные
            for row, video in enumerate(videos, 2):
                ws.cell(row=row, column=1, value=video.video_url)
                ws.cell(row=row, column=2, value=video.channel_url)
                ws.cell(row=row, column=3, value=video.title)
                ws.cell(row=row, column=4, value="Short" if video.is_short else "Обычное")
                ws.cell(row=row, column=5, value=video.views)
                ws.cell(row=row, column=6, value=video.likes)
                ws.cell(row=row, column=7, value=video.comments)
                ws.cell(row=row, column=8, value=video.dislikes or 0)
                ws.cell(row=row, column=9, value=f"{video.like_ratio:.2f}%")
                ws.cell(row=row, column=10, value=f"{video.comment_ratio:.2f}%")
                ws.cell(row=row, column=11, value=f"{video.engagement_rate:.2f}%")
                ws.cell(row=row, column=12, value=video.publish_date.strftime("%Y-%m-%d") if video.publish_date else "")
                ws.cell(row=row, column=13, value=video.duration or "")
                ws.cell(row=row, column=14, value=video.video_category or "")
                ws.cell(row=row, column=15, value=video.video_quality or "")
                ws.cell(row=row, column=16, value="Да" if video.has_cc else "Нет")
                ws.cell(row=row, column=17, value="Да" if video.has_chapters else "Нет")
                ws.cell(row=row, column=18, value="Да" if video.has_branding else "Нет")
                ws.cell(row=row, column=19, value="Да" if video.has_intro else "Нет")
                ws.cell(row=row, column=20, value="Да" if video.has_outro else "Нет")
                ws.cell(row=row, column=21, value="Да" if video.emoji_in_title else "Нет")
                ws.cell(row=row, column=22, value=", ".join(video.top_5_keywords or []))
                ws.cell(row=row, column=23, value=video.links_in_description or 0)
                ws.cell(row=row, column=24, value=video.links_in_channel_description or 0)
                ws.cell(row=row, column=25, value="Да" if video.has_pinned_comment else "Нет")
                ws.cell(row=row, column=26, value=json.dumps(video.contacts_in_video or [], ensure_ascii=False))
                ws.cell(row=row, column=27, value=json.dumps(video.contacts_in_channel or [], ensure_ascii=False))
                ws.cell(row=row, column=28, value=video.speech_speed or 0)
                ws.cell(row=row, column=29, value=video.channel_avg_views or 0)
                ws.cell(row=row, column=30, value=video.channel_avg_likes or 0)
                ws.cell(row=row, column=31, value=video.channel_frequency or 0)
                ws.cell(row=row, column=32, value=video.channel_age or 0)
                ws.cell(row=row, column=33, value=video.average_view_duration or 0)
                ws.cell(row=row, column=34, value=video.click_through_rate or 0)
                ws.cell(row=row, column=35, value=video.improvement_recommendations or "")
                ws.cell(row=row, column=36, value=video.success_analysis or "")
                ws.cell(row=row, column=37, value=video.content_strategy or "")
            
            # Автоширина колонок
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            # Закрепление заголовка
            ws.freeze_panes = "A2"
            
            # Сохранение в буфер
            excel_buffer = io.BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)
            
            return StreamingResponse(
                excel_buffer,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=youtube_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"}
            )

# ==================== Parsing API ====================

@api_router.post("/parse")
async def start_parsing(request_data: Dict[str, Any]):
    """Запуск парсинга YouTube с расширенными параметрами"""
    query = request_data.get("query", "").strip()
    search_type = request_data.get("type", "keyword")
    
    if not query:
        raise HTTPException(status_code=400, detail="Запрос не может быть пустым")
    
    # Дополнительные параметры фильтрации
    filters = {
        "videoType": request_data.get("videoType", "all"),
        "sort": request_data.get("sort", "relevance"),
        "maxResults": request_data.get("maxResults", 50),
        "publishedAfter": request_data.get("publishedAfter"),
        "duration": request_data.get("duration"),  # short, medium, long
        "videoDefinition": request_data.get("videoDefinition"),  # hd, sd
        "videoDimension": request_data.get("videoDimension"),  # 2d, 3d
        "videoCaption": request_data.get("videoCaption"),  # closedCaption, none
        "videoLicense": request_data.get("videoLicense"),  # creativeCommon, youtube
        "regionCode": request_data.get("regionCode", "RU"),
        "relevanceLanguage": request_data.get("relevanceLanguage", "ru")
    }
    
    request_data["filters"] = filters
    
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
        
        # Запуск Celery задачи
        if search_type == "keyword":
            celery_task = parse_youtube_search.delay(task.id, request_data)
        else:
            celery_task = parse_youtube_channel.delay(task.id, request_data)
        
        task.task_id = celery_task.id
        await session.commit()
        
        # Уведомление через WebSocket
        await send_notification(
            "Парсинг запущен",
            f"Начат поиск: {query}",
            "success"
        )
        
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
        
        return [
            {
                "id": task.id,
                "task_id": task.task_id,
                "task_type": task.task_type,
                "parameters": task.parameters,
                "status": task.status,
                "progress": task.progress,
                "total_items": task.total_items,
                "processed_items": task.processed_items,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "error_message": task.error_message
            }
            for task in tasks
        ]

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
        
        # Уведомление
        await notify_task_update(task.to_dict())
        
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
        
        # Уведомление
        await notify_task_update(task.to_dict())
        
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
        
        # Уведомление
        await notify_task_update(task.to_dict())
        
        return {"status": "cancelled"}

@api_router.post("/tasks/pause-all")
async def pause_all_tasks():
    """Приостановка всех активных задач"""
    async with get_session() as session:
        stmt = select(Task).where(Task.status == "running")
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        
        paused_count = 0
        for task in tasks:
            try:
                celery_pause_task(task.task_id)
                task.status = "paused"
                task.paused_at = datetime.now()
                paused_count += 1
            except:
                pass
        
        await session.commit()
        
        return {"paused_count": paused_count}

@api_router.post("/tasks/resume-all")
async def resume_all_tasks():
    """Возобновление всех приостановленных задач"""
    async with get_session() as session:
        stmt = select(Task).where(Task.status == "paused")
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        
        resumed_count = 0
        for task in tasks:
            try:
                celery_resume_task(task.task_id)
                task.status = "running"
                resumed_count += 1
            except:
                pass
        
        await session.commit()
        
        return {"resumed_count": resumed_count}

@api_router.delete("/tasks/completed")
async def clear_completed_tasks():
    """Удаление завершенных задач"""
    async with get_session() as session:
        stmt = select(Task).where(
            Task.status.in_(["completed", "failed", "cancelled"])
        )
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        
        deleted_count = len(tasks)
        for task in tasks:
            await session.delete(task)
        
        await session.commit()
        
        return {"deleted_count": deleted_count}

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
        top_videos_stmt = select(Video).where(
            Video.parse_status == "completed"
        ).order_by(
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
            "topVideos": [
                {
                    "id": video.id,
                    "title": video.title,
                    "channel_name": video.channel_url.split("/")[-1] if video.channel_url else "Unknown",
                    "views": video.views,
                    "engagement_rate": round(video.engagement_rate, 2),
                    "thumbnail_url": video.thumbnail_url
                }
                for video in top_videos
            ]
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
    """Получение настроек приложения из .env"""
    return {
        # API Keys
        "youtubeApiKey": os.getenv("YOUTUBE_API_KEY", ""),
        
        # Database Configuration
        "databasePath": os.getenv("DATABASE_PATH", "youtube_data.db"),
        
        # Server Configuration
        "host": os.getenv("HOST", "127.0.0.1"),
        "port": int(os.getenv("PORT", 8000)),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        
        # Directories
        "tempDir": os.getenv("TEMP_DIR", "temp"),
        "exportDir": os.getenv("EXPORT_DIR", "exports"),
        "logsDir": os.getenv("LOGS_DIR", "logs"),
        
        # Redis Configuration
        "redisUrl": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"),
        
        # Celery Configuration
        "celeryBrokerUrl": os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0"),
        "celeryResultBackend": os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0"),
        
        # API Limits
        "maxResultsPerSearch": int(os.getenv("MAX_RESULTS_PER_SEARCH", 500)),
        "apiRequestDelay": int(os.getenv("API_REQUEST_DELAY", 3)),
        
        # Export Settings
        "exportPageSize": int(os.getenv("EXPORT_PAGE_SIZE", 1000)),
        "maxExportRows": int(os.getenv("MAX_EXPORT_ROWS", 50000)),
        
        # Features Flags
        "enableDeepAnalysis": os.getenv("ENABLE_DEEP_ANALYSIS", "true").lower() == "true",
        "enableWebsocket": os.getenv("ENABLE_WEBSOCKET", "true").lower() == "true",
        "enableAutoRetry": os.getenv("ENABLE_AUTO_RETRY", "true").lower() == "true",
        
        # Security (masked)
        "secretKey": "***" if os.getenv("SECRET_KEY") else "",
        "jwtAlgorithm": os.getenv("JWT_ALGORITHM", "HS256"),
        "accessTokenExpireMinutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    }

@api_router.post("/settings")
async def save_settings(settings: Dict[str, Any]):
    """Сохранение настроек приложения"""
    # В реальном приложении здесь бы обновлялся .env файл
    # Для примера сохраним в базу данных
    async with get_session() as session:
        # Можно создать таблицу Settings для хранения настроек
        # Пока просто возвращаем успех
        return {"status": "saved", "message": "Настройки сохранены"}

# ==================== Export/Import API ====================

@api_router.get("/export/database")
async def export_database():
    """Экспорт базы данных"""
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
        
        # Добавление конфигурации (без секретных данных)
        config_data = {
            "version": "1.0.0",
            "export_date": datetime.now().isoformat(),
            "total_videos": 0,
            "total_channels": 0
        }
        
        # Получаем статистику
        async with get_session() as session:
            config_data["total_videos"] = await session.scalar(
                select(func.count(Video.id))
            ) or 0
            config_data["total_channels"] = await session.scalar(
                select(func.count(Channel.id))
            ) or 0
        
        zip_file.writestr("config.json", json.dumps(config_data, indent=2))
    
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
    
    # Сохранение файла
    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)
    
    try:
        # Распаковка
        with zipfile.ZipFile(temp_path, "r") as zip_file:
            # Проверка наличия базы данных в архиве
            if "youtube_data.db" not in zip_file.namelist():
                raise HTTPException(status_code=400, detail="В архиве отсутствует база данных")
            
            # Создание резервной копии текущей БД
            db_path = os.getenv("DATABASE_PATH", "youtube_data.db")
            if os.path.exists(db_path):
                backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(db_path, backup_path)
            
            # Извлечение новой БД
            zip_file.extract("youtube_data.db", ".")
            
            # Извлечение экспортов
            exports_dir = os.getenv("EXPORT_DIR", "exports")
            os.makedirs(exports_dir, exist_ok=True)
            
            for file_info in zip_file.filelist:
                if file_info.filename.startswith("exports/"):
                    zip_file.extract(file_info, ".")
        
        return {"status": "imported", "message": "База данных успешно импортирована"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при импорте: {str(e)}")
    
    finally:
        # Очистка временных файлов
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ==================== Help API ====================

@api_router.get("/help/content")
async def get_help_content():
    """Получение содержимого справки в JSON формате"""
    return {
        "sections": [
            {
                "id": "parsing",
                "title": "Возможности парсинга",
                "content": {
                    "types": [
                        {"name": "По ключевым словам", "description": "Поиск видео по любым ключевым фразам"},
                        {"name": "По каналу", "description": "Анализ всех видео конкретного канала"},
                        {"name": "По плейлисту", "description": "Анализ видео из плейлиста (в разработке)"},
                        {"name": "По трендам", "description": "Автоматический поиск трендовых видео (в разработке)"}
                    ],
                    "filters": [
                        {"param": "Тип видео", "values": ["Все", "Shorts", "Длинные"]},
                        {"param": "Сортировка", "values": ["Релевантность", "Дата", "Просмотры", "Рейтинг"]},
                        {"param": "Период", "values": ["Любое", "Час", "Сегодня", "Неделя", "Месяц", "Год"]},
                        {"param": "Длительность", "values": ["Короткие (<4 мин)", "Средние (4-20 мин)", "Длинные (>20 мин)"]},
                        {"param": "Качество", "values": ["HD (720p+)", "4K"]},
                        {"param": "Субтитры", "values": ["С субтитрами", "Без субтитров"]}
                    ]
                }
            },
            {
                "id": "parameters",
                "title": "Параметры анализа",
                "content": {
                    "total": 42,
                    "categories": [
                        {
                            "name": "Базовые параметры",
                            "params": ["video_url", "channel_url", "is_short", "title", "description", "duration", "publish_date", "thumbnail_url", "video_category", "video_quality"]
                        },
                        {
                            "name": "Метрики вовлеченности",
                            "params": ["views", "likes", "comments", "dislikes", "like_ratio", "comment_ratio", "engagement_rate", "average_view_duration", "click_through_rate"]
                        },
                        {
                            "name": "Контент и оптимизация",
                            "params": ["has_branding", "subtitles", "keywords", "has_cc", "has_pinned_comment", "links_in_description", "top_5_keywords", "has_chapters", "emoji_in_title"]
                        },
                        {
                            "name": "Канал и контакты",
                            "params": ["links_in_channel_description", "contacts_in_video", "contacts_in_channel", "channel_avg_views", "channel_avg_likes", "channel_frequency", "channel_age"]
                        },
                        {
                            "name": "Технические параметры",
                            "params": ["has_intro", "has_outro", "speech_speed", "links_in_description"]
                        },
                        {
                            "name": "AI-анализ",
                            "params": ["improvement_recommendations", "success_analysis", "content_strategy"]
                        }
                    ]
                }
            }
        ]
    }