from time import sleep
import config as cf
import os,pickle,telebot, sys, logging
from wallapy import check_wallapop


if '-log' in sys.argv:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# inicializamos telegram bot
tb = telebot.TeleBot(cf.telegram_key)

# cargamos la lista de urls procesadas
procesados=[]
if (os.path.isfile('procesados.pkl')):
    try:
        with open('procesados.pkl', 'rb') as fp:
            procesados=pickle.load(fp)
            print('Cargados los enlaces ya procesados de procesados.pkl')
    except:
        print("Error al cargar procesados.pkl")



def procesa_pagina(entrada):
    haynuevos=False

    logging.info(f"Procesando página: {entrada['product_name']}")
    results = check_wallapop(
        product_name=entrada['product_name'],
        keywords=entrada['keywords'],
        min_price=entrada['min_price'],
        max_price=entrada['max_price'],
        excluded_keywords=entrada['excluded_keywords'],
        max_total_items=50,  # Limit the number of listings to retrieve
        order_by="newest", # Sort by price
        time_filter="lastWeek",
    )
    for item in results:
            try:
                # si esta en la lista previa no se hace nada
                procesados.index(item['link'])
            except:
                # enviamos mensaje por telegram
                try:
                    sys.argv.index('-nt')
                except:
                    tb.send_message(cf.telegram_userid,f'<b>TITULO:</b> {item['title']}\n<b>PRECIO:</b> {item['price']}\n<b>ENLACE:</b> {item['link']}\n\n<b>IMAGEN:</b> {item['main_image']}',parse_mode='HTML')
                    logging.info(f'Encontrado: {item['title']} PRECIO: {item['price']}')
                #añadimos el enlace
                procesados.append(item['link'])
                haynuevos=True
        # si ha habido algun enlace guardamos la lista
    if (haynuevos):
        with open('procesados.pkl', 'wb') as fp:
            pickle.dump(procesados, fp)
def main():
    loop=True
    while(loop):
        # procesamos los enlaces
        for producto in cf.OFFERS:
            procesa_pagina(producto)
        #si hay parametro 1 en linea de comandos se sale
        try:
            sys.argv.index('-1')
            return
        except:
            pass
        # esperar hasta siguiente ciclo
        print('Esperando '+str(cf.espera_entre_ciclos)+' segundos')
        sleep(cf.espera_entre_ciclos)


if __name__ == '__main__':
    main()