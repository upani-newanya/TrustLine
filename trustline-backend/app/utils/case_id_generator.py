from datetime import datetime
from random import randint


def generate_case_id() -> str:
    return f"TL-{datetime.utcnow().strftime('%Y%m%d')}-{randint(1000, 9999)}"
