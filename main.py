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
    return "¡BotiNera Avanzada está activa!", 200

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
        # Variables de estado del bot
        self.contador_visitas = 0
        self.usuario_a_seguir = None
        self.trivia_activa = False
        self.respuesta_trivia = ""
        self.bot_pos_x = 0
        self.bot_pos_y = 0
        self.bot_pos_z = 0

    # Tarea repetitiva para anuncios y seguimiento automático
    async def bucle_segundo_plano(self):
        contador_anuncio = 0
        while True:
            await asyncio.sleep(5) # Se ejecuta cada 5 segundos
            
            # 1. Sistema de seguimiento inteligente
            if self.usuario_a_seguir:
                try:
                    # Buscamos la posición del usuario objetivo en la sala
                    room_users = await self.highrise.get_room_users()
                    for user, pos in room_users.content:
                        if user.id == self.usuario_a_seguir or user.username.lower() == str(self.usuario_a_seguir).lower():
                            if isinstance(pos, Position):
                                # Hacemos que el bot camine hacia el usuario objetivo
                                await self.highrise.walk_to(Position(pos.x, pos.y, pos.z - 0.5))
                except Exception as e:
                    print(f"Error al seguir: {e}")

            # 2. Sistema de anuncios automáticos (Cada 5 minutos = 300 segundos)
            contador_anuncio += 5
            if contador_anuncio >= 300:
                contador_anuncio = 0
                frase = random.choice(FRASES_ANUNCIOS)
                await self.highrise.chat(frase)

    async def on_start(self, session_metadata, room_permissions=None) -> None:
        print("¡BotiNera ingresó a la sala con éxito!")
        await asyncio.sleep(2)
        await self.highrise.send_emote("dance-tiktok8")
        # Iniciamos el bucle inteligente en segundo plano
        asyncio.create_task(self.bucle_segundo_plano())

    async def on_chat(self, user, message: str) -> None:
        msg = message.strip().lower()
        print(f"{user.username}: {message}")

        # --- RESPUESTA A TRIVIAS ACTIVAS ---
        if self.trivia_activa and msg in ["a", "b", "c"]:
            if msg == self.respuesta_trivia:
                self.trivia_activa = False
                await self.highrise.chat(f"🎉 ¡Felicidades @{user.username}! Respondiste correctamente y ganaste la trivia. 🎉")
            return

        # --- COMANDOS BÁSICOS ANTERIORES (CONSERVADOS) ---
        if msg == "!hola":
            await self.highrise.chat(f"¡Hola @{user.username}! Bienvenido/a a la sala. ✨")
        elif msg == "!bailar":
            await self.highrise.chat("¡A bailar todo el mundo! 💃")
            await self.highrise.send_emote("dance-tiktok8")
        elif msg == "!aplaudir":
            await self.highrise.send_emote("emote-applause")

        # --- CONTADOR DE VISITAS ---
        elif msg == "!visitas":
            await self.highrise.chat(f"📊 Esta sala ha recibido {self.contador_visitas} visitas desde que estoy online.")

        # --- DETECTAR CUALQUIER EMOTE INTELIGENTE ---
        elif msg.startswith("!emote "):
            emote_solicitado = message.replace("!emote ", "").strip()
            try:
                await self.highrise.send_emote(emote_solicitado)
            except:
                await self.highrise.send_whisper(user.id, "No se pudo ejecutar ese emote. Asegúrate de escribir bien el ID técnico.")

        # --- COMANDO NUEVO: HACER BAILAR AL USUARIO QUE CORRE EL COMANDO ---
        elif msg.startswith("!me "):
            emote_solicitado = message.replace("!me ", "").strip()
            try:
                await self.highrise.send_emote(emote_solicitado, user.id)
            except Exception as e:
                print(f"Error en comando !me: {e}")

        # --- COMANDO NUEVO: HACER BAILAR A TODOS EN LA SALA (Solo Dueño) ---
        elif msg.startswith("!todos ") and user.username.lower() == "iamdakota":
            emote_solicitado = message.replace("!todos ", "").strip()
            try:
                await self.highrise.chat(f"🥳 ¡Coreografía masiva! Todos hacemos: {emote_solicitado} 🥳")
                lista_usuarios = await self.highrise.get_room_users()
                for u, pos in lista_usuarios.content:
                    await self.highrise.send_emote(emote_solicitado, u.id)
            except Exception as e:
                print(f"Error en comando !todos: {e}")

        # --- SISTEMA DE SEGUIMIENTO ---
        elif msg == "!seguir":
            self.usuario_a_forzar = None
            self.usuario_a_seguir = user.id
            await self.highrise.chat(f"🏃‍♂️ Siguiendo a @{user.username}...")
        
        elif msg.startswith("!seguir "):
            objetivo = message.replace("!seguir ", "").replace("@", "").strip()
            self.usuario_a_seguir = objetivo
            await self.highrise.chat(f"🏃‍♂️ Buscando y siguiendo a @{objetivo}...")

        elif msg == "!parar":
            self.usuario_a_seguir = None
            await self.highrise.chat("🛑 Me quedo aquí.")

        # --- SISTEMA DE TRIVIA ---
        elif msg == "!trivia":
            if self.trivia_activa:
                await self.highrise.chat("⚠️ Ya hay una trivia en curso. ¡Responde con A, B o C!")
                return
            preg = random.choice(TRIVIAS)
            self.respuesta_trivia = preg["r"]
            self.trivia_activa = True
            await self.highrise.chat(f"🧠 ¡TRIVIA TIME! 🧠\nPregunta: {preg['p']}\nOpciones: {preg['o']}\n👉 ¡Responde escribiendo solo la letra de la opción correcta!")
            
            # Tiempo límite de 30 segundos para responder
            await asyncio.sleep(30)
            if self.trivia_activa:
                self.trivia_activa = False
                await self.highrise.chat(f"⏱️ Tiempo agotado. Nadie respondió a tiempo. La respuesta correcta era la ({self.respuesta_trivia.upper()}).")

        # --- COMANDO DE TELETRANSPORTE MASIVO (Solo Dueño) ---
        elif msg == "!traer todos" and user.username.lower() == "iamdakota":
            try:
                await self.highrise.chat("🔮 ¡Teletransportando a todos a mi posición actual! 🔮")
                # Obtenemos la lista de todas las personas en la sala
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id != "68654c84f77cce8a0c95eb1b": # No auto-teletransportar al bot
                        # Los mueve al lugar donde el bot está parado actualmente
                        await self.highrise.teleport(u.id, Position(self.bot_pos_x, self.bot_pos_y, self.bot_pos_z))
            except Exception as e:
                print(f"Error en teletransporte masivo: {e}")

    # Registra la posición del bot continuamente para saber a dónde traer a todos
    async def on_user_move(self, user, pos) -> None:
        if user.id == "68654c84f77cce8a0c95eb1b": # Si es el bot el que se mueve
            if isinstance(pos, Position):
                self.bot_pos_x = pos.x
                self.bot_pos_y = pos.y
                self.bot_pos_z = pos.z

    async def on_user_join(self, user, position) -> None:
        # Sumamos 1 al contador de visitas general de la sala
        self.contador_visitas += 1
        try:
            await self.highrise.send_whisper(user.id, f"¡Hola {user.username}! Bienvenido a la sala. Pasala genial. ❤️")
        except:
            pass


# ==========================================
# 4. ENTRADA Y CONEXIÓN AL JUEGO (CONFIG)
# ==========================================
if __name__ == "__main__":
    from highrise.__main__ import main, BotDefinition
    from config.config import room, token
    
    definitions = [BotDefinition(Bot(), room, token)]
    asyncio.run(main(definitions))
