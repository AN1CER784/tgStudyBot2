from aiogram import Router

from routers.admin.access_router import router as access_router
from routers.admin.menu_router import router as menu_router
from routers.admin.roles_router import router as roles_router
from routers.admin.profiles_router import router as profiles_router


def get_admin_router() -> Router:
    router = Router(name="admin_root")
    router.include_router(menu_router)
    router.include_router(access_router)
    router.include_router(roles_router)
    router.include_router(profiles_router)
    return router


__all__ = ["get_admin_router"]
