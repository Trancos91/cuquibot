# Cuquibot

Nombrado así por la cuqui, Asiri, es el bot que vamos a usar para organizarnos en la casa. Este repositorio está armado para que otra gente pueda usar o probar el bot, por si les sirve o lo disfrutan :)

> [!note]
> Todo en este proyecto, incluyendo este README, está en proceso de construcción ^^'

# Descripción

El cuquibot es un bot de organización pensado para ayudar a gente(particularmente gente que vive junta, pero se puede usar individualmente sin problemas) a, bueno, organizarse en las tareas del hogar. Tiene varias funciones, que describo a continuación, pero también se pueden ver utilizando el menú "/help" del bot mismo. Si querés, podés pasar directo a la [instalación](#Instalación)

Hay dos maneras principales de interactuar con el bot: Mediante comandos(instrucciones precedidas por "/" para las cuales no es necesario etiquetar al bot), y mediante mensajes donde se lo tagea (si le hablás por privado, no es necesario tagearlo).

### Listas de compras

El bot cuenta, en principio, con seis listas de compras y dos modelos: De supermercado, verdulería, farmacia, varias, mensual de supermercado y mensual de dietética(figura como 'Juanito', porque quienes lo usamos compramos en Juanito. Ya que estamos, recomiendo :P). Además, cuenta con dos listas(iguales a las demás en todo funcionamiento) que contienen ítems de "modelo" para la dietética y la compra mensual de supermercado.

### Lista de tareas

Además de las listas de compras, el bot cuenta con una lista de tareas para anotar cuestiones pendientes a resolver. Este aspecto es uno de los menos desarrollados del bot. ^^'

### Registro de quehaceres

El bot cuenta con una cantidad de verbos relacionados a los quehaceres de la casa. Enviándole mensajes como "@bot barrí", el bot anota en una planilla quién de la gente configurada para usarlo barrió. Además, algunas de estas acciones, como barrí, limpié, trapeé, y otras aceptan "flags" para indicar dónde se llevó a cabo la acción (por ejemplo, "@bot trapeé -aB"). Estas flags, por ahora, se adaptan a los ambientes de nuestro departamento, perdón.

### Recordatorios

Algunos de estos quehaceres son revisados por los recordatorios del bot, que nos da la opción de recordarnos si pasó demasiado tiempo sin hacer alguno de ellos. En el archivo 'recordatorios.yaml' se pueden configurar.

Además de estos recordatorios "condicionales", el bot permite enviar mensajes en determinados días de la semana sin condiciones, también a modo de recordatorios.

### Registro de víveres

El bot cuenta con un registro de víveres en el cual se pueden anotar distintos elementos cuyo uso se quiera rastrear: Utilizando el comando `/registrarviveres` se pueden agregar a la lista, y luego mediante comandos como `@bot abrí el aciete` o `@bot se acabó el aceite` le indicamos cúando abrimos y cuando se acaba cada cosa, para poder tomar nota de cuánto nos duró. Cada vez que se agote un elemento, se agregará cuánto tiempo duró a la hoja de "Duración de víveres".

# Instalación

El bot utiliza una hoja de cálculo de Google Sheets para almacenar sus listas de forma fácilmente accesible(y modificable) para cualquier persona por fuera de la interfaz de Telegram. Podés acceder a un template de la hoja de cálculos [acá](https://docs.google.com/spreadsheets/d/1LflMQbzMTXCNgplX8LKul4460ROzK-eQ7sx4xeHUU-E/edit?usp=sharing).

> [!important]
> Para poder utilizar la función de recordatorios, hay que obtener el chat_id del chat. Esto está explicado en el tutorial de configuración, pero es importante hacerlo antes de seguir utilizando el bot.

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
3. Cuando lo hagas, te va a dar un API Token. Ingresalo en el campo correspondiente de la [config](src/secretos/config.toml) del bot.
4. Usando el comando `/setcommands`, copiá el texto econtrado en [el archivo de comandos](comandos_botfather.txt).
5. Opcionalmente, podés usar el menú del botfather mediante el comando `/mybots` para editar la descripción, foto de perfil y demás información del bot.

## Agregar al bot al grupo donde se lo use

El bot está pensado para ser usado dentro de grupos. Si querés usarlo en un grupo, vas a tener que:

1. Agregar el bot a un grupo y darle privilegios de administrador.
2. Entrar al chat con el BotFather, escribir el comando `/mybots`, seleccionar el bot, e ir a Bot Settings -> Group Privacy y desactivarlo.

> [!note]
> Nada impide que lo uses exclusivamente por privado. Para esto, tendrías que seguir los mismos pasos que antes, sólo que usando el comando `chatid` en una conversación privada con el bot.(Si alguien más le escribe por privado y se registra, lo podría usar, pero no recibiría los mensajes de recordatorios)

## Configurar la hoja de cálculos de google

1. Con tu mail, o con el mail que prefieras, entrá a la [plantilla de la hoja de cálculos](https://docs.google.com/spreadsheets/d/1LflMQbzMTXCNgplX8LKul4460ROzK-eQ7sx4xeHUU-E/edit?usp=sharing), seleccioná File(Archivo) -> Make a copy(Hacer una copia).
2. Podés cambiarle el nombre a tu propia hoja de cálculos, y podés agregarle información manualmente siempre que respetes el formato. Podés usar la info de muestra en la plantilla como referencia. Es preferible que no pongas ninguna información que utilice fechas de forma desordenada, por ejemplo en los registros de quehaceres.

### Configurar cuenta de servicio para el bot

1. Entrá a [la consola de google cloud](https://console.cloud.google.com/) y autenticate con el mail de la planilla.
2. Creá un proyecto:
   - Tocá en "Select a project", o "Seleccionar un proyecto"
   - Seleccioná "New project" o "Nuevo proyecto", arriba a la derecha de la ventana que apareció.
   - Nombrá el proyecto como prefieras(por ejemplo, el nombre del bot).
   - En organización, podés dejarlo sin organización. Tocá crear.
3. Con el buscador, buscá "Google Drive API" y activalo.
4. Buscá con el mismo buscador "Google Sheets API" y activalo.
5. En el menú de navegación (o de "hamburguesa", o de tres barras horizontales a la izquierda del logo de Google cloud), seleccioná "APIs & Services"(o APIs y Servicios). Luego, Credentials. Si no elegiste el proyecto que creaste, te va a pedir que lo hagas ahora.
6. Tocá el botón "+ Create credentials" o "+ Crear credenciales" y seleccioná "Service account" o "Cuenta de servicio".
7. Elegí un nombre para la cuenta, y un ID(podés dejar que rellene automáticamente lo mismo que el nombre).
8. La descripción es opcional. Tocá "Create and continue" o "Crear y continuar".
9. En la lista de roles, buscá `Editor` con el filtro y seleccionalo. Tocá continue(o continuar, se entiende).
10. Tocá Done. No es necesario dar acceso a otrxs usuarixs a la cuenta.
11. Una vez creado el bot, nos llevará al menú de credenciales. Seleccioná el mail del bot que ahora aparece bajo la lista de Service Accounts(o cuentas de servicio).
12. Copiá el mail que aparece en la sección Email, y dale permisos de Editor a dicho mail en la hoja de cálculos del bot. Hacelo en otra pestaña, vamos a tener que volver acá después del paso.
13. Volviendo a la consola de la cuenta de servicio donde estábamos, tocá la pestaña "Keys" o "Llaves".
14. Tocá "Add key" o "Agregar llave", y seleccioná crear una nueva. Te va a ofrecer crearla en JSON o P12. Seleccioná JSON. Esto va a bajar un archivo JSON a tu computadora.
15. Mové el archivo JSON a la carpeta de "secretos" del bot, la que contiene config.toml y recordatorios.yaml.
16. Renombrá el archivo a "credentials.json"

## Configuración del bot

1. En la carpeta "secretos", vas a encontrar un [archivo de configuración](src/secretos/config.toml). Abrilo con tu editor de texto de preferencia.
2. El archivo te va a pedir el API de telegram del bot(el que te dió el BotFather), el chat_id(más sobre esto después, se puede dejar como está), el nombre de usuario del bot, la contraseña para registrar un usuarix, el path hacia credenciales.json, el archivo de identificación para la cuenta de servicio de Google(si lo dejás en la carpeta secretos, es el que está escrito por defecto), y la key de la hoja de cálculos. Además, tiene una sección de aliases para que pongas el nombre de usuario de telegram de cada persona y cómo querés que lo llame (por ejemplo, que le diga a @comedorazuldepapasfritas "Pablo"). **Esta sección existe sólo para almacenar los aliases que registra cada usuarix mediante el comando `/registrarusuarix`**

### Obtener Key de la hoja de cálculos

Abrí la hoja de cálculos. En la barra de direcciones, vas a encontrar la key después del `/d`, y hasta la barra diagonal. Por ejemplo, en:

`docs.google.com/spreadsheets/d/1IAP4HOacD4Az6q_PFfZgIX7lZVoHrRKM9KBX-IMO25s/edit?usp=sharing`

La key sería:

`1IAP4HOacD4Az6q_PFfZgIX7lZVoHrRKM9KBX-IMO25s`

### Obtener el chat_id

Para obtener el chat_id, lo ideal es poner a andar el bot sin ingresar otro grupo en la config, entrar al grupo donde lo quieras usar, y escribir el comando `/chatid`(Si querés usarlo vos solx, podés hacer esto hablando en privado con el bot, aunque recomiendo usar un grupo para no tener que reconfigurar si querés incluír a más gente). El bot te va a responder con el número de ID del chat, y podés copiarlo, pegarlo en la config, y volver a armar el bot. También se puede conseguir usando el telegram con un navegador de internet, pero lo dejo en tus manos.

## Armado del bot dentro de un contenedor docker

Por ahora, el bot no está publicado en DockerHub ni en ningún lado, así que es necesario que lo construyamos. Este instructivo no incluye el proceso de instalar docker, pero no debería ser difícil encontrar tutoriales rápidos al respecto.

Navegá con la terminal hasta la carpeta del proyecto y escribí el siguiente comando:
`docker build --tag cuquibot:latest .`

Podés elegir otro tag, pero vas a tener que modificar el nombre el archivo docker-compose.

### Configuración del archivo docker-compose

Abrí el archivo de [docker-compose](docker-compose.yaml) y modificá los campos comentados (el path hacia la carpeta de secretos, y, si es necesario, la imagen del bot-si cambiaste el tag cuando la construíste- y/o el DNS).

### Ejecución del contenedor

Una vez modificado el archivo de docker-compose, navegá hacia la carpeta del proyecto nuevamente y escribí:
`docker-compose up -d`.

El bot debería quedar funcionando.

> [!warning]
> Acordate de que vas a necesitar poner el bot a andar, usar el comando `/chatid`, copiar la ID del chat a la config y reiniciarlo.

### Reiniciar el bot

Para reiniciar el bot, podés navegar con tu terminal hacia la carpeta del proyecto, y escribir:
`docker-compose down`

y luego nuevamente:
`docker-compose up -d`

## Registro de usuarix

Antes de poder interactuar con el bot, más allá de los comandos básicos de `/start`, `/help`, y `/chatid`, cada persona que piense usar el bot va a tener que escribirle(en el grupo al que se lo haya agregado o por privado) con el comando `/registrarusuarix <contraseña> <apodo>`. La contraseña va a consistir en una serie de caracteres(**_no puede contener espacios_**), seguido por un apodo (este sí, puede contener cualquier caracter). La contraseña va a haber sido definida en el [archivo de configuración](src/secretos/config.toml) al configurar al bot.
