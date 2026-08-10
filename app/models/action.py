from enum import Enum


class Action(str, Enum):
    FLAG = "flag"
    QUARANTINE = "quarantine"
    IGNORE = "ignore"