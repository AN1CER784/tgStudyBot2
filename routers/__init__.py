from routers.user import get_user_router
from routers.curator import get_curator_router
from routers.admin import get_admin_router


__all__ = [
    "get_user_router",
    "get_curator_router",
    "get_admin_router"
]
