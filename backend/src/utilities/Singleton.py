class Singleton(type):
    instance = None
    
    def __call__(self, *args):
        if self.instance is None:
            self.instance = super(Singleton, self).__call__(*args)
        return self.instance
