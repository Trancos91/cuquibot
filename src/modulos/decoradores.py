import tomllib
from telegram import Update
from telegram.ext import ContextTypes


def requiere_usuarix(func):
    print("Corriento decorador")
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
            print("No hubo error, corriendo función")
            await func(update, context)
    return wrapper

