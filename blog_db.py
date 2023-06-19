import datetime
import re
import sqlite3

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

    # posts part
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

    def add_post(self, title, url, post):
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
            print('Insertion post error')
            return False
        return True

    # users part

    def add_user(self, user, email, hpswd):
        try:
            self.__cur.execute(f'''SELECT COUNT() AS "count" FROM "users" WHERE email LIKE "{email}"''')
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('user with this email already exists')
                return False

            reg_time = datetime.datetime.now().timestamp()
            self.__cur.execute('''INSERT INTO users VALUES (NULL,?,?,?,NULL,?)''', (user, email, hpswd, reg_time))
            self.__db.commit()
        except:
            print('Insertion user error')
            return False
        return True

    def get_user(self, user_id):
        try:
            self.__cur.execute(f'''SELECT * FROM users WHERE id = {user_id} LIMIT 1''')
            res = self.__cur.fetchone()
            if res:
                return res
            print('No such user in DB')
            return False
        except sqlite3.Error as err:
            print('DB error' + str(err))

    def get_user_by_email(self, email):
        try:
            self.__cur.execute(f'''SELECT * FROM users WHERE email LIKE '{email}' LIMIT 1''')
            res = self.__cur.fetchone()
            if res:
                return res
            print('No user with this email in DB')
            return False
        except sqlite3.Error as err:
            print('DB error' + str(err))

    def update_user_avatar(self, img, user_id):
        if not img:
            return False

        try:
            bin_img = sqlite3.Binary(img)
            self.__cur.execute(f'UPDATE users SET avatar = ? WHERE id = ?', (bin_img, user_id))
            self.__db.commit()
        except sqlite3.Error as err:
            print('Update avatar error in DB' + str(err))
            return False
        return True
