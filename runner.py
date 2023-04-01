from app import app, config


ssl_context = None
if config.APP_SSL_CRT and config.APP_SSL_KEY:
    ssl_context = (config.APP_SSL_CRT, config.APP_SSL_KEY)

app.run(config.APP_HOST, config.APP_PORT, ssl_context=ssl_context)
