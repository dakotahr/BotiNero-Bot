import threading
import os
import asyncio
import random
from flask import Flask
from highrise import BaseBot
from highrise.models import Position

# ==========================================
# 1. SERVIDOR FALSO PARA RENDER GRATUITO
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "¡BotiNera Control de Emotes Activa!", 200

def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()


# ==========================================
# 2. BANCO DE DATOS (FRASES, ANUNCIOS Y TRIVIAS)
# ==========================================
FRASES_ANUNCIOS = [
    "✨ Recuerda dejar tu Like a la sala de @IamDakota para apoyarnos. ✨",
    "💫 'El único modo de hacer un gran trabajo es amar lo que haces.' - Steve Jobs 💫",
    "⚠️ Recuerda seguir las reglas de la sala y mantener un ambiente amigable. ⚠️",
    "🌟 'La vida es 10% lo que te pasa y 90% cómo reaccionas a ello.' 🌟",
    "🎁 ¡Disfruta de la música y diviértete con tus amigos aquí! 🎁",
    "⚠️ ¡Escribe '!me [ID]' para bailar tú mismo o '!emote [ID]' para que baile yo! ⚠️"
]

TRIVIAS = [
    {"p": "¿Cuál es el planeta más cercano al Sol?", "o": "A) Marte | B) Mercurio | C) Venus", "r": "b"},
    {"p": "¿Cuántos minutos tiene una hora?", "o": "A) 50 | B) 100 | C) 60", "r": "c"},
    {"p": "¿Qué gas necesitamos para respirar?", "o": "A) Oxígeno | B) Hidrógeno | C) Nitrógeno", "r": "a"},
    {"p": "¿Cuál es el océano más grande del mundo?", "o": "A) Atlántico | B) Pacífico | C) Índico", "r": "b"}
]


