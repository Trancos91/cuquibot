# Cuquibot

Nombrado así por la cuqui, Asiri, es el bot que vamos a usar para organizarnos en la casa.

# Instalación

**En desarrollo**
El bot utiliza una hoja de cálculo de Google Sheets para almacenar sus listas de forma fácilmente accesible(y modificable) para cualquier persona por fuera de la interfaz de Telegram. Podés acceder a un template de la hoja de cálculos [acá](https://docs.google.com/spreadsheets/d/1LflMQbzMTXCNgplX8LKul4460ROzK-eQ7sx4xeHUU-E/edit?usp=sharing).

Para instalar el bot, vas a tener que:

- Configurar la cuenta de telegram del bot.
- Configurar el acceso del bot de python al google sheets a través de una cuenta de servicio utilizando el API de google.
- Configurar el archivo de config del bot, que va a requerir la siguiente información:
  - Token de API del bot de telegram.
  - Credenciales JSON del API de Google(de la cuenta de servicio).
  - "Key" de la hoja de cálculos de Google.
  - Nombre de usuario del bot.
  - ID del grupo de telegram.

## Configurar la cuenta de telegram del bot

1. En Telegram, buscá el usuario(bot) BotFather.
2. Usando el comando `/newbot`, creá un nuevo usuario de Bot. Te va a pedir que ingreses un nombre visible para dicho bot, así como un nombre de usuario único(de telegram).
3. Cuando lo hagas, te va a dar un API Token. Ingresalo en el campo correspondiente de la config del bot.
