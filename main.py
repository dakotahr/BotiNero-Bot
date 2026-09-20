import threading
import os
import asyncio
from flask import Flask
from highrise import BaseBot
from highrise.models import SessionMetadata, UserPosition, Position

# ==========================================
# 1. SERVIDOR FALSA PARA ENGAÑAR A RENDER (GRATIS)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "¡BotiNera está en línea y funcionando perfectamente!", 200

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Iniciamos Flask en un hilo separado
threading.Thread(target=run_flask, daemon=True).start()


# ==========================================
# 2. PROGRAMACIÓN DIRECTA DEL BOT (FUNCIONES)
# ==========================================
class Bot(BaseBot):
    
    # Se ejecuta cuando el bot entra con éxito a tu sala
    async def on_start(self, session_metadata: SessionMetadata, room_permissions: dict) -> None:
        print("¡BotiNera ingresó con éxito a la sala!")
        # Hace un baile automático al entrar
        await self.highrise.send_emote("dance-tiktok8")

    # Se ejecuta cada vez que un usuario escribe en el chat público
    async def on_chat(self, user: str, message: str) -> None:
        print(f"{user.username}: {message}")
        
        # COMANDO 1: Responder con saludo si alguien escribe !hola
        if message.lower() == "!hola":
            await self.highrise.chat(f"¡Hola @{user.username}! Bienvenido/a a nuestra sala. ✨")
            
        # COMANDO 2: Comando para que el bot baile en la sala
        elif message.lower() == "!bailar":
            await self.highrise.chat("¡A mover el cuerpo! 💃")
            await self.highrise.send_emote("dance-tiktok8")
            
        # COMANDO 3: Comando para que el bot aplauda
        elif message.lower() == "!aplaudir":
            await self.highrise.send_emote("emote-applause")

    # Se ejecuta automáticamente cuando alguien entra a la sala
    async def on_user_join(self, user: str, position: UserPosition) -> None:
        # Le envía un susurro privado automático dándole la bienvenida
        try:
            await self.highrise.send_whisper(user.id, f"¡Hola {user.username}! Bienvenido a la sala de IamDakota. Pasala genial. ❤️")
        except:
            pass


# ==========================================
# 3. CONEXIÓN AUTOMÁTICA USANDO TU CONFIG.PY
# ==========================================
if __name__ == "__main__":
    from highrise.__main__ import main
    from config.config import room, token
    
    # Vinculamos tus accesos directamente con el sistema del juego
    os.environ["apiKey"] = token
    os.environ["roomId"] = room
    os.environ["botClass"] = "main:Bot"
    
    # Encendemos el bot
    asyncio.run(main())
