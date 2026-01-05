from .Singleton import Singleton
from flask import session
from ..models.user import User
from .CacheManager import CacheManager
from ..error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION, UNAUTHORIZED_EXCEPTION
from ..error_handling.logger import logger
from flask import current_app
import re
import urllib.parse
import random

class AuthManager(metaclass=Singleton):
    def check_if_user_is_logged_in(self, user_id):
        return session.get('user_id') == user_id
    
    def check_if_user_exists(self, user_id):
        cache = CacheManager()
        return cache.get_user(user_id) is not None

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
        
        # Simple hash
        hash_val = 0
        for char in username:
            hash_val = ord(char) + ((hash_val << 5) - hash_val)
        
        color = colors[abs(hash_val) % len(colors)]
        initial = username[0].upper() if username else '?'

        svg = f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
            <rect width="100" height="100" fill="{color}" />
            <text x="50" y="50" dy=".35em" font-size="50" font-family="Arial, sans-serif" font-weight="bold" text-anchor="middle" fill="white">{initial}</text>
        </svg>'''

        return f"data:image/svg+xml;utf8,{urllib.parse.quote(svg)}"

    def register_user(self, username, password, avatar_url=None):
        cache = CacheManager()
        
        # Check if user exists (by username)
        users = cache.cache.get("users") or {}
        for uid, u in users.items():
            if u['username'].lower() == username.lower():
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
        logger.debug(f"User {username} obtained user_id {user_id} and now resides in cache: {user_id in cache.cache.get("users")}")
        
        return user_id, None

    def login(self, username, password):
        cache = CacheManager()
        users = cache.cache.get("users") or {}
        
        found_user = None
        for uid, u in users.items():
            if u['username'].lower() == username.lower():
                found_user = u
                break
        
        if not found_user:
            return None, 'Nieprawidłowa nazwa użytkownika lub hasło'
        
        # Plain text comparison as per simulation
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

    # Deprecated but kept for compatibility during transition if needed, though strictly replacing.
    def create_user(self, username, password, avatar_url = ''):
        # This was the old unsafe method. Mapping to register for safety or just removing.
        # But previous code used it. I should replace usages.
        return self.register_user(username, password, avatar_url)[0]
