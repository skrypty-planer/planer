from .Singleton import Singleton
from ..models.user import User
from ..models.transaction import Transaction
from flask_caching import Cache
from datetime import date, datetime

class CacheManager(metaclass=Singleton):
    def __init__(self, cache: Cache):
        super()
        self.cache = cache

    def list_transactions(self, user_id):
        user = self.get_user(user_id)
        return user["transactions"]

    def add_transaction(self, user_id, new_transaction: Transaction):
        user = self.get_user(user_id)

        # Aktualizacja danych użytkownika
        user["transactions"].append(new_transaction)
        user["funds"] += new_transaction["amount"]

        # Zapisanie nowych danych w bazie
        self.set_user(user_id, user)

        return new_transaction["transaction_id"]
    
    def get_number_of_transactions_for_user(self, user_id):
        return len(self.get_user(user_id)["transactions"])
    
    def get_user_by_id(self, user_id):
        return self.cache.get("users")[user_id]
    
    def set_user(self, user_id, user: User):
        users = self.cache.get("users")
        users[user_id] = user.get_obj()
        self.cache.set("users", users)
    
    def get_number_of_users(self):
        return len(self.cache.get('users'))
