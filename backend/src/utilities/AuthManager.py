from .Singleton import Singleton
from flask import session
from ..models.user import User
from .CacheManager import CacheManager
from ..error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION


class AuthManager(metaclass=Singleton):
    def check_if_user_is_logged_in(self, user_id):
        return session[user_id] is not None
    
    def check_if_user_exists(self, user_id):
        cache = CacheManager()
        return cache.get_user(user_id) is not None

    def create_user(self, username, password, avatar_url = ''):
        cache = CacheManager()
        user_id = cache.get_number_of_users() + 1
        user = User(user_id, username, password, avatar_url = avatar_url)
        
        try:
            cache.set_user(user_id, user)
        except DATA_NOT_FOUND_EXCEPTION as ex:
            raise ex
        
        return user_id
