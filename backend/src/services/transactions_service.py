from flask_caching import Cache


class TransactionsService:
    def __init__(self, cache: Cache):
        self.cache = cache

    def list_transactions(self, user_id):
        user = None  # TODO GET USER
        return user["transactions"]

    def add_transaction(self, user_id, category, amount, description):
        user = None  # TODO GET USER
        transaction_id = len(user["transactions"] + 1)

        new_transaction = {
            "id": transaction_id,
            "category": category,
            "amount": amount,
            "description": description
        }

        # Aktualizacja danych użytkownika
        user["transactions"].append(new_transaction)
        user["funds"] += amount

        # Zapisanie nowych danych w bazie
        users = self.cache.get("users")
        users[user_id] = user
        self.cache.set("users", users)

        return new_transaction
