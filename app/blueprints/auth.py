from secrets import choice
from string import ascii_letters, digits
from argon2 import PasswordHasher
from asyncpg import Connection
from sanic import Blueprint, HTTPResponse, Request, json, redirect
from sanic_ext import render
from ua_parser import user_agent_parser

from app.utils import protected

ph = PasswordHasher()

API_KEY_VALID_CHARS = ascii_letters + digits

def generate_api_key():
    return"".join(choice(API_KEY_VALID_CHARS) for _ in range(128))


bp = Blueprint("auth", url_prefix="/auth")

# TODO: session duration
async def login_user(conn: Connection, request: Request, user_id: int, email: str) -> HTTPResponse:
    metadata = user_agent_parser.Parse(request.headers.getone("User-Agent"))
    browser = metadata["user_agent"]["family"]
    os = metadata["os"]["family"]

    # don't add VALUES before the values, it breaks it
    # I have no idea why but this works
    uuid = await conn.fetchval("""
        INSERT INTO sessions (token, user_id, ip, browser, os)
        (SELECT gen_random_uuid(), $1, $2, $3, $4)
        RETURNING token;
    """, user_id, request.ip, browser, os)

    res = redirect("/")
    res.add_cookie(
        "session",
        str(uuid),
        httponly=True,
        samesite="strict",  # using this lets me not need to setup csrf and whatnot
    )
    res.add_cookie(
        "email",
        email,
        max_age=60 * 60 * 24 * 365,  # one year
        httponly=True,
        samesite="strict",
    )

    return res

@bp.route("/signup", methods=["GET", "POST"])
async def signup(request):
    if request.method == "GET":
        return await render("auth/signup.jinja")
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email is None or password is None:
            return json({"message": "Username and password must be provided"}, 400)
        
        hashed_password = ph.hash(password)

        async with request.app.ctx.db_pool.acquire() as connection:
            user_id = await connection.fetchval("""
            INSERT INTO users (email, password)
            VALUES ($1, $2)
            RETURNING id;
            """, email, hashed_password)

            return await login_user(connection, request, user_id, email)
    
@bp.route("/signin", methods=["GET", "POST"])
async def login(request):
    if request.method == "GET":
        return await render("auth/signin.jinja")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email is None or password is None:
            return json({"message": "Email and password must be provided"}, 400)

        async with request.app.ctx.db_pool.acquire() as connection:
            user = await connection.fetchrow("""
            SELECT id, password
            FROM users
            WHERE email = $1;
            """, email)

            if user is None or not ph.verify(user["password"], password):
                return json({"message": "Invalid email or password"}, 400)

            return await login_user(connection, request, user["id"], email)
    
@bp.route("/settings")
@protected(session=True)
async def settings(request):
    async with request.app.ctx.db_pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT email
            FROM users
            WHERE id = $1;
        """, request.ctx.user_id)

        api_keys = await conn.fetch(
            """
            SELECT title, created
            FROM api_keys
            WHERE user_id = $1
            ORDER BY created DESC
            """,
            request.ctx.user_id
        )

    return await render("auth/settings.jinja", context={"user": user, "api_keys": api_keys})

@bp.route("/create-api-key", methods=["POST"])
@protected(session=True)
async def create_api_key(request):


    title = request.form.get("title")
    if not title:
        return json({"message": "Title is required"}, 400)

    generated_key = generate_api_key()

    async with request.app.ctx.db_pool.acquire() as conn:
        api_key_id = await conn.fetchval(
            """
            INSERT INTO api_keys (user_id, title, key)
            VALUES ($1, $2, $3)
            RETURNING id;
            """,
            request.ctx.user_id,
            title,
            ph.hash(generated_key),
        )

    return await render("auth/view_api_key.jinja", context={
        "api_key": f"{api_key_id}:{generated_key}",
        "title": title,
    })
        
