from casu import Blueprint
import muffin


bp = Blueprint("/auth")

@bp.route("/signup", methods=["POST"])
async def login(request: muffin.Request) -> muffin.Response:
    


    return muffin.Response("user created")