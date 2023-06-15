from flask import url_for
from flask_login import UserMixin


class UserLogin(UserMixin):
    def from_db(self, user_id, db):
        self.__user = db.get_user(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_name(self):
        return self.__user['name'] if self.__user else 'Без никнейма'

    def get_email(self):
        return self.__user['email'] if self.__user else 'Без e-mail'

    def get_avatar(self, app):
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='images/default.jpg')) as def_img:
                    img = def_img.read()

            except FileNotFoundError as err:
                print('Не удалось загрузить аватар по умолчанию' + str(err))
        else:
            img = self.__user['avatar']
        return img

    def verify_ext(self, filename):
        image_extentions = ('bmp', 'jpg', 'jpeg', 'png')
        ext = filename.rsplit('.', 1)[1].lower()
        if ext in image_extentions:
            return True
        return False





