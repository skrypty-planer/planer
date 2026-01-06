from .Singleton import Singleton
from ..models.user import User
from ..models.transaction import Transaction
from ..error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION
from flask_caching import Cache
from flask import current_app
from datetime import date, datetime

class CacheManager(metaclass=Singleton):
    def __init__(self, cache: Cache):
        print("INIT CacheManager", id(self))
        self.cache = cache
        if not self.cache.get("users"):
            self.cache.set("users", {})

    def list_transactions(self, user_id):
        user = self.get_user(user_id)
        if user:
            return user["transactions"]
        return []

    def add_transaction(self, user_id, new_transaction: dict): # Changed to dict to match usage
        user = self.get_user(user_id)
        if not user:
            return None

        # Aktualizacja danych użytkownika
        user["transactions"].append(new_transaction)
        # Assuming funds is balance? Frontend doesn't strictly track 'funds' property separate from calc, but User model has it.
        # Let's keep it simple.
        user["funds"] += new_transaction["amount"] if new_transaction['type'] == 'income' else -new_transaction["amount"]

        # Zapisanie nowych danych w bazie
        self.set_user(user_id, user)

        return new_transaction["id"]
    
    def get_number_of_transactions_for_user(self, user_id):
        user = self.get_user(user_id)
        return len(user["transactions"]) if user else 0
        
    def get_user(self, user_id):
        users = self.cache.get("users")
        print("GET USERS:", self.cache.get("users"))
        if users and user_id in users:
            return users[user_id]
        return None
    
    def set_user(self, user_id, user_data):
        users = self.cache.get("users") or {}
        # User data can be a User object or a dict. Normalize to dict.
        if isinstance(user_data, User):
            users[user_id] = user_data.get_obj()
        else:
            users[user_id] = user_data

        print("SET USER:", self.cache.get("users"))
        
        self.cache.set("users", users)
    
    def get_number_of_users(self):
        users = self.cache.get('users')
        return len(users) if users else 0
