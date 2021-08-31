#!/usr/bin/env python3
# coding: utf-8

import asyncio, pathlib, aiohttp_jinja2, shelve
from aiohttp import web

PROJECT_ROOT = pathlib.Path(__file__).parent

# Отдаём favicon.ico, правильнее отдавать статику web-сервером (Nginx'ом, например)
async def favicon(request):
    return web.FileResponse(str(PROJECT_ROOT / 'static' / 'images' / 'favicon.ico'))

async def index(request):
    logger = request.app['logger']
    data   = await request.post()
    state  = await get_status_from_shelve()
    logger.info(f'Включить сервис (загружено сохранённое состояние): {state}')

    if request.method == 'POST':
        command = data['command']
        if command == 'start':
            data_out, data_err = await daemon_cmd('start')
        elif command == 'restart':
            data_out, data_err = await daemon_cmd('restart')
        elif command == 'stop':
            data_out, data_err = await daemon_cmd('stop')
        logger.info(f'Получена команда на управление демоном: {command}')
    else:
        command = None
    
    context = {'enabled': 'checked' if state=='true' else ''}
    template = 'index.html'
    response = aiohttp_jinja2.render_template(template, request, context)
    response.headers['Content-Language'] = 'ru'
    return response

async def status(request):
    state = await daemon_status()
    response = {'state': state}
    return web.json_response(response, status=200)

async def actions(request):
    logger = request.app['logger']
    data = await request.post()
    enabled = data['enabled']
    await save_status_to_shelve(enabled)
    logger.info(f'Включить сервис (сохранено состояние): {enabled}')
    response = {'enabled': enabled}
    logger.info(f'Включить сервис: {enabled}')
    return web.json_response(response, status=200)

async def daemon_status():
    reply = await asyncio.create_subprocess_shell(
        f'systemctl status sshd',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        )

    stdout, stderr = await reply.communicate()

    answer = str(stdout)
    if 'Active: active (running)' in answer:
        state = 'active'
    elif 'Active: inactive (dead)' in answer:
        state = 'dead'
    else:
        state = 'unknown'

    return state

async def daemon_cmd(cmd):
    reply = await asyncio.create_subprocess_shell(
        f'systemctl {cmd} sshd',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        )

    stdout, stderr = await reply.communicate()
    return stdout, stderr

async def get_status_from_shelve():
    with shelve.open('storage') as stor:
        if 'state' in stor:
            state = stor['state']
        else:
            state = stor['state'] = 'unknown'
    return state

async def save_status_to_shelve(state):
    with shelve.open('storage') as stor:
        stor['state'] = state


