"""API errors."""

from fastapi import Request
from fastapi.responses import JSONResponse

from api.screams import ScreamNotFound


async def scream_not_found_handler(request: Request, exc: ScreamNotFound):
    """Handle ScreamNotFoundError."""
    return JSONResponse(
        status_code=404,
        content={'message': exc.message},
    )


def register_exception_handler(app):
    """Register exception handler for application."""
    app.add_exception_handler(ScreamNotFound, scream_not_found_handler)
