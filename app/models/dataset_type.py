from enum import Enum


class DatasetType(str, Enum):
    TRAIN_TEST = "train_test"
    CLASS_SEPARATED = "class_separated"
    FLAT = "flat"