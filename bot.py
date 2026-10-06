from multiprocessing import Process
import time

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler
)
import os
from dotenv import load_dotenv

load_dotenv()

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

    print(" Bot iniciado...")
    print("Esperando comandos...")

    # Ejecutar bot
    app.run_polling()