from app.chatbot.engine import MithuruEngine

tests = [
    ("bye", True),
    ("oky bay", True),
    ("oky buy", True),
    ("oky im going to go .bye", True),
    ("ok bye", True),
    ("good night", True),
    ("no im going to seleep thank you for your help", True),
    ("im going to go", True),
    ("yes tell me how much time it will take", False),
    ("my photos were leaked", False),
    ("yes i have the link", False),
    ("im amanda cooray", False),
    ("thank you bye", True),
    ("take care", True),
    ("gotta go", True),
]
for msg, expected in tests:
    result = MithuruEngine._is_farewell(msg)
    status = "OK" if result == expected else "FAIL"
    print(f'{status}: "{msg}" -> {result} (expected {expected})')
