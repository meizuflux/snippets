from sanic.response import json
from sanic import Blueprint, HTTPResponse, Request
from sanic_ext import render


bp = Blueprint("base", url_prefix="/")

@bp.route("/")
async def index(request: Request) -> HTTPResponse:
    return await render("index.jinja")