import threading
from flask import Flask
from highrise.toml_parser import BaseBot
from src.handlers import CommandHandler, EventHandler
from config.config import room, token

# 1. Servidor web falso para que Render Gratuito no se apague
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot BotiNera Activo", 200

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Iniciamos Flask en un hilo separado
threading.Thread(target=run_flask, daemon=True).start()


# 2. Código original de la plantilla de HseinHa
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


# 3. Arranque del bot usando tus credenciales de config.py
if __name__ == "__main__":
    from highrise.__main__ import *
    import asyncio
    
    # Esto ejecuta el bot de Highrise en paralelo con Render
    asyncio.run(main())
