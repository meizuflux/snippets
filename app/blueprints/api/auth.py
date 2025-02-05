from psqlpy import ConnectionPool
from sanic.response import json, HTTPResponse
from sanic.request import Request
from sanic import Blueprint
from argon2 import PasswordHasher
# https://pypi.org/project/argon2-cffi/

ph = PasswordHasher()

async def create_user(pool: ConnectionPool, email: str, password: str):
    hashed_password = ph.hash(password)

    connection = await pool.connection()
    user_id = await connection.fetch_val("""
            INSERT INTO users (email, password)
            VALUES ($1, $2)
            RETURNING id;
        """, [email, hashed_password])

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

@bp.route("/about")
async def about(request: Request) -> HTTPResponse:
    # this is gonna be api_key only?
    # probably need to implement authentication middleware

    return json({
        "username": "etc",
        "email": "etc"
    })

@bp.route("/delete_user")
async def delete_user(request: Request) -> HTTPResponse:
    ...


# again, we want to support both a submission of form data, AND a json api command line call
@bp.route("/update_user")
async def update_user(request: Request) -> HTTPResponse:
    ...

