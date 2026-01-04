
class Transaction:
    def __init__(self, _id, _name, _category, _amount, _transaction_type, _date):
        self.id = _id
        self.name = _name
        self.category = _category
        self.amount = _amount
        self.transaction_type = _transaction_type
        self.date = _date
    
    def get_obj(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "amount": self.amount,
            "type": self.transaction_type,
            "date": self.date
        }