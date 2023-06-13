import datetime
import re

from flask import url_for


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

    def get_post(self, alias):
        try:
            self.__cur.execute(f'''SELECT * FROM posts WHERE url LIKE '{alias}' LIMIT 1''')
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

    def add_post(self, title, post, url):
        try:
            self.__cur.execute(f'''SELECT COUNT() AS "count" FROM "posts" WHERE url LIKE "{url}"''')
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('post with this url already exists')
                return False

            base = url_for('static', filename='blog_posts')
            ptrn = r'(?P<tag><img\s+[^>]*src=)(?P<quote>["\'])(?P<url>.+?)(?P=quote)>'
            text = '\\g<tag>' + base + '/\\g<url>>'
            post_fmtd = re.sub(ptrn, text, post)

            post_time = datetime.datetime.now().timestamp()
            self.__cur.execute('''INSERT INTO posts VALUES (NULL,?,?,?,?)''', (title, post_fmtd, post_time, url))
            self.__db.commit()
        except:
            print('Insertion error')
            return False
        return True
