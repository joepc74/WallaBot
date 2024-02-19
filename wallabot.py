from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import config as cf
import os,pickle,telebot, sys

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
    accept_terms_button = driver.find_element("id","onetrust-accept-btn-handler")
    if(accept_terms_button is not None):
        accept_terms_button.send_keys(Keys.RETURN)

def procesa_pagina(driver,entrada):
    haynuevos=False

    driver.get(entrada['url'])

    try:
        #esperamos que carguen los items de la web
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME,'ItemCardList__item')))

        # buscamos todos los productos
        cards = driver.find_elements(By.CLASS_NAME,"ItemCardList__item")
        # print(cards)
        for card in cards:
            enlace=card.get_attribute('href')
            try:
                # si esta en la lista previa no se hace nada
                procesados.index(enlace)
            except:
                # si NO esta en la lista previa
                titulo=card.get_attribute('title')
                imagen=card.find_element(By.TAG_NAME, "img").get_attribute('src')
                precio=card.find_element(By.CLASS_NAME, "ItemCard__price").text
                # enviamos mensaje por telegram
                tb.send_message(cf.telegram_userid,f'<b>TITULO:</b> {titulo}\n<b>PRECIO:</b> {precio}\n<b>ENLACE:</b> {enlace}\n\n<b>IMAGEN:</b> {imagen}',parse_mode='HTML')
                #añadimos el enlace
                procesados.append(enlace)
                haynuevos=True
        # si ha habiado algun enlace guardamos la lista
        if (haynuevos):
            with open('procesados.pkl', 'wb') as fp:
                pickle.dump(procesados, fp)
    except:
        pass

def main():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    loop=True
    while(loop):
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
            break
        except:
            pass
        # esperar 30 segundos hasta siguiente ciclo
        sleep(30)


if __name__ == '__main__':
    main()