# Escribir un codigo en python para comprobar si una direccion
# IP funciona o esta caida.

# subprocess: Modulo para ejecutar comandos del sistema
# platform: Se ocupa identificar si el codigo se esta ejecutando en Windows o Linux
import subprocess 
import platform

ip_list = {
    "Local":"127.0.0.1",
    "CORTAFUEGO": "10.30.10.1", 
     "SW_PRINCIPAL": "10.30.10.2", 
    "CORTAFUEGO respaldo": "10.30.10.3", 
    "Informatica": "10.30.10.5", 
    "Secretaria Municipal": "10.30.10.6", 
    "Informatica_JP" :"10.30.10.7", 
    "Sala SW_SERVER_MAHO": "10.30.10.8", 
    "Informatica_Jorge": "10.30.10.9", 
    "Servidores": "10.30.10.10", 
    "Traspasado": "10.30.10.11", 
    "Dom": "10.30.10.12", 
    "Finanzas": "10.30.10.13", 
    "Dideco 1": "10.30.10.14", 
    "Transito": "10.30.10.15", 
    "Educacion": "10.30.10.16", 
    "DAO": "10.30.10.17", 
    "Sala Concejo": "10.30.10.18", 
    "Dideco 2": "10.30.10.19", 
    "Secoplac": "10.30.10.20", 
    "Juridico": "10.30.10.21", 
    "Contabilidad": "10.30.10.22", 
    "Licencia Conducir":"10.30.10.23", 
    "DAO 2": "10.30.10.24", 
    "Secoplac 2": "10.30.10.25", 
    "Personal":"10.30.10.26",
}

ping_command = ["ping"]

# determina el sistema operativo del computador y comprueba
# si es windows u otro para modificar el comando "ping' segun
# sea el caso y no tener problemas de tipado.

if platform.system().lower() == "windows":
    ping_command.extend(["-n", "1"])
else:
    ping_command.extend(["-c", "1"])

for name, ip in ip_list.items():
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