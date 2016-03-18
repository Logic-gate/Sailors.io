from werkzeug.security import check_password_hash
from pymongo import MongoClient
from hashlib import md5
import os


class User():

    def __init__(self, username):
        DB_NAME = 'sailors'
        DATABASE = MongoClient(os.environ['OPENSHIFT_MONGODB_DB_URL'])[DB_NAME]
        POSTS_COLLECTION = DATABASE.posts
        USERS_COLLECTION = DATABASE.users
        self.username = username
        self.bio = USERS_COLLECTION.find_one({'_id': username})['bio']
        self.email = USERS_COLLECTION.find_one({'_id':username})['email']

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def get_bio(self):
        return self.bio

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)




        