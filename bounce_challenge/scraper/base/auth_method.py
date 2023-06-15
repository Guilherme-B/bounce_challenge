from dataclasses import dataclass
from enum import Enum, unique

@unique
class AuthMethodType(Enum):
    TOKEN = "token"
    USERNAME = "username"

@dataclass
class AuthMethodToken:
    token: str
    method_type: AuthMethodType = AuthMethodType.TOKEN