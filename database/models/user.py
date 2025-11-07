
from enum import Enum

from tortoise import Model, fields
from tortoise.validators import RegexValidator


class Stage(str, Enum):
    start = "start"
    entry_test = "entry_test"
    lesson = "lesson"
    lesson_on_completion = "lesson_on_completion"
    final_test = "final_test"
    done = "done"


class Roles(str, Enum):
    user = "user"
    curator = "curator"
    admin = "admin"


class Sexes(str, Enum):
    woman = "woman"
    man = "man"


class User(Model):
    id = fields.BigIntField(pk=True)
    full_name = fields.CharField(max_length=255, null=True)
    phone = fields.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?[1-9]\d{1,14}$', flags=0)], null=True
    )
    birthday = fields.DateField(null=True)
    sex = fields.CharEnumField(Sexes, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    role = fields.CharEnumField(Roles, default=Roles.user)
    is_allowed = fields.BooleanField(default=True)

    class Meta:
        table = 'user'


class UserProgress(Model):
    id = fields.IntField(pk=True, auto_increment=True)
    user = fields.OneToOneField('models.User', related_name='progress', on_delete=fields.CASCADE)
    current_stage = fields.CharEnumField(Stage, default=Stage.start)
    stage_index = fields.SmallIntField(default=0, null=True)
    stage_total = fields.SmallIntField(default=0, null=True)
    started_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = 'user_progress'
        indexes = (("user_id", "current_stage"),)
