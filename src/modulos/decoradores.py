import tomllib
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
import modulos.config as config


def requiere_usuarix(func):
    def chequear_usuarix(update: Update):
        id = str(update.message.from_user.id)
        with open("secretos/config.toml", "rb") as file:
            config = tomllib.load(file)
        try:
            config["users"][id]["alias"]
        except KeyError:
            print("Alguien más está usando el bot! :O")
            print(f"Usuarix: {update.message.from_user.first_name}")
            print(f"ID: {update.message.from_user.id}")
            return "No tenés permitido usar este bot, perdón!"
        return None

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if error := chequear_usuarix(update):
            await update.message.reply_text(error)
            return
        else:
            await func(update, context)
    return wrapper

def logea(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if config.LOG:
            ahora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            print(f"[{ahora}] {func.__name__} ejecutado por {update.effective_sender.first_name}, ID: {update.effective_sender.id}")
        await func(update, context)
    return wrapper
