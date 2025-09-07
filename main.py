from contextlib import asynccontextmanager

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import init_db
import requests as rq


# Нам надо такая штука которая будет синхронизировать нашу базу данных для этого нам нужно использовать декоратор asynccontextmanager
@asynccontextmanager
async def lifespan(app_:FastAPI):
    # вызовем функцию init_db для того чтобы бот запустился  
    await init_db()    
    print('Bot is ready')
    '''lifespan(app_: FastAPI) FastAPI умеет вызывать такую функцию при запуске приложения.
    Всё, что до yield — выполняется один раз при старте (например, подключить базу, инициализировать таблицы). Всё, что после yield — выполняется один раз при завершении (например, закрыть соединения, очистить ресурсы).
    await init_db() Здесь запускается инициализация БД и создание таблиц (твоя функция).
    print("Bot is ready") Просто сообщение, что всё готово. yield Место, где приложение «работает». После этого блок кода продолжит выполняться, когда FastAPI будет закрываться.'''
    yield
    
    
# Создадим фастапи приложение, app деген переменный курамыз ол FastAPI класстын объектиси болып табылады. 
# когда мы запускаем приложение мы запускаем и эту функцию lifespan то есть зачем нужна эта функция когда у нас запускается приложение фастапи в том числе срабатывает эта функция то есть мы можем какой то функционал прописать который должен выполнится при запуске приложения 
app = FastAPI(title="To Do App", lifespan=lifespan)

'''
middleware - это специальные какие то инструкции которые должны вызываться до обработки какого то события, 
'''
app.add_middleware(
    # CORSMiddleware - он нужен конечно же в первую очередь для безопасности то есть он контролирует для того чтобы пост запросы пришли к нам не какие то подделки а у нас все было правильно
    CORSMiddleware,
    # allow_origins - это url адреса с которых мы разрешаем чтобы нам приходили запросы 
    allow_origins=['*'],
    # Все снизу нужны для безопасности
    # Говорит: разрешить передавать куки, токены, авторизационные данные при запросах.Например, если у клиента есть JWT в Authorization или cookie-сессия.Без этого браузер не отправит такие данные при cross-origin запросах.
    aloow_credentials=True,
    # методы это могут пост гет методыЭто список HTTP-методов, которые разрешены для запросов.["GET", "POST"] → значит только GET и POST.["*"] → значит все методы (GET, POST, PUT, DELETE, PATCH, и т.д.).
    allow_methods=["*"],
    # headers в пост запросахЭто список HTTP-заголовков, которые можно отправлять с клиента. Например: Content-Type (тип данных) Authorization (токен) X-Custom-Header (свои заголовки) 
    # Если браузер хочет отправить заголовок, которого нет в списке — он заблокирует запрос. ["*"] → значит разрешены все заголовки.
    allow_headers=["*"],
)

# эндпоинты 

# снизу у нас будет гет запрос 
# мы будем ловить tg_id  
@app.get("/api/tasks/{tg_id}")
# а в функции мы тоже будем ловить tg_id который является int
async def tasks(tg_id: int):
    # теперь сделаем запрос и получаем юзера
    user = await rq.add_user(tg_id)
    # и дальше мы должны все таки вернуть tasks 
    return await rq.get_tasks(user.id)

@app.get("/api/main/{tg_id}")
async def profile(tg_id: int):
    user = await rq.add_user(tg_id)
    completed_tasks_count = await rq.get_completed_tasks_count(user.id)
    return {'completedTasks': completed_tasks_count}