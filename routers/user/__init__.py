from aiogram import Router

from routers.user.lesson_router import router as lesson_router
from routers.user.profile_router import router as profile_router
from routers.user.register_router import router as register_router
from routers.user.start_router import router as start_router
from routers.user.entry_test_router import router as entry_test_router
from routers.user.final_test_router import router as final_test_router
from routers.user.done_router import router as done_router
from routers.user.review_router import router as review_router


def get_user_router() -> Router:
    router = Router(name="user_root")
    router.include_router(start_router)
    router.include_router(register_router)
    router.include_router(entry_test_router)
    router.include_router(final_test_router)
    router.include_router(done_router)
    router.include_router(profile_router)
    router.include_router(lesson_router)
    router.include_router(review_router)
    return router


__all__ = ["get_user_router"]
