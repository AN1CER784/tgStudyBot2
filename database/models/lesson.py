from enum import Enum

from tortoise import Model, fields


class LessonType(str, Enum):
    free_lesson = "free_lesson"
    task_lesson = "task_lesson"


class ResponseType(str, Enum):
    text = "text"
    file = "file"


class FileTypes(str, Enum):
    photo = "photo"
    video = "video"
    document = "document"


class Lesson(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    type = fields.CharEnumField(LessonType, default=LessonType.task_lesson)
    response_type = fields.CharEnumField(ResponseType, default=ResponseType.text)
    video_message_ids = fields.JSONField(default=list)
    is_commentable = fields.BooleanField(default=False)

    class Meta:
        table = 'lesson'


class LessonResponse(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='responses', on_delete=fields.CASCADE)
    lesson = fields.ForeignKeyField('models.Lesson', related_name='responses', on_delete=fields.CASCADE)
    response = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_correct = fields.BooleanField(null=True)
    review_comment = fields.TextField(null=True)

    class Meta:
        table = 'lesson_response'
        indexes = (("user_id", "lesson_id"),)
        unique_together = ("user_id", "lesson_id")


class LessonResponseFile(Model):
    id = fields.IntField(pk=True)
    file_id = fields.CharField(max_length=255)
    file_type = fields.CharEnumField(FileTypes, default=FileTypes.document)
    lesson_response = fields.ForeignKeyField('models.LessonResponse', related_name='files', on_delete=fields.CASCADE)

    class Meta:
        table = 'lesson_response_file'
