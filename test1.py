import subprocess 
import platform
import requests
import json
import time
import threading
import smtplib
import ssl 
from email.mime.text import MIMEText
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

API_DEVICES_URL = "https://689a0d64fed141b96ba1b4fb.mockapi.io/Ip_List/ip_list"

EMAIL_SENDER = "jeremy.amaru.ayaviri@alumnos.uta.cl"  
EMAIL_PASSWORD = "21165692" 
EMAIL_RECEIVER = "jeremy.amaru.ayaviri@alumnos.uta.cl" 
SMTP_SERVER = "smtp.gmail.com" 
SMTP_PORT = 465

devices = []

PING_COMMAND = ["ping"]
if platform.system().lower() == "windows":
    PING_COMMAND.extend(["-n", "1"])
else:
    PING_COMMAND.extend(["-c", "1"])

def send_email_notification(subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ssl.create_default_context()) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"Correo enviado: {subject}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

def fetch_devices_from_api():
    global devices
    try:
        res = requests.get(API_DEVICES_URL)
        res.raise_for_status()
        data = res.json()
        
        devices = [{
            "name": item.get('name'),
            "ip": item.get('ip'),
            "status": "unknown"
        } for item in data]
        
        print("Dispositivos obtenidos de la API:", devices)
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener dispositivos de la API: {e}")
        devices = []

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
                    timeout=1
                )
                new_status = "UP" if result.returncode == 0 else "DOWN"
            except (subprocess.TimeoutExpired, Exception):
                new_status = "DOWN"

            if old_status == "UP" and new_status == "DOWN":
                subject = f"⚠️ Dispositivo {device['name']} CAÍDO"
                body = f"El dispositivo {device['name']} con IP {device['ip']} ha dejado de responder."
                send_email_notification(subject, body)
            
            device['status'] = new_status

        socketio.emit('status_update', {'devices': devices})
        print("Estados actualizados y enviados via WebSocket.")
        time.sleep(5)  

@app.route('/')
def index():
    return "Servidor de monitoreo activo."

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado:', request.sid)
    if devices:
        emit('status_update', {'devices': devices}, room=request.sid)

if __name__ == '__main__':
    fetch_devices_from_api()  
    threading.Thread(target=check_status_and_notify, daemon=True).start()
    socketio.run(app, debug=True, port=5000)
