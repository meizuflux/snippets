from casu import Application

from app.blueprints import base



def app_factory():
    app = Application()
    
    blueprints = (
        base,
    )

    for blueprint in blueprints:
        app.add_blueprint(blueprint.bp)

    for route in app.router.routes():
        print(f"Path: {route.path}, Methods: {route.methods}")

    return app