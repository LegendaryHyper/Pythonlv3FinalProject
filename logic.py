import sqlite3
from datetime import datetime
from config import DATABASE 
import os
import re

class DatabaseManager:
    def __init__(self, database):
        self.database = database
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users(
                                user_id INTEGER PRIMARY KEY,
                                user_name TEXT)
                                ''')
            conn.execute('''CREATE TABLE IF NOT EXISTS balance_and_items(
                                user_id INTEGER,
                                balance INTEGER,
                                FOREIGN KEY(user_id) REFERENCES users(user_id))
                                ''')
            conn.execute('''CREATE TABLE IF NOT EXISTS shop(
                                item_id INTEGER PRIMARY KEY,
                                item_name TEXT,
                                cost INTEGER)
                                ''')
            conn.commit()
    def add_user(self, user_id, user_name):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute("INSERT INTO users VALUES (?, ?)",(user_id, user_name))
            conn.execute("INSERT INTO balance_and_items (user_id, balance) VALUES (?, ?)",(user_id, 0))
            conn.commit()
    def get_users(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM users')
            return [x[0] for x in cur.fetchall()]
    def set_balance(self, user_id, delta):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT balance FROM balance_and_items WHERE user_id = ?", (user_id,))
            balance = cur.fetchall()[0]
            conn.execute("UPDATE balance_and_items SET balance = ? WHERE user_id = ?", (balance[0] + delta, user_id))
            conn.commit()
    def add_to_shop(self, item_name, item_cost):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM shop")
            item_id = cur.fetchall()[0][0] + 1
            conn.execute("INSERT INTO shop (item_id, item_name, cost) VALUES(?, ?, ?)", (item_id, item_name, item_cost))
            no_space = item_name.replace(" ", "")
            conn.execute(f"ALTER TABLE balance_and_items ADD {no_space} 'INTEGER'")
            conn.execute(f"UPDATE balance_and_items SET {no_space} = 0")
            conn.commit()
    def get_shop(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT item_name, cost FROM shop")
            return cur.fetchall()
    def update_inv(self, user_id, item_name, delta):
        conn = sqlite3.connect(self.database)
        no_space = item_name.replace(" ", "")
        with conn:
            cur = conn.cursor()
            cur.execute(f"SELECT {no_space} FROM balance_and_items WHERE user_id = ?", (user_id,))
            result = cur.fetchone()
            if result is None:
                print(f"No record found for user_id: {user_id}")
                return
            current_count = result[0]
            new_count = current_count + delta
            cur.execute(f"UPDATE balance_and_items SET {no_space} = ? WHERE user_id = ?", (new_count, user_id))
            conn.commit()
    def get_cost(self, item_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT cost FROM shop WHERE item_name = ?", (item_name,))
            return cur.fetchall()[0][0]
    def get_balance(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT balance FROM balance_and_items WHERE user_id = ?", (user_id,))
            return cur.fetchall()[0][0]
if __name__ == '__main__':
    manager = DatabaseManager(DATABASE)
    manager.set_balance()