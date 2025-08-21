import asyncio
import subprocess 
import platform
import requests
import base64
import os
from datetime import datetime
from email.mime.text import MIMEText
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

API_DEVICES_URL = "https://689a0d64fed141b96ba1b4fb.mockapi.io/Ip_List/ip_list"

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
EMAIL_SENDER = "jeremy.amaru.ayaviri@alumnos.uta.cl"
EMAIL_RECEIVER = "jeremy.amaru.ayaviri@alumnos.uta.cl"

devices = []
gmail_service = None 

PING_COMMAND = ["ping"]
if platform.system().lower() == "windows":
    PING_COMMAND.extend(["-n", "1"])
else:
    PING_COMMAND.extend(["-c", "1"])

def get_gmail_service():
    """
    Inicializa el servicio de Gmail para enviar correos.
    Verifica si las credenciales existen en 'token.json' y las refresca si es necesario.
    Si no existen, inicia el flujo de autorización.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email_notification(subject, body):
    global gmail_service
    if not gmail_service:
        print("Error: El servicio de Gmail no está inicializado.")
        return
    
    try:
        message = create_message(EMAIL_SENDER, EMAIL_RECEIVER, subject, body)
        send_message(gmail_service, 'me', message)
        print(f"Correo de notificación enviado")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

def send_message(service, user_id, message):
    """Envía un mensaje de email."""
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print('An error occurred: %s' % error)

def fetch_devices_from_api():
    global devices
    try:
        res = requests.get(API_DEVICES_URL)
        res.raise_for_status()
        data = res.json()
        
        devices = [{
            "name": item.get('name'),
            "ip": item.get('ip'),
            "status": "Desconocido",
            "active": "Perdido/s",
            "down_count": 0  
        } for item in data]
        
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener dispositivos de la API: {e}")

async def ping_device_async(device):
    """
    Función asíncrona para hacer un solo ping.
    Utiliza asyncio.to_thread para no bloquear el bucle de eventos.
    """
    try:
        result = await asyncio.to_thread(
            subprocess.run,
            PING_COMMAND + [device['ip']], 
            capture_output=True, 
            text=True, 
            timeout=3
        )
        return "Activo" if result.returncode == 0 else "Desconocido"
    except (subprocess.TimeoutExpired, Exception):
        return "Desconocido"

def check_status_and_notify_sync():
    global devices
    
    if not devices:
        fetch_devices_from_api()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    new_statuses = loop.run_until_complete(
        asyncio.gather(*[ping_device_async(device) for device in devices])
    )
    
    off_devices_for_email = []
    
    for i, new_status in enumerate(new_statuses):
        devices[i]['status'] = new_status
        if new_status == "Activo":
            devices[i]['active'] = "Encontrado" 
        if devices[i]["active"] == "Encontrado" and new_status != "Activo": 
            devices[i]["status"] = "Caido"


        if new_status == "Caido" and devices[i]['active'] == "Encontrado":
            devices[i]['down_count'] += 1
            print(devices[i]["name"], "count_down", devices[i]["down_count"])
        else:
            devices[i]['down_count'] = 0
        
        if devices[i]['down_count'] == 8:
            off_devices_for_email.append(devices[i])
            devices[i]['down_count'] = 0

    socketio.start_background_task(target=lambda: socketio.emit('status_update', {'devices': devices}))
    
    if off_devices_for_email:
        fallDevices = [f"{item['name']} ({item['ip']})" for item in off_devices_for_email]
        subject = f"⚠️ Dispositivo/s CAÍDO/S"
        body = 'Dispositivos confirmados como caídos:\n\n' + f'\n {datetime.now()}\n\n'.join(fallDevices)
        send_email_notification(subject, body) 
        print("Notificación de caída enviada.")
        for device in off_devices_for_email:
            device['down_count'] = 0

@app.route('/')
def index():
    return jsonify(devices)

@socketio.on('connect')
def handle_connect():
    if devices:
        emit('status_update', {'devices': devices}, room=request.sid)

if __name__ == '__main__':
    gmail_service = get_gmail_service()
    fetch_devices_from_api()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_status_and_notify_sync, trigger="interval", seconds=30 )
    scheduler.start()
    
    socketio.run(app, debug=True, port=5000)
