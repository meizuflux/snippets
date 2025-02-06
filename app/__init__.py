import asyncpg
from sanic import Sanic

from app.blueprints import base, auth, api


async def before_request(request):
    #request.ctx.user = await fetch_user_by_token(request.token)
    ...

async def before_startup(app):
    app.ctx.db_pool = await asyncpg.create_pool(
        dsn="postgres://postgres:test@localhost:5432/snippets",
    )

async def after_shutdown(app):
    await app.ctx.db_pool.close()

def app_factory():
    app = Sanic(__name__)

    # TODO: change this to not such a crappy templating thingy
    app.config.TEMPLATING_ENABLE_ASYNC = True

    app.before_server_start(before_startup)
    app.after_server_stop(after_shutdown)

    app.on_request(before_request)

    
    blueprints = (
        base,
        auth,
        api,
    )

    for blueprint in blueprints:
        app.blueprint(blueprint.bp)


    return app