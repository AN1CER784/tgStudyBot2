from aiogram import Router

from routers.curator.list_router import router as list_router
from routers.curator.review_router import router as review_router


def get_curator_router() -> Router:
    router = Router(name="curator_root")
    router.include_router(list_router)
    router.include_router(review_router)
    return router


__all__ = ["get_curator_router"]
