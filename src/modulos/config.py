"""
Singleton de módulo que contiene la info de config, la carga al comienzo y permite
actualizar los recordatorios
"""
import tomllib
import yaml

TOKEN = ""
BOT_USERNAME = ""
CHAT_ID = ""
PASSWD = ""
LOG = False
 
GOOGLE_API = ""
WORKSHEET_URL = ""

RECORDATORIOS = {}

def cargar_config(path="secretos/config.toml"):
    try:
        with open(path, "rb") as file:
            config = tomllib.load(file)
            global TOKEN
            global BOT_USERNAME
            global CHAT_ID
            global LOG
            TOKEN = config["telegram"]["tg_api"].strip()
            BOT_USERNAME = config["telegram"]["bot_user"]
            CHAT_ID = config["telegram"]["chat_id"]
            try:
                LOG = config["telegram"]["log"]
                print("Logeando las interacciones con el bot")
            except KeyError:
                print("Sin logear las interacciones con el bot")
                LOG = False
    except FileNotFoundError:
        raise FileNotFoundError("ERROR: No se encontró un archivo toml de configuración! Asegurate de que exista.")

def cargar_recordatorios(path="secretos/recordatorios.yaml"):
    try:
        global RECORDATORIOS
        with open("secretos/recordatorios.yaml", "rb") as file:
            RECORDATORIOS = yaml.safe_load(file)
    except FileNotFoundError:
        print("ERROR: No se encontró un archivo yaml de recordatorios! Asegurate de que exista.")

def actualizar_recordatorios(path="secretos/recordatorios.yaml"):
    with open(path, "w") as file:
        yaml.safe_dump(RECORDATORIOS, file, indent=2, allow_unicode=True)
