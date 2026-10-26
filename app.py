
# PASO 1. IMPORTAR LAS DEPENDENCIAS
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import requests
import os
import time
from dotenv import load_dotenv

# PASO 2. CARGAR LAS VARIABLES DE ENTORNO
load_dotenv()

token = os.getenv("tokenTelegram")
chat_id = os.getenv("chatIdTelegram")

# PASO 3. CONFIGURAR FLASK Y SOCKETIO
app = Flask(__name__)
socket = SocketIO(app, cors_allowed_origins="*")

# URL DE TELEGRAM
url_enviar = f"https://api.telegram.org/bot{token}/sendMessage"
url_recibir = f"https://api.telegram.org/bot{token}/getUpdates"



# PASO 4. RUTA PRINCIPAL
@app.route("/")
def inicio():
    return render_template(
        "login.html",
        apiKey=os.getenv("apiKey"),
        authDomain=os.getenv("authDomain"),
        projectId=os.getenv("projectId"),
        storageBucket=os.getenv("storageBucket"),
        messagingSenderId=os.getenv("messagingSenderId"),
        appId=os.getenv("appId"),
        measurementId=os.getenv("measurementId")
    )


# PASO 5. RUTA DEL CHAT
@app.route("/chat")
def chat():
    return render_template(
        "index.html",
        apiKey=os.getenv("apiKey"),
        authDomain=os.getenv("authDomain"),
        projectId=os.getenv("projectId"),
        storageBucket=os.getenv("storageBucket"),
        messagingSenderId=os.getenv("messagingSenderId"),
        appId=os.getenv("appId"),
        measurementId=os.getenv("measurementId")
    )


# PASO 6. ENVIAR MENSAJES A TELEGRAM
def enviarTelegram(texto):
    try:
        respuesta = requests.post(
            url_enviar,
            data={
                "chat_id": chat_id,
                "text": texto
            },
            timeout=10
        )

        datos = respuesta.json()

        if datos.get("ok"):
            print("Mensaje enviado a Telegram")
        else:
            print("Error de Telegram:", datos)

    except requests.RequestException as error:
        print("Error al enviar a Telegram:", error)

palabras_especificas={
    "ayuda":"Alerta: Usuario solicita ayuda",
    "soporte":"Alerta: Usuario solicita apoyo",
    "imagen":"Imagen solicitada",
    "reporte": "Reporte solicitado",
    
}

# PASO 7. RECIBIR MENSAJES DEL CHAT WEB
@socket.on("message")
def recibir_mensaje(mensaje):

    print("Mensaje recibido:", mensaje)

    # COMPARTIR EL MENSAJE CON LOS USUARIOS DEL CHAT
    emit("mensaje", mensaje, broadcast=True)

    # CONVERTIR EL MENSAJE A TEXTO
    texto = str(mensaje).strip()
    texto_minuscula = texto.lower()

    # BUSCAR LAS PALABRAS ESPECIFICAS
    for palabra, alerta in palabras_especificas.items():

        if palabra in texto_minuscula:
            mensaje_telegram = (
                f"{alerta}\n\n"
                f"Mensaje original: {texto}"
            )

            enviarTelegram(mensaje_telegram)
            break


# PASO 8. RECIBIR MENSAJES DESDE TELEGRAM
def recibirTelegram():

    ultimo_id = 0

    while True:
        try:
            respuesta = requests.get(
                url_recibir,
                params={
                    "offset": ultimo_id + 1,
                    "timeout": 10
                },
                timeout=20
            )

            datos = respuesta.json()

            if not datos.get("ok"):
                print("Error al consultar Telegram:", datos)
                time.sleep(2)
                continue

            for actualizacion in datos.get("result", []):

                ultimo_id = actualizacion["update_id"]

                if "message" in actualizacion:
                    mensaje = actualizacion["message"]
                    texto = mensaje.get("text", "")

                    # IGNORAR MENSAJES SIN TEXTO
                    if texto:
                        print("Telegram:", texto)

                        # ENVIAR EL MENSAJE AL CHAT WEB
                        socket.emit(
                            "mensaje_telegram",
                            {"texto": texto}
                        )

        except (requests.RequestException, ValueError) as error:
            print("Error al recibir de Telegram:", error)
            time.sleep(2)


# PASO 9. INICIAR EL SERVIDOR
if __name__ == "__main__":

    hilo = threading.Thread(
        target=recibirTelegram,
        daemon=True
    )
    hilo.start()

    socket.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False
    )
