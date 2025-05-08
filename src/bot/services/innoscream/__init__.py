"""A simple abstraction over API for easier use."""

from .client import InnoScreamAPI
from .models import Scream

__all__ = ['InnoScreamAPI', 'Scream']
