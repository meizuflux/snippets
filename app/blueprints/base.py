from casu import Blueprint
import muffin


bp = Blueprint("/")

@bp.route("/", methods="GET")
async def index(request: muffin.Request) -> muffin.Response:
    return muffin.Response("hello world")