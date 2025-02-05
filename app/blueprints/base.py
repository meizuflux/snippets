from sanic.response import json
from sanic import Blueprint, HTTPResponse, Request


bp = Blueprint("base", url_prefix="/")

@bp.route("/")
async def index(request: Request) -> HTTPResponse:
    return json({"message": "hello wordl"})