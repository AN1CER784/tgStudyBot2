from enum import Enum

from tortoise import models, fields


class QType(str, Enum):
    single = "single"
    text = "text"


class Test(models.Model):
    id = fields.IntField(pk=True, auto_increment=True)
    title = fields.CharField(255)
    description = fields.TextField(null=True)
    shuffle_questions = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    fail_message = fields.TextField(null=True)
    perfect_success_message = fields.TextField(null=True)
    normal_success_message = fields.TextField(null=True)

    class Meta:
        table = 'test'


class Question(models.Model):
    id = fields.IntField(pk=True, auto_increment=True)
    test = fields.ForeignKeyField("models.Test", related_name="questions", on_delete=fields.CASCADE)
    text = fields.TextField()
    type = fields.CharEnumField(QType)
    order = fields.IntField(default=0)
    points = fields.FloatField(default=1.0)

    class Meta:
        indexes = (("test_id", "order"),)
        table = 'question'


class Option(models.Model):
    id = fields.IntField(pk=True, auto_increment=True)
    question = fields.ForeignKeyField("models.Question", related_name="options", on_delete=fields.CASCADE)
    text = fields.TextField()
    is_correct = fields.BooleanField(default=False)
    order = fields.IntField(default=0)

    class Meta:
        indexes = (("question_id", "order"),)
        table = 'option'


class AttemptStatus(str, Enum):
    in_progress = "in_progress"
    completed = "completed"
    aborted = "aborted"


class Attempt(models.Model):
    id = fields.IntField(pk=True, auto_increment=True)
    user = fields.ForeignKeyField("models.User", related_name="attempts", on_delete=fields.CASCADE)
    test = fields.ForeignKeyField("models.Test", related_name="attempts", on_delete=fields.CASCADE)
    started_at = fields.DatetimeField(auto_now_add=True)
    finished_at = fields.DatetimeField(null=True)
    status = fields.CharEnumField(AttemptStatus, default=AttemptStatus.in_progress)
    score = fields.FloatField(default=0.0)
    max_score = fields.FloatField(default=0.0)
    attempt_no = fields.IntField(default=1)
    review_comment = fields.TextField(null=True)

    class Meta:
        indexes = (("user_id", "test_id"),)
        table = 'attempt'


class Answer(models.Model):
    id = fields.IntField(pk=True, auto_increment=True)
    question = fields.ForeignKeyField("models.Question", related_name="answers", on_delete=fields.CASCADE)
    attempt = fields.ForeignKeyField("models.Attempt", related_name="answers", on_delete=fields.CASCADE)
    selected_option = fields.ForeignKeyField("models.Option", null=True, on_delete=fields.SET_NULL)  # для single
    text_answer = fields.TextField(null=True)  # для text
    is_correct = fields.BooleanField(null=True)
    points_awarded = fields.FloatField(default=0.0)

    class Meta:
        unique_together = (("attempt_id", "question_id"),)
        table = 'answer'
