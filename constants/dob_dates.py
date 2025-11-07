from datetime import date, datetime, time

MIN_DOB = datetime(1920, 1, 1, 0, 0, 0)
MAX_DOB = datetime.combine(date.today(), time.max)
