import datetime


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def get_menu(self):
        try:
            self.__cur.execute('''SELECT * FROM navigation''')
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print('Read error')
            return []

    def add_post(self, title, post):
        try:
            post_time = datetime.datetime.now().timestamp()
            self.__cur.execute('''INSERT INTO posts VALUES (NULL,?,?,?)''', (title, post, post_time))
            self.__db.commit()
        except:
            print('Insertion error')
            return False
        return True
