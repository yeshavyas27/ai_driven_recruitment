from enum import Enum


class MatchCriteria(int, Enum):
    STRICT = 3
    MODERATE = 2
    FLEXIBLE = 1