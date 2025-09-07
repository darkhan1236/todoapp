# Нам нужно первую очередь найти пользователя который у нас должен пользоваться этим ботом для того чтобы найти этого пользователя мы должны сделать запрос в базу данных
# Поэтому и надо этот файл

from sqlalchemy import select, update, delete, func
from models import async_session, User, Task
from pydantic import BaseModel, ConfigDict
from typing import List


'''Теперь нам надо взять tasks из базы данных. Для того чтобы вернуть таски на фронтенд нам нужно использовать сериализацию данных. Дело в том что жаваскрипт принимает в себя данные только в виде json формата и поэтому
наш питоновский объект должны преобразовать в этот json формат которыый понимает жаваскрипт. и для этого мы должны использовать pydantic. '''
class TaskSchema(BaseModel):
    id: int
    title: str 
    completed: bool
    user: int
    
    # model_config нужен для того чтобы сериализация работала корректно. Вот это вот TaskSchema на 100% соответсвует тому что написано в моделях  
    # Без from_attributes=True → Pydantic понимает только JSON/словари. С from_attributes=True → Pydantic понимает ещё и обычные объекты (например, SQLAlchemy-модели).
    model_config = ConfigDict(from_attributies=True)
    

# мы должны достать пользователя если его нет то должны создать его.
async def add_user(tg_id):
    # используя асинхронную сессию мы должны сделать определенный запрос 
    async with async_session() as session:
        # во первых найти этого юзера, мы с помощью scalar делаем select(User) где tg_id юзера равен на айди который мы сюда передали
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        # если юзер есть тогда мы его возвращаем, но бывает и иные случаи 
        if user:
            return user
        # создадим нового пользователя если юзер не нашелся
        new_user = user(tg_id=tg_id)
        # с помощью сессии нам нужно добавить этого пользователя в базу данных
        session.add(new_user)
        # далее изменение нам нужно сохранить
        await session.commit()
        # далее нам нужно этого пользователя вернуть поэтому мы должны сделать refresh
        await session.refresh(new_user)
        # и потом его надо вернуть в функцию
        return new_user
    
    
# теперь напишем ту самую функцию для get_task 
async def get_tasks(user_id):
    async with async_session() as session:
        tasks = await session.scalars(select(Task).where(Task.user == user_id, Task.completed == False))
        
        # теперь надо сделать сериализацию из питонского типа преобразовать в тот который мы можем передать по json и при этом чтобы жаваскрипт его понимал 
        # теперь в этой переменной будут храниться данные которые мы можем передать на фронтенд и он его поймет 
        serialized_tasks = [
            TaskSchema.model_validate(t).model_dump() for t in tasks 
        ]
        # TaskSchema.model_validate(t) Берёт объект t (например, SQLAlchemy-модель Task) Проверяет его поля и типы по Pydantic-схеме TaskSchema. Возвращает Pydantic-объект (TaskSchema). model_dump() Превращает Pydantic-объект в обычный Python-словарь (dict).
        
        return serialized_tasks
    
    
async def get_completed_tasks_count(user_id):
    async with async_session() as session:
        # посчитаем сколько у нас айдишек, и дальше пропишем where те таски которые выполнены
        return await session.scalars(select(func.count(Task.id)).where(Task.completed == True))
    