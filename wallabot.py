from time import sleep

import config as cf
import os,pickle,sqlite3, sys, logging, asyncio
from wallapy import check_wallapop,WallaPyClient
from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_filters, types
from telebot.types import BotCommand

cliente=WallaPyClient()
con=None
# inicializamos telegram bot
bot = AsyncTeleBot(cf.telegram_key)

asyncio.run(bot.set_my_commands([
    BotCommand('start', 'instrucciones de uso del bot'),
    BotCommand('help', 'instrucciones de uso del bot'),
    BotCommand('misseguimientos', 'listado de mis seguimientos activos'),
    BotCommand('mytrackings', 'listado de mis seguimientos activos'),
    ]))

if '-log' in sys.argv:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='wallabot.log', filemode='a')

# cargamos la lista de urls procesadas
procesados=[]
if (os.path.isfile('procesados.pkl')):
    try:
        with open('procesados.pkl', 'rb') as fp:
            procesados=pickle.load(fp)
            logging.info('Cargados los enlaces ya procesados de procesados.pkl')
    except:
        logging.warning("Error al cargar procesados.pkl")

async def procesa_cadena(texto):
    excluidas=[]
    incluidas=[]
    min_price=None
    max_price=None
    for cadena in texto.split():
        if cadena.startswith('-'):
            excluidas.append(cadena[1:])
        elif cadena.startswith('>'):
            try:
                min_price=float(cadena[1:])
            except:
                pass
        elif cadena.startswith('<'):
            try:
                max_price=float(cadena[1:])
            except:
                pass
        else:
            incluidas.append(cadena)
    logging.info(f"Buscando: {incluidas} excluyendo {excluidas} con precio entre {min_price} y {max_price}")
    results = await cliente.check_wallapop(
        product_name=' '.join(incluidas),
        keywords=[],
        min_price=min_price,
        max_price=max_price,
        excluded_keywords=excluidas,
        max_total_items=10,  # Limit the number of listings to retrieve
        order_by="newest", # Sort by price
        time_filter="lastWeek",
    )
    return results

async def procesa_pagina(entrada,chatid):
    global cliente
    haynuevos=False

    logging.info(f"Procesando página: {entrada}")
    results = await procesa_cadena(entrada)
    for item in results:
            try:
                # si esta en la lista previa no se hace nada
                procesados.index(item['link'])
            except:
                # enviamos mensaje por telegram
                try:
                    sys.argv.index('-nt')
                except:
                    await bot.send_message(chatid,f'<b>TITULO:</b> {item["title"]}\n<b>PRECIO:</b> {item["price"]}\n<b>ENLACE:</b> {item["link"]}\n\n<b>IMAGEN:</b> {item["main_image"]}',parse_mode='HTML')
                    logging.info(f'Encontrado: {item['title']} PRECIO: {item['price']}')
                #añadimos el enlace
                procesados.append(item['link'])
                haynuevos=True
        # si ha habido algun enlace guardamos la lista
    if haynuevos:
        with open('procesados.pkl', 'wb') as fp:
            pickle.dump(procesados, fp)

###########################################################
# Comando mytrackings
###########################################################
@bot.message_handler(commands=['start','help'])
async def send_start(message):
    await bot.reply_to(message, 'Este bot te permite seguir productos en Wallapop.\nUsa el comando /mytrackings para ver tus seguimientos activos.\nIntroduce el texto de búsqueda para encontrar productos. Puedes usar >precio para filtrar por precio mínimo y <precio para filtrar por precio máximo. Usa -palabra para excluir resultados que contengan esa palabra.')

###########################################################
# Comando mytrackings
###########################################################
@bot.message_handler(commands=['mytrackings','misseguimientos'])
async def send_mytrackings(message):
    global con
    cursor = con.cursor()
    cursor.execute("SELECT id, track FROM tracks WHERE user_id=?;", (message.from_user.id,))
    seguimientos = cursor.fetchall()
    if not seguimientos:
        await bot.reply_to(message, 'No tienes ningún seguimiento activo.')
        return
    respuesta=""
    for id, track in seguimientos:
        respuesta += f'• {track} - /untrack_{id}\n'
    await bot.reply_to(message, respuesta)
    # await bot.delete_message(message.chat.id, message.id)  # Elimina el mensaje original para evitar spam



@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    if message.from_user.id != cf.telegram_userid:
        logging.warning(f"Usuario no autorizado: {message.from_user.id}")
        await bot.reply_to(message, 'No estás autorizado para usar este bot.')
        return
    logging.info(f"Recibido mensaje: {message.text}")
    if message.text.startswith('/untrack_'):
        track_id = message.text[9:]
        global con
        cursor = con.cursor()
        cursor.execute("DELETE FROM tracks WHERE id=? AND user_id=?;", (track_id, message.from_user.id))
        con.commit()
        await bot.reply_to(message, 'Seguimiento eliminado.')
        return

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    results = await procesa_cadena(message.text)
    salida=f"Resultados:\n\n"
    for item in results:
        salida+=f'<b>TITULO:</b> {item["title"]}\n<b>PRECIO:</b> {item["price"]}\n<b>ENLACE:</b> {item["link"]}\n\n'
    # print(salida)
    keyboard=None
    if len(results)>0:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Track', callback_data=f'/track {message.text}'))

    await bot.send_message(cf.telegram_userid,salida,parse_mode='HTML',disable_web_page_preview=True, reply_markup=keyboard)

###########################################################
# Callbacks para los botones de resultados
# Se ejecuta cuando el usuario pulsa un botón de resultado
###########################################################
@bot.callback_query_handler(func=lambda message: True)
async def callbacks(call):
    if call.data.startswith('/track '):
        logging.info(f"El usuario quiere trackear: {call.data[7:]}")
        con.execute("INSERT INTO tracks (user_id, track) VALUES (?, ?)", (call.message.chat.id, call.data[7:]))
        con.commit()
        await bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None # Pass None to remove all buttons
        )
        await bot.send_message(call.message.chat.id, f"Ahora se hará seguimiento de: {call.data[7:]}")

async def actualiza_trackings():
    global con
    loop=True
    while(loop):
        # procesamos los enlaces
        trackings=con.execute("SELECT * FROM tracks").fetchall()
        for track in trackings:
            id, user_id, texto, last_check = track
            logging.info(f"Procesando seguimiento {id} para el usuario {user_id} con texto: {texto}")
            try:
                await procesa_pagina(texto,user_id)
            except Exception as e:
                logging.error(f"Error procesando producto {texto}: {e}")
        #si hay parametro 1 en linea de comandos se sale
        try:
            sys.argv.index('-1')
            return
        except:
            pass
        # esperar hasta siguiente ciclo
        logging.info('Esperando '+str(cf.espera_entre_ciclos)+' segundos')
        await asyncio.sleep(cf.espera_entre_ciclos)

async def init_db():
    """Initialize the database connection and create the tracks table if it doesn't exist.

    This function sets up the SQLite database for storing tracked stocks information.
    """
    logging.info("Initializing database connection...")
    global con
    con = sqlite3.connect("bot.db")
    con.row_factory = sqlite3.Row
    # Create the tracks table if it doesn't exist
    con.execute("CREATE TABLE IF NOT EXISTS tracks (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, track TEXT, last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")

async def main():
    try:
        bot.add_custom_filter(asyncio_filters.StateFilter(bot))
        L = await asyncio.gather(
            init_db(),
            actualiza_trackings(),
            bot.polling(non_stop=True)
            )
    finally:
        bot.close()

if __name__ == '__main__':
    asyncio.run(main())