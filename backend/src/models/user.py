
class User:
    def __init__(self, _id, _username, _password, _transactions = [], _funds = 0, _avatar_url = ''):
        self.id = _id
        self.username = _username
        self.password = _password
        self.transactions = _transactions
        self.avatar_url = _avatar_url
        self.funds = _funds
    
    def get_obj(self):
        return {
            'user_id': self.id,
            'username': self.username,
            'password': self.password,
            'transactions': self.transactions,
            'funds': self.funds,
            'avatar_url': self.avatar_url
        }
