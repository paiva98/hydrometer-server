# database.py
import sqlite3
from datetime import datetime, timedelta
import random
from faker import Faker

class BancoDeDados:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connect()
        self.create_table()

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def create_table(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hydrometers (
                id INTEGER PRIMARY KEY, 
                code TEXT NOT NULL UNIQUE,
                name TEXT       
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY, 
                value TEXT NOT NULL, 
                date TEXT NOT NULL, 
                hydrometer_id INTEGER,
                FOREIGN KEY(hydrometer_id) REFERENCES hydrometers(id)
            )
        ''')
        conn.commit()
        conn.close()

    def insert(self, code, value, name=None, date=None):

        print("aaaaaaaaaaaaaa", code, value, name, date)

        if date is None:
            date = datetime.now()
            date = date.strftime('%Y-%m-%d')

        if name is None:
            name = "Nao definido"

        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO hydrometers(code, name) VALUES(?, ?)', (code, name))
        cursor.execute('SELECT id FROM hydrometers WHERE code = ?', (code,))

        hydrometer_id = cursor.fetchone()[0]

        cursor.execute(
            'INSERT INTO predictions(value, date, hydrometer_id) VALUES(?, ?, ?)', 
            (value, date, hydrometer_id)
        )

        conn.commit()
        conn.close()

    def search_recent(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT predictions.*, hydrometers.code, hydrometers.name
            FROM predictions
            INNER JOIN hydrometers ON predictions.hydrometer_id = hydrometers.id
            ORDER BY date DESC
            LIMIT 10
        ''')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_hydrometers_with_predictions(self, days):
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT h.id, h.code, h.name, p.value, p.date
            FROM hydrometers h
            JOIN predictions p ON h.id = p.hydrometer_id
            WHERE p.date >= date('now', '-{} day')
            ORDER BY p.date
        '''.format(days))

        results = cursor.fetchall()
        conn.close()
        return results
    
    def config_database(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        conn.commit()
        conn.close()

    
    def populate_database(self, num_hidrometros, num_predicoes):
        fake = Faker()
        for _ in range(num_hidrometros):
            code = str(random.randint(1000, 99999))  # gera um código de hidrômetro aleatório
            name = fake.name()  # gera um nome aleatório

            for _ in range(num_predicoes):
                value = str(random.randint(1000000, 9999999))  # gera um valor de previsão aleatório
                date = datetime.now() - timedelta(days=random.randint(0, 365))  # gera uma data aleatória no último ano
                date = date.strftime('%Y-%m-%d')
                self.insert(code, value, name, date)


