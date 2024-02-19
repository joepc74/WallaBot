from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import config as cf
import os,pickle,telebot

tb = telebot.TeleBot(cf.telegram_key)

primervideo=True
procesados=[]
if (os.path.isfile('procesados.pkl')):
    try:
        with open('procesados.pkl', 'rb') as fp:
            procesados=pickle.load(fp)
            print('Cargados los enlaces ya procesados de procesados.pkl')
    except:
        print("Error al cargar procesados.pkl")


def login(driver):
    driver.get('https://es.wallapop.com/')
    sleep(2)
    accept_terms_button = driver.find_element("id","onetrust-accept-btn-handler")
    if(accept_terms_button is not None):
        accept_terms_button.send_keys(Keys.RETURN)

def procesa_pagina(driver,entrada):
    haynuevos=False

    driver.get(entrada['url'])

    try:
        # sleep(10)
        # saltar_terms_button = driver.find_element(By.LINK_TEXT,"Saltar")
        # saltar_terms_button.click()
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME,'ItemCardList__item')))

        cards = driver.find_elements(By.CLASS_NAME,"ItemCardList__item")
        # print(cards)
        for card in cards:
            enlace=card.get_attribute('href')
            try:
                procesados.index(enlace)
            except:
                titulo=card.get_attribute('title')
                imagen=card.find_element(By.TAG_NAME, "img").get_attribute('src')
                precio=card.find_element(By.CLASS_NAME, "ItemCard__price").text
                tb.send_message(cf.telegram_userid,f'<b>TITULO:</b> {titulo}\n<b>PRECIO:</b> {precio}\n<b>ENLACE:</b> {enlace}\n\n<b>IMAGEN:</b> {imagen}',parse_mode='HTML')
                procesados.append(enlace)
                haynuevos=True
        if (haynuevos):
            with open('procesados.pkl', 'wb') as fp:
                pickle.dump(procesados, fp)
    except:
        pass

def main():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    while(True):
        driver = webdriver.Chrome(options=options)
        login(driver)
        for enlace in cf.OFFERS:
            procesa_pagina(driver, enlace)
        driver.quit()
        sleep(30)


if __name__ == '__main__':
    main()