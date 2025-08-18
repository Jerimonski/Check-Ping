<div align="center">
<h1 align="center">Estados de red en tiempo real (Backend)</h1>
</div>

<!-- ACERCA DEL PROYECTO -->

## Acerca del proyecto
Este proyecto de backend es el cerebro detrás del sistema de monitoreo. Su función principal es realizar pings en tiempo real a una lista de direcciones IP predefinidas para verificar su estado de conexión. Si un dispositivo deja de responder, el sistema envía una notificación inmediata por correo electrónico. Utiliza WebSockets para comunicar el estado de cada dispositivo al frontend, permitiendo una visualización instantánea y actualizada.

### Motivos del proyecto:

* Monitoreo automatizado y en tiempo real de una cantidad variable de dispositivos.

* Notificación inmediata y automática por correo electrónico al detectar un fallo.

* Comunicación bidireccional y en tiempo real con el frontend para una experiencia de usuario fluida.

## Desarrollado con:
### Tecnologías
* ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
* ![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
* ![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)

<!-- PREPARACIÓN ANTES DEL CÓDIGO -->

## Preparación antes del código
### Clona el repositorio:

1. Clonacion del repositorio:
   ```sh
    git clone https://github.com/Jerimonski/Check-Ping.git
   ```
2. Instala los paquetes de Python necesarios:
  ```sh
    pip install Flask Flask-SocketIO requests google-api-python-client google-auth-oauthlib
   ```

3. Configuración del correo electrónico (Gmail API)
Para que el backend pueda enviar correos de notificación, necesitas configurar la Gmail API.

Ve a la Google Cloud Console.

Crea un nuevo proyecto o selecciona uno existente.

Habilita la API de Gmail.

En la sección "Credenciales", crea una credencial de tipo ID de cliente de OAuth.

Configura la pantalla de consentimiento de OAuth con la información de tu aplicación.

Descarga el archivo credentials.json y colócalo en la misma carpeta que el archivo principal de tu proyecto.

La primera vez que ejecutes la aplicación, se abrirá una ventana del navegador para que inicies sesión en tu cuenta de Gmail y otorgues los permisos necesarios. Esto generará automáticamente el archivo token.json para futuras autenticaciones.

<!-- MODO DE USO -->

## Modo de uso
### Una vez configurado, el backend funcionará de la siguiente manera:

Inicia la aplicación Python desde tu terminal:
   ```sh
      python app.py
   ```

El servidor se ejecutará en http://localhost:5000.

El sistema comenzará a hacer pings a los dispositivos en un hilo en segundo plano.

Si un dispositivo deja de responder, se enviará una notificación por correo electrónico.

El estado de cada dispositivo se actualizará en tiempo real y se transmitirá a través de WebSockets, permitiendo que el frontend refleje los cambios al instante.
