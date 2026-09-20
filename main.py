import threading
from flask import Flask
from highrise import BaseBot
from src.handlers import CommandHandler, EventHandler

# 1. Servidor web falso para que Render Gratuito no se apague
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot BotiNera Activo", 200

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Iniciamos Flask en un hilo separado
threading.Thread(target=run_flask, daemon=True).start()


# 2. Estructura del bot adaptada de la plantilla
class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.command_handler = CommandHandler(self)
        self.event_handler = EventHandler(self)

    async def on_start(self, session_metadata, room_permissions):
        await self.event_handler.on_start(session_metadata, room_permissions)

    async def on_chat(self, user, message):
        await self.command_handler.on_chat(user, message)

    async def on_user_join(self, user, position):
        await self.event_handler.on_user_join(user, position)

    async def on_user_leave(self, user):
        await self.event_handler.on_user_leave(user)


# 3. Arranque del bot leyendo automáticamente tu config.py
if __name__ == "__main__":
    import asyncio
    from highrise.__main__ import main
    from config.config import room, token
    
    # Configuramos las variables para que el SDK de Highrise las detecte
    import os
    os.environ["apiKey"] = token
    os.environ["roomId"] = room
    os.environ["botClass"] = "main:Bot"
    
    # Ejecuta el bot de Highrise
    asyncio.run(main())
