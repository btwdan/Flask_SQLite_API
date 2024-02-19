import sqlite3
import aiohttp
import math
import os
from flask import Flask, request, jsonify
from req_for_bd import *

# Инициализируем наш сервер
app = Flask(__name__)

class Users:
    def __init__(self, path: str) -> None:
        '''
        Метод который инициализирует наш класс и выполняет подключение к нашей базе данных
        '''
        self.conn = sqlite3.connect(path)
        self.crs = self.conn.cursor()

    def add_user(self, username: str, balance: int) -> None:
        '''
        Метод который добавляет нового пользователя в базу данных
        '''
        self.crs.execute('INSERT INTO users(username, balance) VALUES(?, ?)', (username, balance))
        self.conn.commit()

    def del_user(self, user_id: int) -> None:
        '''
        Метод который удаляет пользователя по его id
        '''
        self.crs.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.conn.commit()
        
    def refresh_balance(self, user_id: int, new_balance: int) -> None:
        '''
        Метод который обновляет баланс пользователя
        '''
        self.crs.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
        self.conn.commit()
    
    def get_balance(self, user_id: int) -> int:
        '''
        Метод который возвращает актуальный баланс пользователя по его id
        '''
        self.crs.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
        row = self.crs.fetchone()
        return row[0] if row else None

    def __del__(self) -> None:
        '''
        Метод который вызывается сборщиком мусора для закрытия работы с бд
        '''
        self.conn.close()


async def fetch_weather(city: str) -> int:
    # Создаем запрос, который получает актуальную темпиратуру в нужном нам городе
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                # Проверяем успешно ли обработан наш запрос сервером
                if response.status == 200:
                    temperature = data['main']['temp']
                    return math.ceil(temperature)
                # Возвращаем ошибку которую нам отправил сервер
                else:
                    print(f"Failed: {data.get('message')}")
                    return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

@app.route('/')
async def start():
    return "Hello it's my test task for job)"

@app.route('/update_bal_by_city/<user_id>/<city>', methods=['POST'])
async def update_balance(user_id: int, city: str):
    user = Users('test.db')

    if not user_id: return jsonify({'Error': 'Missing userId'}), 400

    # Получение температуры воздуха в указанном городе
    temperature = await fetch_weather(city)
    # Проверяем корректность полученых данных
    if temperature is None:
        return jsonify({'Error': 'Failed to fetch weather data'}), 500

    # Обновление баланса пользователя на основе температуры
    try:

        # Получаем текущий баланс пользователя
        current_balance = user.get_balance(user_id)
        # Проверяем корректность полученых данных
        if current_balance is None:
            return jsonify({'Error': 'Failed to get user balance'}), 500

        # Обновляем баланс пользователя
        new_balance = current_balance + temperature  # Добавляем температуру к текущему балансу
        # Проверяем на положительность результата
        if new_balance < 0: 
            return jsonify({'Message': f"User balance can't be updated beacase balance can't be less than 0"}), 200
        # Обращаемся к классу и и обновляем баланс пользователя
        user.refresh_balance(user_id, new_balance)

        return jsonify({'Message': f'User balance updated'}), 200

    except Exception as e:
        return jsonify({'Error': str(e)}), 500

if __name__ == "__main__":
    name_db = 'test.db'
    if not os.path.exists(name_db):
        conn = sqlite3.connect(name_db)
        crs = conn.cursor()
        crs.execute(create_table_user)
        crs.execute(insert_data)
        conn.commit()
        conn.close() 
    
    app.run(debug=True)