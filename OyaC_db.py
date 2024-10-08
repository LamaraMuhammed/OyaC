"""
mysql-connector-python --version = 8.0.33
"""
from datetime import date

import mysql.connector


class DB:
    db = mysql.connector.connect(host="127.0.0.1", user="root", password="Lmr977552", database="Oya_Oya_C")
    cursor = db.cursor()
    evt_time = date.today()

    # DB Operation
    def add_new_item(self, evt_time, item_name, theme_measure, roll, half, packet, status):
        statement = "INSERT INTO Oya_Item(event_time, item_name, theme_measure_1, theme_measure_2, theme_measure_3, " \
                    "roll_price, half_roll_price, packet_price, row_status) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(statement, [evt_time, item_name, theme_measure[0], theme_measure[1],
                                        theme_measure[2], roll, half, packet, status])
        self.db.commit()
        self.add_event('c', self.evt_time)

    def retrieve_item(self):
        self.cursor.execute("SELECT * FROM Oya_Item")
        return self.cursor.fetchall()

    def update_item(self, query, val):
        self.cursor.execute(query, val)
        self.db.commit()
        self.add_event('u', self.evt_time)

    def delete_item(self, evt):
        self.cursor.execute("DELETE FROM Oya_Item WHERE event_time = %s", (evt,))
        self.db.commit()
        self.add_event('d', self.evt_time)

    # password insertion    -----------------------------------
    def create_pwd(self, pwd):
        query = "INSERT INTO OyaC_Password(user_password) VALUES(%s)"
        self.cursor.execute(query, [pwd])
        self.db.commit()

    def update_pwd(self, old, new):
        query = "UPDATE OyaC_Password SET user_password = %s WHERE user_password = %s"
        self.cursor.execute(query, [new, old])
        self.db.commit()

    def delete_pwd(self, pwd):
        self.cursor.execute("DELETE FROM OyaC_Password WHERE user_password = %s", (pwd,))
        self.db.commit()
        self.add_event('pwd_d', self.evt_time)

    def check_pwd(self, pwd):
        self.cursor.execute("SELECT user_password FROM OyaC_Password WHERE user_password = %s", (pwd,))
        res = self.cursor.fetchall()
        if res:
            return res[0]

    def get_pwd(self):
        self.cursor.execute("SELECT user_password FROM OyaC_Password WHERE user_password IS NOT NULL")
        res = self.cursor.fetchone()
        if res:
            return res[0]

    def add_event(self, role, event_date, number=None):
        query = None
        if role == 'c':
            query = "INSERT INTO OyaC_Password(user_add, add_date) VALUES(True, %s)"
        elif role == 'r':
            query = "INSERT INTO OyaC_Password(user_recovery_number) VALUES(%s)"
            self.cursor.execute(query, [number])
            self.db.commit()
        elif role == 'u':
            query = "INSERT INTO OyaC_Password(user_edit, edit_date) VALUES(True, %s)"
        elif role == 'd':
            query = "INSERT INTO OyaC_Password(user_delete, delete_date) VALUES(True, %s)"
        elif role == 'pwd_d':
            query = "INSERT INTO OyaC_Password(user_password_deletion, password_deletion_date) VALUES(True, %s)"

        if not number:
            self.cursor.execute(query, [event_date])
            self.db.commit()
