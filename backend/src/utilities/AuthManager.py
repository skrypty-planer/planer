from .Singleton import Singleton

class AuthManager(metaclass=Singleton):
    def check_if_user_is_logged_in(self, username):
        pass

    def create_user(self, username, password):
        pass
