from dataclasses import dataclass
from datetime import date


@dataclass
class User:
    ssn: str
    first_name: str
    last_name: str
    date_of_birth: date
