from multiprocessing import Process
import time
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from google import genai

import os
from dotenv import load_dotenv


load_dotenv()

apiGoogle=os.getenv("apiGoogle")
#Paso1. configurar gemini
cliente=genai.Client(api_key=apiGoogle)
modelo="gemini-3.5-flash-lite"
#Paso2. Configurar las funcion de informacion de conocimiento
def cargarInformacion():
    try: 
        with open("chat/informacion.txt","r",encoding="utf-8") as archivo:
            return archivo.read()
    except FileNotFoundError:
        return ""



async def responder(update:Update,context:ContextTypes.DEFAULT_TYPE):
    pregunta=update.message.text
    contexto=cargarInformacion()
    if not contexto.strip():
        await update.message.reply_text("Error al activar la base de conocimiento...")
        return
    mensajeEspera=await update.message.reply_text("Analizando...")
    try:
        indicacion=f"""
            Debes responder de forma cordial las consultas de los usuarios
            Solo debes utilizar como fuente principal el siguiente archivo: 
            {contexto}

            Reglas:
            1. Responde solo basandote en el material proporcianado
            2. Si no tienes informacion suficiente puedes buscarlo en tu base de datos
            pero sin salir del tema especifico para tu busqueda
            3. Usa mensajes cortos, respondiendo los mas humano posible como un asistente de atencion al cliente
            4. recepciona y solicita datos para registro de los interesados puedes ser persuasvio

            Pregunta de la persona: {pregunta}
        """
        respuesta=await asyncio.to_thread(
            cliente.models.generate_content,
                model=modelo,
                contents=indicacion
        )
        texto=respuesta.text or ("Error al procesar")
        for inicio in range(0,len(texto),2000):
            await update.message.reply_text(texto[inicio:inicio+2000])
    except Exception as error:
        print("Error al conectar",error)

async def imagenEnviar(update:Update,context:ContextTypes.DEFAULT_TYPE):
    with open("telegram.jpg","rb") as imagen:
        await update.message.reply_photo(photo=imagen)

async def pdfEnviar(update:Update,context:ContextTypes.DEFAULT_TYPE):
    with open("practica.pdf","rb") as pdf:
        await update.message.reply_document(pdf)

async def audioEnviar(update:Update,context:ContextTypes.DEFAULT_TYPE):
    with open("musica.mp3","rb") as musica:
        await update.message.reply_audio(musica)

def simulacion():
    print("Proceso iniciado...")

    for i in range(1, 11):
        print(f"Proceso {i} iniciado")
        time.sleep(1)

    print("Proceso finalizado")




async def procesar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Crear un nuevo proceso
    proceso = Process(target=simulacion)

    # Iniciar el proceso
    proceso.start()

   
    await update.message.reply_text(
        f"✅ Proceso iniciado correctamente.\n"
        f"PID del proceso: {proceso.pid}"
    )




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Hola, bienvenido al bot.\n\n"
        "Comandos disponibles:\n"
        "/procesar - Iniciar un proceso\n"
        "/productos - Ver productos"
    )




async def productos(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🛒 PRODUCTOS\n\n"
        "1. Laptop\n"
        "2. Mouse\n"
        "3. Teclado\n"
        "4. Monitor"
    )




if __name__ == "__main__":

    
    TOKEN =os.getenv("tokenTelegram")

    
    app = ApplicationBuilder().token(TOKEN).build()

   
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("procesar", procesar))
    app.add_handler(CommandHandler("productos", productos))
    app.add_handler(CommandHandler("imagen",imagenEnviar))
    app.add_handler(CommandHandler("practica",pdfEnviar))
    app.add_handler(CommandHandler("musica",audioEnviar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,responder))

    print(" Bot iniciado...")
    print("Esperando comandos...")

    # Ejecutar bot
    app.run_polling()