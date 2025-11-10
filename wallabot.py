from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import config as cf
import os,pickle,telebot, sys

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


def login(driver):
    # entramos en la web
    driver.get('https://es.wallapop.com/')
    sleep(2)
    #aceptamos los terminos y condiciones
    try:
        accept_terms_button = driver.find_element("id","onetrust-accept-btn-handler")
        if(accept_terms_button is not None):
            accept_terms_button.send_keys(Keys.RETURN)
    except:
        pass

def procesa_pagina(driver,entrada):
    haynuevos=False

    driver.get(entrada['url'])

    try:
        #esperamos que carguen los items de la web
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,"a[class*='item-card']")))
        # buscamos todos los productos
        cards = driver.find_elements(By.CSS_SELECTOR,"a[class*='item-card']")
        # print(cards)
        # input("Pulsa una tecla para continuar...")
        for card in cards:
            enlace=card.get_attribute('href')
            try:
                # si esta en la lista previa no se hace nada
                procesados.index(enlace)
            except:
                # si NO esta en la lista previa
                titulo=card.get_attribute('title')
                if ('filtrotitulo' in entrada):
                    if titulo.lower().find(entrada['filtrotitulo'].lower())==-1:
                        # si no cumple el filtro de titulo se ignora
                        continue
                imagen=card.find_element(By.TAG_NAME, "img").get_attribute('src')
                precio=card.find_element(By.CSS_SELECTOR, "strong[class*='Card__price']").text
                if precio=='':
                    precio=card.find_element(By.CLASS_NAME, "item-detail-price_ItemDetailPrice--standard__TxPXr").text
                # enviamos mensaje por telegram
                try:
                    sys.argv.index('-nt')
                except:
                    tb.send_message(cf.telegram_userid,f'<b>TITULO:</b> {titulo}\n<b>PRECIO:</b> {precio}\n<b>ENLACE:</b> {enlace}\n\n<b>IMAGEN:</b> {imagen}',parse_mode='HTML')
                    print(f'Encontrado: {titulo} PRECIO: {precio}')
                #añadimos el enlace
                procesados.append(enlace)
                haynuevos=True
        # si ha habiado algun enlace guardamos la lista
        if (haynuevos):
            with open('procesados.pkl', 'wb') as fp:
                pickle.dump(procesados, fp)
    except Exception as e:
        print(f"Error al procesar la pagina: {e}")
        pass

def main():
    options = webdriver.ChromeOptions()
    # si hay parametro -nh se NO abre en modo headless
    try:
        sys.argv.index('-nh')
    except:
        options.add_argument('--headless=new')
        options.add_argument("--window-position=-2400,-2400")
    loop=True
    while(loop):
        print('Comenzando escaneo...')
        driver = webdriver.Chrome(options=options)
        # preproceso de la web
        login(driver)
        # procesamos los enlaces
        for enlace in cf.OFFERS:
            procesa_pagina(driver, enlace)
        driver.quit()
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