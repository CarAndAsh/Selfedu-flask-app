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

    def get_posts(self, sort_by='time'):
        try:
            self.__cur.execute(f'''SELECT * FROM posts ORDER BY {sort_by} DESC''')
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print('Read posts error')
            return []

    def get_post(self, id):
        try:
            self.__cur.execute(f'''SELECT * FROM posts WHERE id == {id} LIMIT 1''')
            res = self.__cur.fetchone()
            if res:
                return res
        except:
            print('Read post error')
            return (False, False)

    def get_cols(self, tab):
        try:
            self.__cur.execute(f'''SELECT * FROM {tab} LIMIT 1''')
            res = self.__cur.fetchone()

            if res:
                print(res.keys())
                return res.keys()
        except:
            print('Get cols error')
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