# ==========================================
# 3. PROGRAMACIÓN INTERNA DEL BOT
# ==========================================
class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.contador_visitas = 0
        self.usuario_a_seguir = None
        self.trivia_activa = False
        self.respuesta_trivia = ""
        self.bot_pos_x = 0
        self.bot_pos_y = 0
        self.bot_pos_z = 0

    async def bucle_segundo_plano(self):
        contador_anuncio = 0
        while True:
            await asyncio.sleep(5)
            
            # Seguimiento inteligente
            if self.usuario_a_seguir:
                try:
                    room_users = await self.highrise.get_room_users()
                    for user, pos in room_users.content:
                        if user.id == self.usuario_a_seguir or user.username.lower() == str(self.usuario_a_seguir).lower():
                            if isinstance(pos, Position):
                                await self.highrise.walk_to(Position(pos.x, pos.y, pos.z - 0.5))
                except Exception as e:
                    print(f"Error al seguir: {e}")

            # Anuncios automáticos (Cada 5 minutos)
            contador_anuncio += 5
            if contador_anuncio >= 300:
                contador_anuncio = 0
                frase = random.choice(FRASES_ANUNCIOS)
                await self.highrise.chat(frase)

    async def on_start(self, session_metadata, room_permissions=None) -> None:
        print("¡BotiNera ingresó a la sala con éxito!")
        await asyncio.sleep(2)
        await self.highrise.send_emote("dance-tiktok8")
        asyncio.create_task(self.bucle_segundo_plano())

    async def on_chat(self, user, message: str) -> None:
        msg = message.strip().lower()

        # Respuesta a trivia activa
        if self.trivia_activa and msg in ["a", "b", "c"]:
            if msg == self.respuesta_trivia:
                self.trivia_activa = False
                await self.highrise.chat(f"🎉 ¡Felicidades @{user.username}! Respondiste correctamente y ganaste la trivia. 🎉")
            return

        # Comandos básicos
        if msg == "!hola":
            await self.highrise.chat(f"¡Hola @{user.username}! Bienvenido/a a la sala. ✨")
        elif msg == "!bailar":
            await self.highrise.chat("¡A bailar todo el mundo! 💃")
            await self.highrise.send_emote("dance-tiktok8")
        elif msg == "!aplaudir":
            await self.highrise.send_emote("emote-applause")
        elif msg == "!visitas":
            await self.highrise.chat(f"📊 Esta sala ha recibido {self.contador_visitas} visitas desde que estoy online.")

        # --- EMOTE DEL BOT ---
        elif msg.startswith("!emote "):
            emote_solicitado = message.replace("!emote ", "").strip()
            try:
                await self.highrise.send_emote(emote_solicitado)
            except:
                pass

        # --- 🔥 NUEVO: FORZAR EMOTE AL USUARIO QUE EJECUTÓ EL COMANDO 🔥 ---
        elif msg.startswith("!me "):
            emote_solicitado = message.replace("!me ", "").strip()
            try:
                # El bot le ordena al servidor del juego hacer bailar al usuario específico
                await self.highrise.send_emote(emote_solicitado, user.id)
            except Exception as e:
                print(f"Error al forzar emote a usuario: {e}")

        # --- 🔥 NUEVO: BAILAR TODOS JUNTOS (Solo Dueño) 🔥 ---
        elif msg.startswith("!todos ") and user.username.lower() == "iamdakota":
            emote_solicitado = message.replace("!todos ", "").strip()
            try:
                await self.highrise.chat(f"🥳 ¡Sincronizando pasos! Todos bailamos {emote_solicitado} 🥳")
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    # Aplica el baile a cada una de las personas en la sala
                    await self.highrise.send_emote(emote_solicitado, u.id)
            except Exception as e:
                print(f"Error en baile masivo: {e}")

        # Seguimiento e interacciones
        elif msg == "!seguir":
            self.usuario_a_seguir = user.id
            await self.highrise.chat(f"🏃‍♂️ Siguiendo a @{user.username}...")
        elif msg.startswith("!seguir "):
            objetivo = message.replace("!seguir ", "").replace("@", "").strip()
            self.usuario_a_seguir = objetivo
            await self.highrise.chat(f"🏃‍♂️ Buscando y siguiendo a @{objetivo}...")
        elif msg == "!parar":
            self.usuario_a_seguir = None
            await self.highrise.chat("🛑 Me quedo aquí.")

        # Sistema de Trivia
        elif msg == "!trivia":
            if self.trivia_activa:
                await self.highrise.chat("⚠️ Ya hay una trivia en curso. ¡Responde con A, B o C!")
                return
            preg = random.choice(TRIVIAS)
            self.respuesta_trivia = preg["r"]
            self.trivia_activa = True
            await self.highrise.chat(f"🧠 ¡TRIVIA TIME! 🧠\nPregunta: {preg['p']}\nOpciones: {preg['o']}\n👉 ¡Responde escribiendo solo la letra de la opción correcta!")
            
            await asyncio.sleep(30)
            if self.trivia_activa:
                self.trivia_activa = False
                await self.highrise.chat(f"⏱️ Tiempo agotado. La respuesta correcta era la ({self.respuesta_trivia.upper()}).")

        # Teletransporte Masivo (Solo Dueño)
        elif msg == "!traer todos" and user.username.lower() == "iamdakota":
            try:
                await self.highrise.chat("🔮 ¡Teletransportando a todos a mi posición actual! 🔮")
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id != "68654c84f77cce8a0c95eb1b":
                        await self.highrise.teleport(u.id, Position(self.bot_pos_x, self.bot_pos_y, self.bot_pos_z))
            except Exception as e:
                print(f"Error en teletransporte masivo: {e}")

    async def on_user_move(self, user, pos) -> None:
        if user.id == "68654c84f77cce8a0c95eb1b":
            if isinstance(pos, Position):
                self.bot_pos_x = pos.x
                self.bot_pos_y = pos.y
                self.bot_pos_z = pos.z

    async def on_user_join(self, user, position) -> None:
        self.contador_visitas += 1
        try:
            await self.highrise.send_whisper(user.id, f"¡Hola {user.username}! Bienvenido a la sala. Pasala genial. ❤️")
        except:
            pass
