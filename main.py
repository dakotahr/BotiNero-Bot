import threading
import os
import asyncio
from flask import Flask
from highrise import BaseBot

# ==========================================
# 1. SERVIDOR FALSO PARA RENDER GRATUITO
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "¡BotiNera está activa!", 200

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Iniciamos Flask en un hilo separado
threading.Thread(target=run_flask, daemon=True).start()


# ==========================================
# 2. FUNCIONES DEL BOT (COMANDOS)
# ==========================================
class Bot(BaseBot):
    
    # CORRECCIÓN: 'room_permissions' ahora es opcional (=None) para evitar el error del SDK
    async def on_start(self, session_metadata, room_permissions=None) -> None:
        print("¡BotiNera ingresó a la sala con éxito!")
        # Forzamos un breve tiempo de espera para estabilizar la conexión antes de actuar
        await asyncio.sleep(2)
        # Hace un baile automático al entrar al juego
        await self.highrise.send_emote("dance-tiktok8")

    # Se ejecuta cuando alguien escribe en el chat público
    async def on_chat(self, user, message: str) -> None:
        print(f"{user.username}: {message}")
        
        # COMANDO: !hola
        if message.lower() == "!hola":
            await self.highrise.chat(f"¡Hola @{user.username}! Bienvenido/a a la sala. ✨")
            
        # COMANDO: !bailar
        elif message.lower() == "!bailar":
            await self.highrise.chat("¡A bailar todo el mundo! 💃")
            await self.highrise.send_emote("dance-tiktok8")
            
        # COMANDO: !aplaudir
        elif message.lower() == "!aplaudir":
            await self.highrise.send_emote("emote-applause")

    # Se ejecuta automáticamente cuando un usuario se une a la sala
    async def on_user_join(self, user, position) -> None:
        # Saludo privado automático (susurro) al entrar
        try:
            await self.highrise.send_whisper(user.id, f"¡Hola {user.username}! Bienvenido a la sala. Pasala genial. ❤️")
        except:
            pass


# ==========================================
# 3. ENTRADA Y CONEXIÓN AL JUEGO (CONFIG)
# ==========================================
if __name__ == "__main__":
    from highrise.__main__ import main, BotDefinition
    from config.config import room, token
    
    # Configuramos las variables usando el inicio estándar oficial de Highrise
    definitions = [BotDefinition(Bot(), room, token)]
    
    # Ejecuta el sistema del juego pasándole la definición
    asyncio.run(main(definitions))
