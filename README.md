# WallaBot
Bot que procesa busquedas de Wallapop y manda un telegram con cada novedad

## Formato del archivo config.py

    telegram_key='<TELEGRAM_API_KEY>'
    telegram_userid='<TELEGRAM_CHAT_ID>'
    espera_entre_ciclos=<SEGUNDOS_DE_ESPERA_ENTRE_CICLOS>
    OFFERS=[
        {
            'product_name':'<NOMBRE_BUSQUEDA>',
            'min_price':<PRECIO_MINIMO>,
            'max_price':<PRECIO_MAXIMO>,
            'keywords':['<KEYWORD1>','<KEYWORD2>'],
            'excluded_keywords':['<KEYWORD_EXCLUDED1>','<KEYWORD_EXCLUDED2>'],
        },
        {
            'product_name':'<NOMBRE_BUSQUEDA>',
            'min_price':<PRECIO_MINIMO>,
            'max_price':<PRECIO_MAXIMO>,
            'keywords':['<KEYWORD1>','<KEYWORD2>'],
            'excluded_keywords':['<KEYWORD_EXCLUDED1>','<KEYWORD_EXCLUDED2>'],
        },
	    ...
    ]
