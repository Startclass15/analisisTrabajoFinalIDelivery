# Paso 1. Importar Flask y SocketIO
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import requests
from dotenv import load_dotenv
import os

#Cargar las variables de entorno
load_dotenv()

# Paso 2. Crear la aplicación y configurar SocketIO
app = Flask(__name__)
socket = SocketIO(app, cors_allowed_origins="*")

#token telegrm
token=os.getenv("tokenTelegram")
url=f"https://api.telegram.org/bot{token}/getUpdates"


# Paso 3. Crear la ruta principal
@app.route("/")
def inicio():
    return render_template("login.html",
        apiKey=os.getenv("apiKey"),
        authDomain=os.getenv("authDomain"),
        projectId=os.getenv("projectId"),
        storageBucket= os.getenv("storageBucket"),
        messagingSenderId= os.getenv("messagingSenderId"),
        appId=os.getenv("appId"),
        measurementId=os.getenv("measurementId") 
                           
    )


@app.route("/chat")
def chat():
    return render_template("index.html",
        apiKey=os.getenv("apiKey"),
        authDomain=os.getenv("authDomain"),
        projectId=os.getenv("projectId"),
        storageBucket= os.getenv("storageBucket"),
        messagingSenderId= os.getenv("messagingSenderId"),
        appId=os.getenv("appId"),
        measurementId=os.getenv("measurementId")                  
    )


# Paso 4. Recibir mensajes desde los clientes
@socket.on("message")
def recibir_mensaje(mensaje):

    print("Mensaje recibido:", mensaje)

    # Enviar el mensaje a TODOS los usuarios conectados
    emit("mensaje", mensaje, broadcast=True)

def recibirTelegram():
    id=0
    while True:
        try:
            respuesta=requests.get(url, params={"offset":id+1,"timeout":10}).json()
            for mensaje in respuesta["result"]:
                id=mensaje["update_id"]
                if "message" in mensaje:
                    texto=mensaje["message"].get("text","")
                    socket.emit("mensaje_telegram",{
                        "texto":texto
                    })
                    print(texto)
        except Exception as error:
            print("Error al comunicar ",error)


# Paso 5. Inicializar el servidor
if __name__ == "__main__":

    hilo=threading.Thread(target=recibirTelegram)
    hilo.start()

    socket.run(app, host="0.0.0.0",port=5000, debug=True)