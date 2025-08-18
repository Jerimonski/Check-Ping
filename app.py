import subprocess 
import platform
import requests
import json
import time
import threading
import base64
import os
from email.mime.text import MIMEText
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

API_DEVICES_URL = "https://689a0d64fed141b96ba1b4fb.mockapi.io/Ip_List/ip_list"

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
EMAIL_SENDER = "jeremy.amaru.ayaviri@alumnos.uta.cl"
EMAIL_RECEIVER = "jeremy.amaru.ayaviri@alumnos.uta.cl"

devices = []
offDevices = []

gmail_service = None 

PING_COMMAND = ["ping"]
if platform.system().lower() == "windows":
    PING_COMMAND.extend(["-n", "1"])
else:
    PING_COMMAND.extend(["-c", "1"])

def get_gmail_service():
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
    """Crea un mensaje para el email."""
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email_notification(subject, body):
    """
    Envía un correo electrónico de notificación usando el servicio de la API de Gmail.
    """
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
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
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
            "status": "UNKNOWN"
        } for item in data]
        
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener dispositivos de la API: {e}")

def check_status_and_notify():
    while True:
        if not devices:
            fetch_devices_from_api()

        for device in devices:
            old_status = device['status']
            try:
                result = subprocess.run(
                    PING_COMMAND + [device['ip']],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                new_status = "UP" if result.returncode == 0 else "DOWN"
            except (subprocess.TimeoutExpired, Exception):
                new_status = "DOWN"
            if old_status == "UP" and new_status == "DOWN":
                offDevices.append(device)
            device['status'] = new_status
            socketio.emit('status_update', {'devices': devices})
        
        if offDevices:
            fallDevices = []
            for item in offDevices:
                fallDevices.append(item['name'])
                fallDevices.append(item['ip'])
            subject = f"⚠️ Dispositivo/s CAÍDO/S"
            body = '\n '.join(fallDevices)
            send_email_notification(subject, body)  
            offDevices.clear()

        socketio.emit('status_update', {'devices': devices})
        print("Estados actualizados y enviados via WebSocket.")
        time.sleep(30)  


@app.route('/')
def index():
    return devices
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado:', request.sid)
    if devices:
        emit('status_update', {'devices': devices}, room=request.sid)

if __name__ == '__main__':
    gmail_service = get_gmail_service()
    fetch_devices_from_api()  
    threading.Thread(target=check_status_and_notify, daemon=True).start()
    socketio.run(app, debug=True, port=5000)
