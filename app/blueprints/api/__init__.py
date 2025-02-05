from sanic import Blueprint
from . import auth


sub_bps = (
    auth.bp,
)
bp = Blueprint.group(*sub_bps, version_prefix="/api/v")