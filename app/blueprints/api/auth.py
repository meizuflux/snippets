from asyncpg import Pool
from sanic.response import json, HTTPResponse
from sanic.request import Request
from sanic import Blueprint
from argon2 import PasswordHasher

from app.utils import protected
# https://pypi.org/project/argon2-cffi/

ph = PasswordHasher()

async def create_user(pool: Pool, email: str, password: str):
    hashed_password = ph.hash(password)

    async with pool.acquire() as connection:
        user_id = await connection.fetchval("""
            INSERT INTO users (email, password)
            VALUES ($1, $2)
            RETURNING id;
        """, email, hashed_password)

    return user_id


bp = Blueprint("api_auth", url_prefix="/auth", version=1)

# TODO: figure out code duplication for form data but also json being sent
# perhaps from a content-type header? 
@bp.route("/signup", methods=["POST"])
async def signup(request: Request) -> HTTPResponse:
    username = request.json.get("username")
    password = request.json.get("password")

    if username is None or password is None:
        return json({"message": "Username and password must be provided"}, 400)

    try:
        user_id = await create_user(request.app.ctx.db_pool, username, password)
    except Exception as e:
        print(e)
        return json({"message": "Failed to create user"}, 400)

    return json({"message": "User created"})

# sample API key: Za-L6ffPDk%j4^RQbcBA-DcG0aVCc0C:uHX~vzB=dP%;B~21D9guelJj0PEU^pb7ojwfQ8GWwHd~lI22CwHzCDZ<@DTysb~HXTh:fUw+CYyh;k5UrH=Gi^jb?U;KKsB&feMEynrfmyWRQp?LN^!g&hIr@!RrUs@lxAw5@lF2wJKH%4>cJLHeFgbOMg9oJ9KhtK&FHI1%MfESYBja>zkQW?;
@bp.route("/about")
@protected(api_key=True)
async def about(request: Request) -> HTTPResponse:
    async with request.app.ctx.db_pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT id, email, joined
            FROM users
            WHERE id = $1;
        """, request.ctx.user_id)

        return json({
            "id": user["id"],
            "email": user["email"],
            "joined": user["joined"].strftime("%Y-%m-%d %H:%M")
        })

@bp.route("/delete_user")
async def delete_user(request: Request) -> HTTPResponse:
    ...


# again, we want to support both a submission of form data, AND a json api command line call
@bp.route("/update_user")
async def update_user(request: Request) -> HTTPResponse:
    ...

