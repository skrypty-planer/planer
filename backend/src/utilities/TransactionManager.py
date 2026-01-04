from .Singleton import Singleton
from ..models.transaction import Transaction
from datetime import date, datetime
from .CacheManager import CacheManager
from ..error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION

class TransactionManager(metaclass=Singleton):
    
    def create_transation(self, user_id, name, transaction_type, amount, category):
        cache = CacheManager()
        
        try:
            user = self.get_user(user_id)
        except DATA_NOT_FOUND_EXCEPTION as ex:
            raise ex
        transaction_id = len(user["transactions"] + 1)

        transaction = Transaction(transaction_id, name, category, amount, transaction_type, date.today().strftime("%Y-%m-%d"))
        
        cache.add_transaction(user_id, transaction)
        
    def filter_transactions(self, user_id, date_from, date_to, name, category, amount_min, amount_max):
        cache = CacheManager()
        transactions = cache.list_transactions(user_id)

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
            if name is not None and transaction["name"] != name:
                continue
            if category is not None and transaction["category"] != category:
                continue

            filter_result.append(transaction)

        return filter_result
