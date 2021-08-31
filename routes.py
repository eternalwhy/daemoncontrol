#!/usr/bin/env python3
# coding: utf-8

import pathlib, re
from views import index, actions, favicon, status


PROJECT_ROOT = pathlib.Path(__file__).parent

def setup_routes(app):
    app.router.add_get('/favicon.ico', favicon)
    app.router.add_static('/static/', path=str(PROJECT_ROOT / 'static'), name='static')

    app.router.add_get('/', index, name='index')
    app.router.add_post('/', index, name='index')
    app.router.add_post('/actions', actions)
    app.router.add_post('/status', status)
    
