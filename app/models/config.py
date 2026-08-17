from pydantic import BaseModel, Field


class DatasetConfig(BaseModel):

    # Duplicate handling
    duplicate_policy: str = "quarantine"

    # Blur configuration
    blur_threshold: float = 60.0

    # Resolution configuration
    min_width: int = 224
    min_height: int = 224

    # Train/test configuration
    create_split: bool = False
    train_ratio: float = Field(default=0.8, gt=0, lt=1)

    # Processing configuration
    batch_size: int = 100
    worker_count: int = 4
    max_in_flight: int = 4

    # Label validation configuration
    label_similarity_threshold: float = 0.75
    label_margin: float = 0.03
    enable_label_validation: bool = False

    enable_clustering: bool = False
    num_clusters: int = 5