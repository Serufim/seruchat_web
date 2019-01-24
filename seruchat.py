import socketio
from urllib.parse import parse_qs
from aiohttp import web

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

users = dict()

@sio.on('connect', namespace='/chat')
async def connect(sid, data):
    query = parse_qs(data['QUERY_STRING'])
    name = query['name']
    sio.enter_room(sid, 'chaters', namespace='/chat')
    users[sid]=name
    await sio.emit('reply', {"name": users[sid], "message": "Подключился"}, room='chaters', namespace='/chat')


@sio.on('chat message', namespace='/chat')
async def message(sid, data):
    await sio.emit('reply', {"name": users[sid], "message": data}, room='chaters', namespace='/chat', skip_sid=sid)


@sio.on('disconnect', namespace='/chat')
async def disconnect(sid):
    await sio.emit('reply', {"name": users[sid], "message": "Отключился"}, room='chaters', namespace='/chat')


if __name__ == '__main__':
    web.run_app(app, host='localhost',port=3000)