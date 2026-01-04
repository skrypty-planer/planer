from .Singleton import Singleton
from ..models.user import User
from ..models.transaction import Transaction
from ..error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION
from flask_caching import Cache
from flask import current_app
from datetime import date, datetime

class CacheManager(metaclass=Singleton):
    def __init__(self, cache: Cache):
        super()
        self.cache = cache

    def list_transactions(self, user_id):
        try:
            user = self.get_user(user_id)
        except DATA_NOT_FOUND_EXCEPTION as ex:
            current_app.pending_errors.append(ex)

        return user["transactions"]

    def add_transaction(self, user_id, new_transaction: Transaction):
        try:
            user = self.get_user(user_id)
        except DATA_NOT_FOUND_EXCEPTION as ex:
            current_app.pending_errors.append(ex)

        # Aktualizacja danych użytkownika
        user["transactions"].append(new_transaction)
        user["funds"] += new_transaction["amount"]

        # Zapisanie nowych danych w bazie
        try:
            self.set_user(user_id, user)
        except DATA_NOT_FOUND_EXCEPTION as ex:
            current_app.pending_errors.append(ex)

        return new_transaction["transaction_id"]
    
    def get_number_of_transactions_for_user(self, user_id):
        try:
            user = self.get_user(user_id)
        except DATA_NOT_FOUND_EXCEPTION as ex:
            current_app.pending_errors.append(ex)
        return len(user["transactions"])
        
    def get_user(self, user_id):
        try:
            user = self.cache.get("users")[user_id]
        except DATA_NOT_FOUND_EXCEPTION as ex:
            current_app.pending_errors.append(ex)
        
        return user
    
    def set_user(self, user_id, user: User):
        users = self.cache.get("users")
        
        try:
            user = users[user_id]
        except DATA_NOT_FOUND_EXCEPTION as ex:
            current_app.pending_errors.append(ex)
        
        users[user_id] = user.get_obj()
        
        self.cache.set("users", users)
    
    def get_number_of_users(self):
        return len(self.cache.get('users'))
