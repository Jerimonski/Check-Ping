# Escribir un codigo en python para comprobar si una direccion
# IP funciona o esta caida

#hacer una web que haga un ping constante en vivo de los ip que tenga
#se debe poder ver en tiempo real los dispositivos acticos y cuando
# uno se caiga, debe manda un correo avisando de que se cayo

# subprocess: Modulo para ejecutar comandos del sistema
# platform: Se ocupa identificar si el codigo se esta ejecutando en Windows o Linux
# requests: Modulo para hacer peticiones a una API
#json: transforma la respuesta de la API a un json.

import subprocess 
import platform
import requests
import json
import socket
import ipaddress

res = requests.get("https://689a0d64fed141b96ba1b4fb.mockapi.io/Ip_List/ip_list")
response = json.loads(res.text)

ping_command = ["ping"]

# determina el sistema operativo del computador y comprueba
# si es windows u otro para modificar el comando "ping' segun
# sea el caso y no tener problemas de tipado.

if platform.system().lower() == "windows":
    ping_command.extend(["-n", "1"])
else:
    ping_command.extend(["-c", "1"])

for item in response:
    name = item.get('name')
    ip = item.get('ip')
    network_mask = ipaddress.ip_network(f"{ip}/24", strict=False)
    subnet_mask = network_mask.netmask
    try:
        # se encarga de transformar el mensaje de respuesta 
        # a texto legible, donde captura la respuesta y el texto, 
        # con un tiempo maximo de respuesta de 1 segundo.
        result = subprocess.run(
            ping_command + [ip],
            capture_output=True,
            text=True,
            timeout=1
        )
        # siguiendo la convencion, cualquier respuesta igual a 0,
        # es una respuesta exitosa y cualquier otra es erronea
        if result.returncode == 0:
            print(f"✅ {name} ({ip}): Host esta en linea.")
        else:
            print(f"❌ {name} ({ip}): Host no responde.")
    except subprocess.TimeoutExpired:
        print(f"⚠️ {name} ({ip}): Tiempo de espera agotado.")
    except Exception as error:
        print(f"❌ {name} ({ip}): Error al ejecutar el ping: {error}")