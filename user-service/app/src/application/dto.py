import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserCommand:
    name: str
    email: str
    identification_type: str
    identification_number: str
    birth_date: datetime.date
