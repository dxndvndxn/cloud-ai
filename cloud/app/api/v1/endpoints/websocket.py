# backend/app/api/v1/endpoints/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
import asyncio
from app.core.logger import logger
from app.api.v1.endpoints.ws_manager import manager


router = APIRouter(tags=["sokot"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # # Отправляем приветственное сообщение при подключении
        # await manager.broadcast({
        #     "type": "connection",
        #     "message": "WebSocket подключен успешно",
        #     "status": "connected"
        # })

        while True:
            # Ожидаем сообщение от клиента
            data = await websocket.receive_text()

            try:
                # Пытаемся распарсить JSON
                logger.info(data)
                message_data = json.loads(data)
                await websocket.send_json({
                    "list_of_ids": message_data
                })

            except json.JSONDecodeError:
                # Если не JSON, обрабатываем как обычный текст
                await websocket.send_json({
                    "type": "text",
                    "message": f"Получено: {data}",
                    "echo": data
                })

    except WebSocketDisconnect:
        print("WebSocket клиент отключился")
    except Exception as e:
        print(f"Ошибка в WebSocket: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass