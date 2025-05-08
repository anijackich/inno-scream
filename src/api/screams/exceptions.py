"""`screams` exceptions."""


class ScreamNotFound(Exception):
    """Scream not found."""

    def __init__(self, message: str = 'Scream not found'):
        """
        Create ScreamNotFound instance.

        Args:
            message (str): Exception message
        """
        self.message = message
        super().__init__(message)
