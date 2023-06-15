from enum import Enum, unique

@unique
class ScraperError(Enum):
    UNAUTHORIZED = 401
    RESOURCE_NOT_FOUND = 404