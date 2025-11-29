from flask_caching import Cache
from datetime import date, datetime


class TransactionsService:
    def __init__(self, cache: Cache):
        self.cache = cache

    def list_transactions(self, user_id):
        user = None  # TODO GET USER DATA
        return user["transactions"]

    def filter_transactions(self, user_id, date_from, date_to, category, description, amount_min, amount_max):
        user = None  # TODO GET USER DATA
        transactions = user["transactions"]

        if date_from is not None:
            from_date = datetime.strptime(date_from, "%Y-%m-%d").date()
        else:
            from_date = None

        if date_to is not None:
            to_date = datetime.strptime(date_to, "%Y-%m-%d").date()
        else:
            to_date = None

        filter_result = []

        for transaction in transactions:
            transaction_date = datetime.strptime(transaction["date"], "%Y-%m-%d").date()

            if from_date is not None and transaction_date < from_date:
                continue
            if to_date is not None and transaction_date > to_date:
                continue
            if amount_min is not None and transaction["amount"] < amount_min:
                continue
            if amount_max is not None and transaction["amount"] > amount_max:
                continue
            if category is not None and transaction["category"] != category:
                continue
            if (description is not None
                    and description not in transaction["description"]
                    and description.lower() not in transaction["description"]):
                continue

            filter_result.append(transaction)

        return filter_result

    def add_transaction(self, user_id, category, amount, description):
        user = None  # TODO GET USER DATA
        transaction_id = len(user["transactions"] + 1)

        new_transaction = {
            "id": transaction_id,
            "category": category,
            "amount": amount,
            "description": description,
            "date": date.today().strftime("%Y-%m-%d")
        }

        # Aktualizacja danych użytkownika
        user["transactions"].append(new_transaction)
        user["funds"] += amount

        # Zapisanie nowych danych w bazie
        users = self.cache.get("users")
        users[user_id] = user
        self.cache.set("users", users)

        return new_transaction
