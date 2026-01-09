from .Singleton import Singleton
from flask import session, current_app
from ..models.user import User
from .CacheManager import CacheManager
from ..error_handling.logger import logger
import re
import urllib.parse
import random

class AuthManager(metaclass=Singleton):
    def check_if_user_is_logged_in(self, user_id):
        return session.get('user_id') == user_id
    
    def check_if_user_exists(self, user_id = None, username = None):
        cache = CacheManager()
        if user_id:
            return cache.get_user(user_id) is not None
        elif username:
            return cache.get_user_by_username(username) is not None
        else:
            return False

    def validate_password(self, password):
        if len(password) < 8:
            return False, 'Hasło musi mieć co najmniej 8 znaków'
        if not re.search(r'[A-Z]', password):
            return False, 'Hasło musi zawierać co najmniej jedną dużą literę'
        if not re.search(r'[0-9]', password):
            return False, 'Hasło musi zawierać co najmniej jedną cyfrę'
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, 'Hasło musi zawierać co najmniej jeden znak specjalny'
        return True, None

    def generate_avatar(self, username):
        colors = [
            '#F44336', '#E91E63', '#9C27B0', '#673AB7', '#3F51B5',
            '#2196F3', '#03A9F4', '#00BCD4', '#009688', '#4CAF50',
            '#8BC34A', '#CDDC39', '#FFC107', '#FF9800', '#FF5722'
        ]
        
        color = colors[random.randint(0, len(colors) - 1)]
        initial = username[0].upper() if username else '?'

        svg = f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
            <rect width="100" height="100" fill="{color}" />
            <text x="50" y="50" dy=".35em" font-size="50" font-family="Arial, sans-serif" font-weight="bold" text-anchor="middle" fill="white">{initial}</text>
        </svg>'''

        return f"data:image/svg+xml;utf8,{urllib.parse.quote(svg)}"

    def register_user(self, username, password, avatar_url=None):
        cache = CacheManager()
        
        if cache.get_user_by_username(username):
            return None, 'Użytkownik o tej nazwie już istnieje'

        valid, error = self.validate_password(password)
        if not valid:
            return None, error

        user_id = f"user-{str(random.randint(100000, 999999))}"
        final_avatar_url = avatar_url if avatar_url else self.generate_avatar(username)

        # Create user
        # User constructor: _id, _username, _password, _transactions=[], _funds=0, _avatar_url=''
        user = User(user_id, username, password, _avatar_url=final_avatar_url)
        
        cache.set_user(user_id, user)
        in_cache = user_id in cache.cache.get("users")
        logger.debug(f"User {username} obtained user_id {user_id} and now resides in cache: {in_cache}")
        
        return user_id, None

    def login(self, username, password):
        cache = CacheManager()
        users = cache.cache.get("users") or {}
        
        found_user = cache.get_user_by_username(username)
        
        if not found_user:
            return None, 'Nieprawidłowa nazwa użytkownika lub hasło'
        
        if found_user['password'] != password:
            return None, 'Nieprawidłowa nazwa użytkownika lub hasło'
            
        return found_user['user_id'], None

    def login_guest(self):
        guest_id = 'guest-user'
        cache = CacheManager()
        user = cache.get_user(guest_id)
        
        if not user:
            # Create guest
            avatar = self.generate_avatar('Gość')
            new_guest = User(guest_id, 'Gość', '', _avatar_url=avatar)
            cache.set_user(guest_id, new_guest)
        
        return guest_id

    def update_profile(self, user_id, username=None, password=None, avatar_url=None):
        cache = CacheManager()
        user = cache.get_user(user_id)
        
        if not user:
            return False, 'Użytkownik nie znaleziony'

        users = cache.cache.get("users") or {}

        if username and username != user['username']:
            # Check for duplicates
            for uid, u in users.items():
                if uid != user_id and u['username'].lower() == username.lower():
                    return False, 'Nazwa użytkownika jest już zajęta'
            user['username'] = username
            
            # Regenerate avatar if auto-generated
            if not avatar_url and 'data:image/svg+xml' in user['avatar_url']:
                user['avatar_url'] = self.generate_avatar(username)

        if password:
            valid, error = self.validate_password(password)
            if not valid:
                return False, error
            user['password'] = password

        if avatar_url:
            user['avatar_url'] = avatar_url

        cache.set_user(user_id, user)
        return True, None
