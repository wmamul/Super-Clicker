class AuthError(Exception):
    
    def message(self):
        return { 'message': self.args[0] }

class SessionError(Exception):

    def message(self):
        return { 'message': self.args[0] }
