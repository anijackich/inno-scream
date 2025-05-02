class ScreamNotFound(Exception):
    def __init__(self, message: str = 'Scream not found'):
        self.message = message
        super().__init__(message)
