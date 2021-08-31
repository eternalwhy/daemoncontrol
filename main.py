#!/usr/bin/env python3
# coding: utf-8

import asyncio
import jinja2
import aiohttp_jinja2

import logging, logging.config

from aiohttp import web
from routes import setup_routes

from logging.handlers import SysLogHandler


LOG_PATH = 'main.log' 

logging.basicConfig(
    filename=LOG_PATH, 
    format = '%(levelname)-10s %(asctime)s %(module)s, %(funcName)s, : %(message)s',
    level=logging.INFO)
    # level=logging.DEBUG)
logger = logging.getLogger('asyncio')

formatter = logging.Formatter('%(levelname)-10s %(asctime)s %(module)s, %(funcName)s, : %(message)s')
syslog_handler = SysLogHandler(address='/dev/log')
syslog_handler.setFormatter(formatter)
logger.addHandler(syslog_handler)


def init():
    app = web.Application()
    app['logger'] = logger
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
    setup_routes(app)

    return app

def main():
    loop = asyncio.get_event_loop()
    app = init()
    web.run_app(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    try:
        logger.info('Приложение запущено')
        main()
    
    except Exception as err:
        logger.exception(err)

    finally:
        logger.info('Приложение завершается')

