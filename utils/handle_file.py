def handle_file_from_message(message) -> str | None:
    if message.document:
        return message.document.file_id, "document"
    elif message.photo:
        return message.photo[-1].file_id, "photo"
    elif message.video:
        return message.video.file_id, "video"
