'''
mysql-connector-python --version = 8.0.33
'''

import mysql.connector


class DB:
    db = mysql.connector.connect(host="127.0.0.1", user="root", password="Lmr977552", database="Oya_Oya_C")
    cursor = db.cursor()

    # DB Operation
    def add_new_item(self, evt_time, item_name, theme_measure, roll, half, packet, status):
        statement = "INSERT INTO Oya_Item(event_time, item_name, theme_measure_1, theme_measure_2, theme_measure_3, " \
                    "roll_price, half_roll_price, packet_price, row_status) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(statement, [evt_time, item_name, theme_measure[0], theme_measure[1],
                                        theme_measure[2], roll, half, packet, status])
        self.db.commit()

    def retrieve_item(self):
        self.cursor.execute("SELECT * FROM Oya_Item")
        return self.cursor.fetchall()

    def update_item(self, query, val):
        self.cursor.execute(query, val)
        self.db.commit()

    def delete_item(self, evt):
        self.cursor.execute("DELETE FROM Oya_Item WHERE event_time = %s", (evt,))
        self.db.commit()

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

    def check_pwd(self, pwd):
        self.cursor.execute("SELECT user_password FROM OyaC_Password WHERE user_password = %s", (pwd,))
        res = self.cursor.fetchone()
        if res:
            return res[0]

    def get_pwd(self, q):
        self.cursor.execute("SELECT * FROM OyaC_Password")
        res = self.cursor.fetchall()
        if res:
            if q == 0:
                return res[0][0]
            else:
                return res[0][1]
