from pydantic import BaseModel, Field

from app.models.action import Action


class DatasetConfig(BaseModel):

    # =========================
    # Analyzer switches
    # =========================

    enable_corruption_detection: bool = True
    enable_resolution_check: bool = True
    enable_blur_detection: bool = True
    enable_duplicates: bool = True
    enable_clustering: bool = False
    enable_label_validation: bool = False

    # =========================
    # Analyzer actions
    # =========================

    corruption_action: Action = Action.FLAG
    resolution_action: Action = Action.FLAG
    blur_action: Action = Action.QUARANTINE
    duplicate_action: Action = Action.QUARANTINE
    clustering_action: Action = Action.FLAG
    label_validation_action: Action = Action.FLAG

    # =========================
    # Duplicate configuration
    # =========================

    duplicate_policy: str = "quarantine"

    # =========================
    # Blur configuration
    # =========================

    blur_threshold: float = 60.0

    # =========================
    # Resolution configuration
    # =========================

    min_width: int = 224
    min_height: int = 224

    # =========================
    # Train/test configuration
    # =========================

    create_split: bool = False

    train_ratio: float = Field(
        default=0.8,
        gt=0,
        lt=1,
    )

    # =========================
    # Processing configuration
    # =========================

    batch_size: int = 100
    worker_count: int = 4
    max_in_flight: int = 4

    # =========================
    # Label validation
    # =========================

    label_similarity_threshold: float = 0.75
    label_margin: float = 0.03

    # =========================
    # Clustering
    # =========================

    num_clusters: int = 5

    # =========================
    # Action policy
    # =========================

    def get_analyzer_actions(
        self,
    ) -> dict[str, Action]:

        return {
            "corruption": self.corruption_action,
            "resolution": self.resolution_action,
            "blur": self.blur_action,
            "duplicate": self.duplicate_action,
            "clustering": self.clustering_action,
            "label_validation": (
                self.label_validation_action
            ),
        }