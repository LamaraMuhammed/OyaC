import threading
import sqlite3
import uuid


class DB:
    conn = sqlite3.connect('OyaC.db')
    cur = conn.cursor()
    start_process = bool(True)

    def check_table_existence(self):
        tbl = self.cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        if tbl:
            for v in tbl:
                if 'OyaC' in v:
                    return True
                else:
                    self.start_process = False
        else:
            self.start_process = False

    def create_item_tables(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS OyaC (
        item_id PRIMARY KEY, item_name, theme_measure_1, theme_measure_2, theme_measure_3,\
        roll_price, half_price, packet_price, row_status)
        """)
        self.conn.commit()
        self.create_pwd_table()

    def auto_insertion(self, step):
        self.insert_items([
            self.generate_id(), 'Product', 'Carton', 'Half', 'Packet', '10,000', '5,000', '1,000', '#'
        ])

        if step == 0:
            self.start_process = True

    def insert_items(self, arg):
        self.cur.execute("INSERT INTO OyaC VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", arg)
        self.conn.commit()

    def get_items(self):
        if self.start_process:
            data = self.cur.execute("SELECT * FROM OyaC").fetchall()
            if data:
                return data

    def update_item(self, query, val):
        self.cur.execute(query, val)
        self.conn.commit()

    def delete_item(self, item_id):
        self.cur.execute("DELETE FROM OyaC WHERE item_id == ?", [item_id, ])
        self.conn.commit()

    # Password
    def create_pwd_table(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS OyaC_Password(user_password)")
        self.conn.commit()

    def create_pwd(self, pwd):
        self.cur.execute("INSERT INTO OyaC_Password VALUES(?)", [pwd, ])
        self.conn.commit()

    def update_pwd(self, old, new):
        self.cur.execute("UPDATE OyaC_Password SET user_password == ? WHERE user_password == ?", [new, old])
        self.conn.commit()

    def get_pwd(self):
        pwd = self.cur.execute("SELECT user_password FROM OyaC_Password WHERE user_password IS NOT NULL").fetchall()
        if pwd:
            return pwd[0]

    def check_pwd(self, pwd):
        pwd = self.cur.execute(
            "SELECT user_password FROM OyaC_Password WHERE user_password == ?",
            [pwd, ]).fetchall()
        if pwd:
            return pwd[0]

    def delete_pwd(self, pwd):
        self.cur.execute("DELETE FROM OyaC_Password WHERE user_password == ?", [pwd, ])
        self.conn.commit()

    @staticmethod
    def generate_id():
        return str(uuid.uuid4())[:13]
