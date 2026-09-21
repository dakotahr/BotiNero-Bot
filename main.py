import threading, os, asyncio, random
from flask import Flask
from highrise import BaseBot
from highrise.models import Position
import config

# Corregido: Ahora lee exactamente las variables en español de tu config.py
USER_DUENO = config.ownerName if hasattr(config, 'ownerName') else config.dueño
ID_BOT_SALA = config.botID if hasattr(config, 'botID') else config.botid
NOMBRE_DEL_BOT = config.botName if hasattr(config, 'botName') else config.botname
PREFIX = config.prefix

# ==========================================
# 1. SERVIDOR FALSO PARA RENDER GRATUITO
# ==========================================
app = Flask(__name__)
@app.route('/')
def home(): return f"¡{NOMBRE_DEL_BOT} Avanzado está activo!", 200
def run_flask(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_flask, daemon=True).start()

# ==========================================
# 2. BANCO DE DATOS (FRASES, ANUNCIOS Y TRIVIAS)
# ==========================================
FRASES_ANUNCIOS = [
    f"✨ Recuerda dejar tu Like a la sala de @{USER_DUENO} para apoyarnos. ✨",
    "💫 'El único modo de hacer un gran trabajo es amar lo que haces.' - Steve Jobs 💫",
    "⚠️ Recuerda seguir las reglas de la sala y mantener un ambiente amigable. ⚠️",
    "🌟 'La vida es 10% lo que te pasa y 90% cómo reaccionas a ello.' 🌟",
    "🎁 ¡Disfruta de la música y diviértete con tus amigos aquí! 🎁",
    "🌈 'No cuentes los días, haz que los días cuenten.' 🌈"
]

TRIVIAS = [
    {"p": "¿Cuál es el planeta más cercano al Sol?", "o": "A) Marte | B) Mercurio | C) Venus", "r": "b"},
    {"p": "¿Cuántos minutos tiene una hora?", "o": "A) 50 | B) 100 | C) 60", "r": "c"},
    {"p": "¿Qué gas necesitamos para respirar?", "o": "A) Oxígeno | B) Hidrógeno | C) Nitrógeno", "r": "a"},
    {"p": "¿Cuál es el océano más grande del mundo?", "o": "A) Atlántico | B) Pacífico | C) Índico", "r": "b"}
]

