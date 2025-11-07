from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "lesson" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "type" VARCHAR(11) NOT NULL DEFAULT 'task_lesson',
    "video_message_id" VARCHAR(2048) NOT NULL
);
COMMENT ON COLUMN "lesson"."type" IS 'free_lesson: free_lesson\ntask_lesson: task_lesson';
CREATE TABLE IF NOT EXISTS "test" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "shuffle_questions" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "fail_message" TEXT,
    "perfect_success_message" TEXT,
    "normal_success_message" TEXT
);
CREATE TABLE IF NOT EXISTS "question" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" TEXT NOT NULL,
    "type" VARCHAR(6) NOT NULL,
    "order" INT NOT NULL DEFAULT 0,
    "points" DOUBLE PRECISION NOT NULL DEFAULT 1,
    "test_id" INT NOT NULL REFERENCES "test" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_question_test_id_3b0bd1" ON "question" ("test_id", "order");
COMMENT ON COLUMN "question"."type" IS 'single: single\ntext: text';
CREATE TABLE IF NOT EXISTS "option" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" TEXT NOT NULL,
    "is_correct" BOOL NOT NULL DEFAULT False,
    "order" INT NOT NULL DEFAULT 0,
    "question_id" INT NOT NULL REFERENCES "question" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_option_questio_6addef" ON "option" ("question_id", "order");
CREATE TABLE IF NOT EXISTS "user" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "full_name" VARCHAR(255),
    "phone" VARCHAR(15),
    "birthday" DATE,
    "sex" VARCHAR(5),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "role" VARCHAR(7) NOT NULL DEFAULT 'user',
    "is_allowed" BOOL NOT NULL DEFAULT True
);
COMMENT ON COLUMN "user"."sex" IS 'woman: woman\nman: man';
COMMENT ON COLUMN "user"."role" IS 'user: user\ncurator: curator\nadmin: admin';
CREATE TABLE IF NOT EXISTS "attempt" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "started_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "finished_at" TIMESTAMPTZ,
    "status" VARCHAR(11) NOT NULL DEFAULT 'in_progress',
    "score" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "max_score" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "attempt_no" INT NOT NULL DEFAULT 1,
    "review_comment" TEXT,
    "test_id" INT NOT NULL REFERENCES "test" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_attempt_user_id_1c29d4" ON "attempt" ("user_id", "test_id");
COMMENT ON COLUMN "attempt"."status" IS 'in_progress: in_progress\ncompleted: completed\naborted: aborted';
CREATE TABLE IF NOT EXISTS "answer" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text_answer" TEXT,
    "is_correct" BOOL,
    "points_awarded" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "attempt_id" INT NOT NULL REFERENCES "attempt" ("id") ON DELETE CASCADE,
    "question_id" INT NOT NULL REFERENCES "question" ("id") ON DELETE CASCADE,
    "selected_option_id" INT REFERENCES "option" ("id") ON DELETE SET NULL,
    CONSTRAINT "uid_answer_attempt_849c68" UNIQUE ("attempt_id", "question_id")
);
CREATE TABLE IF NOT EXISTS "lesson_response" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "response" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "is_correct" BOOL,
    "review_comment" TEXT,
    "lesson_id" INT NOT NULL REFERENCES "lesson" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_lesson_resp_user_id_52d60f" ON "lesson_response" ("user_id", "lesson_id");
CREATE TABLE IF NOT EXISTS "user_progress" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "current_stage" VARCHAR(20) NOT NULL DEFAULT 'start',
    "stage_index" SMALLINT DEFAULT 0,
    "stage_total" SMALLINT DEFAULT 0,
    "started_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL UNIQUE REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_user_progre_user_id_e9efc6" ON "user_progress" ("user_id", "current_stage");
COMMENT ON COLUMN "user_progress"."current_stage" IS 'start: start\nentry_test: entry_test\nlesson: lesson\nlesson_on_completion: lesson_on_completion\nfinal_test: final_test\ndone: done';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
