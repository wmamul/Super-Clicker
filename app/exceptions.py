class DatabaseError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
    
    def __str__(self):
        if self.message:
            return f'Database error: {self.message}'
        else: 
            return 'Database error.'

class AuthError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
            
    def __str__(self):
        if self.message:
            return f'Authenitcation or authorization error: {self.message}'
        else:
            return 'Authentication or authorization error.'

class SessionError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f'Session error: {self.message}'
        else:
            return 'Session error.'
