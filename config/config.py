
import os

prefix = '/'

# Credenciales obtenidas desde variables de entorno
room = os.getenv('HIGHRISE_ROOM_ID', '').strip()
token = os.getenv('HIGHRISE_API_TOKEN', '').strip()

# Datos del bot
botID = '686523fd88522a5a95892544'
botName = 'BotiNero'
ownerName = 'IamDakota'

coordinates = {
    'x': 0,
    'y': 0,
    'z': 0,
    'facing': 'FrontRight'
}

# Comprobar que las credenciales estén configuradas
if not room:
    raise RuntimeError(
        'Falta configurar la variable HIGHRISE_ROOM_ID.'
    )

if not token:
    raise RuntimeError(
        'Falta configurar la variable HIGHRISE_API_TOKEN.'
    )
