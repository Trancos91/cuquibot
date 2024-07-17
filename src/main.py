import datetime
from pytz import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, Defaults, CallbackQueryHandler, PollAnswerHandler)


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text('Holi, soy el Cuquibot, miau!'
        ' Escribí "/help" para ver los comandos disponibles :3')
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = ('A implementar nya')

    await update.message.reply_text(mensaje)
