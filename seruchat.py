import socketio
import os
import aiohttp_cors
from aiohttp import web
from dotenv import load_dotenv
load_dotenv()

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

users = dict()
slaves_count = 0

async def check_connection(request):
    return web.json_response({"power":True})

@sio.on('connect', namespace='/chat')
async def connect(sid, data):
    global slaves_count
    sio.enter_room(sid, 'chaters', namespace='/chat')
    slaves_count +=1
    await sio.emit('user_stat', {"users": len(users), "slaves": slaves_count}, room="chaters", namespace='/chat')

@sio.on('login', namespace='/chat')
async def login(sid,data):
    global slaves_count
    print(data)
    #Если есть поле name и оно не совпадает с теми что уже есть
    if 'name' in data and data['name'] not in users.values() and data['name'] != "":
        users[sid] = [data['name'],True if 'token' in data.keys() and data['token']=='secret' else False]
        slaves_count-=1
        await sio.emit('reply',{"name":users[sid][0],"message":f"Подключился",'admin':users[sid][1]},room='chaters',namespace='/chat')
        await sio.emit('login_success',room=sid,namespace='/chat')
        await sio.emit('user_stat', {"users": len(users), "slaves": slaves_count}, namespace='/chat')
    elif 'name' not in data or data['name'] =="":
        await sio.emit('login_error',{"message":f"Вы не ввели имя"},room=sid,namespace='/chat')
    else:
        await sio.emit('login_error',{"message":f"Никнейм {data['name']} Уже существует"},room=sid,namespace='/chat')

@sio.on('chat_message', namespace='/chat')
async def message(sid, data):
    await sio.emit('reply', {"name": users[sid][0], "message": data, "admin":users[sid][1]}, room='chaters', namespace='/chat')


@sio.on('disconnect', namespace='/chat')
async def disconnect(sid):
    global slaves_count
    sio.leave_room(sid,'chaters')
    if(sid in users):
        await sio.emit('reply', {"name": users[sid][0], "message": "Отключился", "admin":users[sid][1]}, room='chaters', namespace='/chat')
        del users[sid]
    else:
        slaves_count -=1    
    await sio.emit('user_stat',{"users":len(users),"slaves":slaves_count})


# Configure default CORS settings.
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
})

# Configure CORS on all routes.
cors.add(app.router.add_get('/check',check_connection));

if __name__ == '__main__':
    web.run_app(app, host=os.getenv("HOST"),port=os.getenv("PORT"))