# ==========================================
# 3. PROGRAMACIÓN AVANZADA DEL BOT
# ==========================================
class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.contador_visitas = 0
        self.usuario_a_seguir = None
        self.trivia_activa = False
        self.respuesta_trivia = ""
        # Sistema de seguridad si no existen las coordenadas
        coor = getattr(config, 'coordinates', {'x': 0.0, 'y': 0.0, 'z': 0.0})
        self.bot_pos_x = coor.get('x', 0.0)
        self.bot_pos_y = coor.get('y', 0.0)
        self.bot_pos_z = coor.get('z', 0.0)

    async def bucle_segundo_plano(self):
        contador_anuncio = 0
        while True:
            await asyncio.sleep(5)
            if self.usuario_a_seguir:
                try:
                    room_users = await self.highrise.get_room_users()
                    for user, pos in room_users.content:
                        if user.id == self.usuario_a_seguir or user.username.lower() == str(self.usuario_a_seguir).lower():
                            if isinstance(pos, Position):
                                await self.highrise.walk_to(Position(pos.x, pos.y, pos.z - 0.5))
                except Exception as e: print(f"Error al seguir: {e}")

            contador_anuncio += 5
            if contador_anuncio >= 300:
                contador_anuncio = 0
                await self.highrise.chat(random.choice(FRASES_ANUNCIOS))

    async def on_start(self, session_metadata, room_permissions=None) -> None:
        print(f"¡{NOMBRE_DEL_BOT} ingresó a la sala con éxito!")
        await asyncio.sleep(2)
        await self.highrise.send_emote("dance-tiktok8")
        asyncio.create_task(self.bucle_segundo_plano())

    async def on_chat(self, user, message: str) -> None:
        msg = message.strip().lower()
        print(f"{user.username}: {message}")

        if self.trivia_activa and msg in ["a", "b", "c"]:
            if msg == self.respuesta_trivia:
                self.trivia_activa = False
                await self.highrise.chat(f"🎉 ¡Felicidades @{user.username}! Respondiste correctamente y ganaste la trivia. 🎉")
            return

        if msg == f"{PREFIX}hola":
            await self.highrise.chat(f"¡Hola @{user.username}! Bienvenido/a a la sala. ✨")
        elif msg == f"{PREFIX}bailar":
            await self.highrise.chat("¡A bailar todo el mundo! 💃")
            await self.highrise.send_emote("dance-tiktok8")
        elif msg == f"{PREFIX}aplaudir":
            await self.highrise.send_emote("emote-applause")
        elif msg == f"{PREFIX}visitas":
            await self.highrise.chat(f"📊 Esta sala ha recibido {self.contador_visitas} visitas desde que estoy online.")
        
        elif msg.startswith(f"{PREFIX}emote "):
            emote = message.replace(f"{PREFIX}emote ", "").strip()
            try: await self.highrise.send_emote(emote)
            except: await self.highrise.send_whisper(user.id, "No se pudo ejecutar el emote. Revisa el ID técnico.")

        elif msg.startswith(f"{PREFIX}me "):
            emote = message.replace(f"{PREFIX}me ", "").strip()
            try: await self.highrise.send_emote(emote, user.id)
            except Exception as e: print(f"Error en comando {PREFIX}me: {e}")

        elif msg.startswith(f"{PREFIX}todos ") and user.username.lower() == USER_DUENO.lower():
            emote = message.replace(f"{PREFIX}todos ", "").strip()
            try:
                await self.highrise.chat(f"🥳 ¡Coreografía masiva! Todos hacemos: {emote} 🥳")
                lista = await self.highrise.get_room_users()
                for u, pos in lista.content: await self.highrise.send_emote(emote, u.id)
            except Exception as e: print(f"Error en comando {PREFIX}todos: {e}")

        elif msg == f"{PREFIX}seguir":
            self.usuario_a_seguir = user.id
            await self.highrise.chat(f"🏃‍♂️ Siguiendo a @{user.username}...")
        elif msg.startswith(f"{PREFIX}seguir "):
            self.usuario_a_seguir = message.replace(f"{PREFIX}seguir ", "").replace("@", "").strip()
            await self.highrise.chat(f"🏃‍♂️ Buscando y siguiendo a @{self.usuario_a_seguir}...")
        elif msg == f"{PREFIX}parar":
            self.usuario_a_seguir = None
            await self.highrise.chat("🛑 Me quedo aquí.")

        elif msg == f"{PREFIX}trivia":
            if self.trivia_activa:
                await self.highrise.chat("⚠️ Ya hay una trivia en curso. ¡Responde con A, B o C!")
                return
            preg = random.choice(TRIVIAS)
            self.respuesta_trivia = preg["r"]
            self.trivia_activa = True
            await self.highrise.chat(f"🧠 ¡TRIVIA TIME! 🧠\nPregunta: {preg['p']}\nOpciones: {preg['o']}\n👉 ¡Responde con la letra de la opción!")
            await asyncio.sleep(30)
            if self.trivia_activa:
                self.trivia_activa = False
                await self.highrise.chat(f"⏱️ Tiempo agotado. La respuesta correcta era la ({self.respuesta_trivia.upper()}).")

        elif msg == f"{PREFIX}traer todos" and user.username.lower() == USER_DUENO.lower():
            try:
                await self.highrise.chat("🔮 ¡Teletransportando a todos a mi posición actual! 🔮")
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id != ID_BOT_SALA:
                        await self.highrise.teleport(u.id, Position(self.bot_pos_x, self.bot_pos_y, self.bot_pos_z))
            except Exception as e: print(f"Error en teletransporte masivo: {e}")

    async def on_user_move(self, user, pos) -> None:
        if user.id == ID_BOT_SALA and isinstance(pos, Position):
            self.bot_pos_x, self.bot_pos_y, self.bot_pos_z = pos.x, pos.y, pos.z

    async def on_user_join(self, user, position) -> None:
        self.contador_visitas += 1
        try: await self.highrise.send_whisper(user.id, f"¡Hola {user.username}! Bienvenido a la sala. Pasala genial. ❤️")
        except: pass

# ==========================================
# 4. ENTRADA Y CONEXIÓN AL JUEGO
# ==========================================
if __name__ == "__main__":
    from highrise.__main__ import main, BotDefinition
    definitions = [BotDefinition(Bot(), config.room, config.token)]
    asyncio.run(main(definitions))
