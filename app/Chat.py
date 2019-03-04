import socketio

class Chat(socketio.AsyncNamespace):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.users = dict()
        self.anonimuses = 0

    async def send_statistic(self):
        common_users = [user for user in list(filter(lambda x:x['role']!="Admin",self.users.values()))]
        admins = [user for user in list(filter(lambda x:x['role']=="Admin",self.users.values()))]
        await self.emit('user_stat', {"users": len(common_users), "slaves": self.anonimuses,"admins":len(admins)}, room="chaters")

    async def on_connect(self, sid, environ):
        self.enter_room(sid, 'chaters')
        self.anonimuses += 1
        await self.send_statistic()

    async def on_login(self,sid, data):
        #TODO: Переделать метод, нельзя коннектится без имени и с ником SERUFIM, Админ должен что-то слать, хз, можно сгенерить токен и его слать
        # Если есть поле name и оно не совпадает с теми что уже есть
        if 'name' in data and data['name'] != "":
            self.users[sid] = {"username":data['name'], "role":"Admin" if 'token' in data.keys() and data['token'] == 'secret' else "Default"}
            self.anonimuses -= 1
            await self.emit('reply', {"name": self.users[sid]["username"], "message": f"Подключился", 'role': self.users[sid]["role"]},
                           room='chaters', namespace='/chat')

            await self.emit('login_success', room=sid, namespace='/chat')
            await self.send_statistic()
        elif 'name' not in data or data['name'] == "":
            await self.emit('login_error', {"message": f"Вы не ввели имя"}, room=sid, namespace='/chat')
        else:
            await self.emit('login_error', {"message": f"Никнейм {data['name']} Уже существует"}, room=sid,
                           namespace='/chat')

    async def on_chat_message(self,sid, data):
        await self.emit('reply', {"name": self.users[sid]["username"], "message": data, "admin": self.users[sid]["role"]=="Admin"}, room='chaters',
                       namespace='/chat')

    async def on_disconnect(self,sid):
        self.leave_room(sid, 'chaters')
        if (sid in self.users):
            await self.emit('reply', {"name": self.users[sid]["username"], "message": "Отключился", "admin": self.users[sid]["role"]},
                           room='chaters', namespace='/chat')
            del self.users[sid]
        else:
            self.anonimuses -= 1
        await self.send_statistic()

    async def on_logout(self,sid):
        del self.users[sid]
        self.anonimuses += 1
        await self.send_statistic()


