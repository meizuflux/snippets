
from functools import wraps
from typing import Callable
from uuid import UUID

from asyncpg import Connection
from sanic import HTTPResponse, Request, json

# TODO: we need to handle getting a connection here, ideally then pass the connection to the request
async def logged_in(conn: Connection, request: Request, *, session: bool = False, api_key: bool = False) -> bool:
    is_authorized = False

    if session:
        passed_session = request.cookies.get("session")
        print(passed_session)
        if passed_session:
            user_id = await conn.fetchval("SELECT user_id FROM sessions WHERE token = $1", UUID(passed_session))
            if user_id:
                is_authorized = True
                request.ctx.user_id = user_id

    if not is_authorized and api_key:
        passed_api_key = request.headers.get("apiKey")
        if passed_api_key:
            is_authorized = await validate_api_key(passed_api_key)

    return is_authorized


def protected(*, session: bool = True, api_key: bool = True):
    """
    Decorator to protect routes by checking for session or API key.

    Args:
        session (bool): Whether to check for a session cookie. Defaults to True.
        api_key (bool): Whether to check for an API key in headers. Defaults to True.

    Returns:
        function: The decorated function that checks authorization.
    """

    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            async with request.app.ctx.db_pool.acquire() as conn:
                is_authorized = await logged_in(conn, request, session=session, api_key=api_key)

            if is_authorized:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return json({"status": "not_authorized"}, 403)
        return decorated_function
    return decorator