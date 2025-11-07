from typing import Literal, List, Tuple

from constants.pagination import PAGE_SIZE
from database.models import User, UserProgress
from database.models.user import Roles, Stage


async def add_or_update_user(user_id: int, full_name: str | None = None, birthday: str | None = None,
                             phone: str | None = None,
                             role: Literal['user', 'admin', 'curator'] | None = None, is_allowed: bool = True):
    user = await User.update_or_create(
        id=user_id,
        defaults={
            "full_name": full_name,
            "birthday": birthday,
            "phone": phone,
            "role": role,
            "is_allowed": is_allowed
        }
    )
    return user


async def update_user_role(user_id: int, role: Literal['user', 'admin', 'curator']) -> User:
    user = await User.get(id=user_id)
    user.role = role
    await user.save()
    return user


async def get_user(user_id: int) -> User:
    user = await User.filter(id=user_id).prefetch_related('progress').first()
    return user


async def create_or_update_user_stage(user_id: int, stage: str, stage_index: int | None = None,
                                      stage_total: int | None = None) -> UserProgress:
    user_progress, _ = await UserProgress.update_or_create(
        user_id=user_id,
        defaults={
            "current_stage": stage,
            "stage_index": stage_index,
            "stage_total": stage_total,
        }
    )
    return user_progress


async def get_admins() -> List[User]:
    admins = await User.filter(role__in=['admin']).all()
    return admins


async def get_curators() -> List[User]:
    curators = await User.filter(role__in=['curator']).all()
    return curators


async def get_all_users(page: int = 0) -> Tuple[List[User], int]:
    total = await User.all().count()
    users = await User.all().order_by("-id").offset(page * PAGE_SIZE).limit(PAGE_SIZE)
    return users, total


async def get_common_users_with_progress() -> Tuple[List[User], int]:
    return await User.filter(role=Roles.user).exclude(progress__current_stage=Stage.done).order_by("-id")


async def grant_access(tg_id: int) -> User:
    user, _ = await User.get_or_create(id=tg_id, defaults={"role": "user", "is_allowed": True})
    if not user.is_allowed:
        user.is_allowed = True
        await user.save()
    return user


async def revoke_access(tg_id: int) -> User | None:
    user = await User.get_or_none(id=tg_id)
    if not user:
        return None
    user.is_allowed = False
    await user.save()
    return user


async def set_role(tg_id: int, role: str) -> User:
    assert role in ("user", "curator", "admin")
    user, _ = await User.get_or_create(id=tg_id, defaults={"role": role, "is_allowed": True})
    user.role = role
    if role in ("curator", "admin"):
        user.is_allowed = True
    await user.save()
    return user
