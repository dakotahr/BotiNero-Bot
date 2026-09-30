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
    return "¡Bot Avanzado está activo!", 200

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
# LISTA DE EMOTES PARA !DANCE
# Puedes editar esta lista en el futuro.
# El número corresponde a la posición del emote.
# ==========================================

DANCE_EMOTES = [
    "emote-kiss",
    "emote-no",
    "emote-sad",
    "emote-yes",
    "emote-laughing",
    "emote-hello",
    "emote-wave",
    "emote-shy",
    "emote-tired",
    "emoji-angry",
    "idle-loop-sitfloor",
    "emoji-thumbsup",
    "emote-lust",
    "emoji-cursing",
    "emote-greedy",
    "emoji-flex",
    "emoji-gagging",
    "emoji-celebrate",
    "dance-macarena",
    "dance-tiktok8",
    "dance-blackpink",
    "emote-model",
    "dance-tiktok2",
    "dance-pennywise",
    "emote-bow",
    "dance-russian",
    "emote-curtsy",
    "emote-snowball",
    "emote-hot",
    "emote-snowangel",
    "emote-charging",
    "dance-shoppingcart",
    "emote-confused",
    "idle-enthusiastic",
    "emote-telekinesis",
    "emote-float",
    "emote-teleporting",
    "emote-swordfight",
    "emote-maniac",
    "emote-energyball",
    "emote-snake",
    "idle-singing",
    "emote-frog",
    "emote-superpose",
    "emote-cute",
    "dance-tiktok9",
    "dance-weird",
    "dance-tiktok10",
    "emote-pose7",
    "emote-pose8",
    "idle-dance-casual",
    "emote-pose1",
    "emote-pose3",
    "emote-pose5",
    "emote-cutey",
    "dance-zombie",
    "dance-duckwalk",
    "dance-smoothwalk",
    "dance-touch",
    "dance-hipshake",
    "dance-blackpink",
    "dance-cheerleader",
    "dance-anime",
    "dance-weird",
    "emote-gravity",
    "sit-relaxed",
    "emote-heartfingers",
    "emote-tapdance",
    "emote-adoringfans",
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
        self.anuncios_activos = True

        # Tareas de emotes en bucle
        self.me_emote_tasks = {}
        self.bot_emote_task = None
        self.dance_emote_tasks = {}

    # Tarea repetitiva para anuncios y seguimiento automático
    # Bucle de emote para usuarios con !me
    async def bucle_me_emote(self, user_id, emote):
        try:
            while True:
                await self.highrise.send_emote(emote, user_id)
                await asyncio.sleep(12)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error en bucle !me: {e}")

    # Bucle de emote para el bot con !emote
    async def bucle_bot_emote(self, emote):
        try:
            while True:
                await self.highrise.send_emote(emote)
                await asyncio.sleep(12)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error en bucle !emote: {e}")

    async def bucle_dance(self, user_id, emote):
        try:
            while True:
                await self.highrise.send_emote(emote, user_id)
                await asyncio.sleep(12)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error en bucle !dance: {e}")
        finally:
            if self.dance_emote_tasks.get(user_id) is asyncio.current_task():
                del self.dance_emote_tasks[user_id]

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

            # 2. Sistema de anuncios automáticos (Modificado con el interruptor)
            if self.anuncios_activos:
                contador_anuncio += 5
                if contador_anuncio >= 300: # Cada 5 minutos
                    contador_anuncio = 0
                    frase = random.choice(FRASES_ANUNCIOS)
                    await self.highrise.chat(frase)
            else:
                contador_anuncio = 0 # Si los apagás, el reloj se congela en cero

    async def on_start(self, session_metadata, room_permissions=None) -> None:
        print("¡BotiNero ingresó a la sala con éxito!")
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

         # --- CONTROL DE ANUNCIOS (Solo Dueño) ---
        elif msg == "!anuncios off" and user.username.lower() == "iamdakota":
            self.anuncios_activos = False
            await self.highrise.chat("🔇 Anuncios automáticos desactivados.")
            
        elif msg == "!anuncios on" and user.username.lower() == "iamdakota":
            self.anuncios_activos = True
            await self.highrise.chat("🔊 Anuncios automáticos activados.")

        # --- SISTEMA DE CLONACIÓN DE ROPA EN MEMORIA ---
        elif msg == "!cloname 1":
            if hasattr(self, 'outfit_fabrica') and self.outfit_fabrica:
                await self.highrise.chat("👕 Volviendo al outfit 1 (Ropa de fábrica)...")
                try:
                    await self.highrise.set_outfit(self.outfit_fabrica)
                except Exception as e:
                    print(f"Error outfit 1: {e}")
            else:
                await self.highrise.send_whisper(user.id, "Aún no tengo guardado mi outfit de fábrica. Usa !cloname solo primero.")

        elif msg == "!cloname 2":
            if hasattr(self, 'outfit_clonado') and self.outfit_clonado:
                await self.highrise.chat("✨ Cambiando al outfit 2 (Clonado)...")
                try:
                    await self.highrise.set_outfit(self.outfit_clonado)
                except Exception as e:
                    print(f"Error outfit 2: {e}")
            else:
                await self.highrise.send_whisper(user.id, "No hay ningún outfit clonado guardado. Usa !cloname solo primero.")

        elif msg == "!cloname":
            await self.highrise.chat("🤖 Analizando tu outfit para clonarlo...")
            try:
                if not hasattr(self, 'outfit_fabrica') or self.outfit_fabrica is None:
                    resultado_bot = await self.highrise.get_my_outfit()
                    self.outfit_fabrica = resultado_bot.outfit
                    print("✅ Outfit de fábrica guardado.")

                resultado_usuario = await self.highrise.get_user_outfit(user.id)
                tu_ropa = resultado_usuario.outfit
                self.outfit_clonado = tu_ropa

                await self.highrise.set_outfit(tu_ropa)
                await self.highrise.chat("✨ ¡Clonación exitosa! Guardado como Outfit 2. Usa '!cloname 1' para volver a fábrica.")
            except Exception as e:
                print(f"Error clonar: {e}")
                await self.highrise.send_whisper(user.id, "❌ No pude clonar tu ropa. ¡Usa prendas básicas de fábrica!")

        # --- COMANDO !DANCE ---
        #
        # !dance 2
        #       -> ejecuta el emote numero 2 una vez
        #
        # !dance 2 loop
        #       -> repite el emote numero 2 sobre el usuario
        #
        # !dance parar
        #       -> detiene el loop de ese usuario

        elif msg.startswith("!dance"):

            partes = message.strip().split()

            if len(partes) == 2 and partes[1].lower() == "parar":
                tarea = self.dance_emote_tasks.get(user.id)

                if tarea:
                    tarea.cancel()
                    await self.highrise.chat(
                        f"🛑 Dejé de repetir el dance para @{user.username}."
                    )
                else:
                    await self.highrise.send_whisper(
                        user.id,
                        "ℹ️ No tienes ningún dance en bucle."
                    )
                return

            if len(partes) < 2:
                await self.highrise.send_whisper(
                    user.id,
                    f"Uso: !dance NUMERO o !dance NUMERO loop. "
                    f"Hay {len(DANCE_EMOTES)} emotes disponibles."
                )
                return

            try:
                numero = int(partes[1])
            except ValueError:
                await self.highrise.send_whisper(
                    user.id,
                    f"❌ Debes usar un número del 1 al {len(DANCE_EMOTES)}."
                )
                return

            if numero < 1 or numero > len(DANCE_EMOTES):
                await self.highrise.send_whisper(
                    user.id,
                    f"❌ El número debe estar entre 1 y {len(DANCE_EMOTES)}."
                )
                return

            emote_solicitado = DANCE_EMOTES[numero - 1]

            if len(partes) >= 3 and partes[2].lower() == "loop":
                tarea_anterior = self.dance_emote_tasks.get(user.id)

                if tarea_anterior:
                    tarea_anterior.cancel()

                tarea = asyncio.create_task(
                    self.bucle_dance(user.id, emote_solicitado)
                )

                self.dance_emote_tasks[user.id] = tarea

                await self.highrise.chat(
                    f"🔁 @{user.username} está haciendo "
                    f"{emote_solicitado} (#{numero}) en bucle."
                )
                return

            try:
                await self.highrise.send_emote(
                    emote_solicitado,
                    user.id
                )
            except Exception as e:
                print(f"Error en comando !dance: {e}")

        # --- DETECTAR CUALQUIER EMOTE INTELIGENTE ---
        #
        # !emote dance-tiktok8
        #       -> ejecuta una vez
        #
        # !emote dance-tiktok8 loop
        #       -> repite el emote
        #
        # !emote parar
        #       -> detiene el loop del bot

        elif msg.startswith("!emote "):
            partes = message.strip().split()

            if len(partes) == 2 and partes[1].lower() == "parar":
                if self.bot_emote_task:
                    self.bot_emote_task.cancel()
                    self.bot_emote_task = None
                    await self.highrise.chat("🛑 Dejé de repetir el emote.")
                return

            if len(partes) >= 3 and partes[2].lower() == "loop":
                emote_solicitado = partes[1]

                if self.bot_emote_task:
                    self.bot_emote_task.cancel()

                self.bot_emote_task = asyncio.create_task(
                    self.bucle_bot_emote(emote_solicitado)
                )

                await self.highrise.chat(
                    f"🔁 Repitiendo {emote_solicitado}."
                )
                return

            if len(partes) < 2:
                await self.highrise.send_whisper(
                    user.id,
                    "Uso: !emote ID o !emote ID loop"
                )
                return

            emote_solicitado = partes[1]

            try:
                await self.highrise.send_emote(emote_solicitado)
            except Exception:
                await self.highrise.send_whisper(
                    user.id,
                    "No se pudo ejecutar ese emote. Asegúrate de escribir bien el ID técnico."
                )

        # --- COMANDO NUEVO: HACER BAILAR AL USUARIO QUE CORRE EL COMANDO ---
        #
        # !me dance-tiktok8
        #       -> ejecuta una vez
        #
        # !me dance-tiktok8 loop
        #       -> repite el emote
        #
        # !me parar
        #       -> detiene el loop de ese usuario

        elif msg.startswith("!me "):
            partes = message.strip().split()

            if len(partes) == 2 and partes[1].lower() == "parar":
                tarea = self.me_emote_tasks.get(user.id)

                if tarea:
                    tarea.cancel()
                    await self.highrise.chat(
                        f"🛑 Dejé de repetir el emote para @{user.username}."
                    )
                else:
                    await self.highrise.chat(
                        f"ℹ️ @{user.username} no tiene un emote en bucle."
                    )
                return

            if len(partes) >= 3 and partes[2].lower() == "loop":
                emote_solicitado = partes[1]

                tarea_anterior = self.me_emote_tasks.get(user.id)
                if tarea_anterior:
                    tarea_anterior.cancel()

                tarea = asyncio.create_task(
                    self.bucle_me_emote(user.id, emote_solicitado)
                )
                self.me_emote_tasks[user.id] = tarea

                await self.highrise.chat(
                    f"🔁 @{user.username} ahora tiene {emote_solicitado} en bucle."
                )
                return

            if len(partes) < 2:
                await self.highrise.send_whisper(
                    user.id,
                    "Uso: !me ID o !me ID loop"
                )
                return

            emote_solicitado = partes[1]

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
                    if u.id != "686523fd88522a5a95892544": # No auto-teletransportar al bot
                        # Los mueve al lugar donde el bot está parado actualmente
                        await self.highrise.teleport(u.id, Position(self.bot_pos_x, self.bot_pos_y, self.bot_pos_z))
            except Exception as e:
                print(f"Error en teletransporte masivo: {e}")

    # Registra la posición del bot continuamente para saber a dónde traer a todos
    async def on_user_move(self, user, pos) -> None:
        if user.id == "686523fd88522a5a95892544": # Si es el bot el que se mueve
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
