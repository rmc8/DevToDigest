import os
import sqlite3


class DataBase:
    def __init__(self, dir_path: str):
        self.db_path = os.path.join(dir_path, "database.db")
        self.conn = None
        if not os.path.exists(self.db_path):
            self._create_table()
        else:
            self.connect()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)

    def _create_table(self):
        self.connect()
        cursor = self.conn.cursor()
        query = """
            CREATE TABLE IF NOT EXISTS data
            (id INTEGER PRIMARY KEY, url TEXT UNIQUE, en_title TEXT, ja_title TEXT, translated_text TEXT)
        """
        cursor.execute(query)
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()

    def insert_data(self, url: str, en_title: str, ja_title: str, translated_text: str):
        cursor = self.conn.cursor()
        query = """
            INSERT OR IGNORE INTO data (url, en_title, ja_title, translated_text)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (url, en_title, ja_title, translated_text))
        self.conn.commit()

    def get_all_data(self):
        cursor = self.conn.cursor()
        query = "SELECT * FROM data"
        cursor.execute(query)
        return cursor.fetchall()

    def url_exists(self, url: str) -> bool:
        cursor = self.conn.cursor()
        query = "SELECT 1 FROM data WHERE url = ? LIMIT 1"
        cursor.execute(query, (url,))
        return cursor.fetchone() is not None

    def __del__(self):
        self.close()
