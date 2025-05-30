from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Подключение нового клиента"""
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_personal_message(
            {"type": "connection", "message": "Connected to YouTube Analyzer"},
            websocket
        )
    
    def disconnect(self, websocket: WebSocket):
        """Отключение клиента"""
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Отправка сообщения конкретному клиенту"""
        await websocket.send_json(message)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Широковещательная рассылка всем подключенным клиентам"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Удаление отключенных соединений
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

# Глобальный менеджер соединений
manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для real-time обновлений"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Ожидание сообщений от клиента
            data = await websocket.receive_text()
            
            # Обработка команд от клиента
            try:
                message = json.loads(data)
                command = message.get("command")
                
                if command == "ping":
                    await manager.send_personal_message(
                        {"type": "pong", "timestamp": datetime.now().isoformat()},
                        websocket
                    )
                elif command == "subscribe":
                    # Подписка на определенные типы событий
                    await manager.send_personal_message(
                        {"type": "subscribed", "events": message.get("events", [])},
                        websocket
                    )
                
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON"},
                    websocket
                )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Вспомогательные функции для отправки обновлений

async def notify_task_update(task_data: Dict[str, Any]):
    """Уведомление об обновлении задачи"""
    await manager.broadcast({
        "type": "task_update",
        "task": task_data,
        "timestamp": datetime.now().isoformat()
    })

async def notify_video_added(video_data: Dict[str, Any]):
    """Уведомление о добавлении нового видео"""
    await manager.broadcast({
        "type": "video_added",
        "video": video_data,
        "timestamp": datetime.now().isoformat()
    })

async def notify_error(error_message: str, task_id: Optional[int] = None):
    """Уведомление об ошибке"""
    await manager.broadcast({
        "type": "error",
        "message": error_message,
        "task_id": task_id,
        "timestamp": datetime.now().isoformat()
    })

async def send_notification(title: str, message: str, notification_type: str = "info"):
    """Отправка уведомления пользователю"""
    await manager.broadcast({
        "type": "notification",
        "notification": {
            "type": notification_type,
            "title": title,
            "message": message
        },
        "timestamp": datetime.now().isoformat()
    })