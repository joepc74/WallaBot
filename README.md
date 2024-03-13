# WallaBot
Bot que procesa busquedas de Wallapop y manda un telegram con cada novedad

## Formato del archivo config.py

    telegram_key='<TELEGRAM_API_KEY>'
    telegram_userid='<TELEGRAM_CHAT_ID>'
    espera_entre_ciclos=<SEGUNDOS_DE_ESPERA_ENTRE_CICLOS>
    OFFERS=[
	    {'nombre':'<NOMBRE_BUSQUEDA>','url':'<URL_BUSQUEDA>'},
	    {'nombre':'<NOMBRE_BUSQUEDA>','url':'<URL_BUSQUEDA>'},
	    ...
    ]
