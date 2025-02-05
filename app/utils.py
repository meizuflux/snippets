
from functools import wraps
from typing import Callable

from sanic import HTTPResponse, Request, json


async def logged_in(request, *, session: bool = False, api_key: bool = False) -> bool:
    is_authorized = False

    if session:
        passed_session = request.cookies.get("session")
        if passed_session:
            is_authorized = await validate_session(passed_session)

    if not is_authorized and api_key:
        passed_api_key = request.headers.get("apiKey")
        if passed_api_key:
            is_authorized = await validate_api_key(passed_api_key)

    return is_authorized


def protected(*, session: bool = True, api_key: bool = True) -> Callable[[Callable], Callable[[Request, any, any], HTTPResponse]]:
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
            is_authorized = await logged_in(request, session=session, api_key=api_key)

            if is_authorized:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return json({"status": "not_authorized"}, 403)
        return decorated_function
    return decorator