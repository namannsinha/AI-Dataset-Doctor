from pathlib import Path

from app.analyzers.corruption import CorruptionAnalyzer
from app.analyzers.resolution import ResolutionAnalyzer
from app.analyzers.blur import BlurAnalyzer
from app.analyzers.duplicate import DuplicateAnalyzer

from app.core.action_policy import ActionPolicy
from app.core.pipeline import Pipeline
from app.core.working_dataset import WorkingDataset

from app.models import Action, DatasetConfig

from app.parsers.folder_parser import FolderParser

from app.quarantine.quarantine_manager import (
    QuarantineManager,
)
from app.reports.report_writer import ReportWriter
from app.clean.clean_dataset_manager import (
    CleanDatasetManager,
)


def main():

    # -------------------------
    # 1. Dataset paths
    # -------------------------

    dataset_path = Path(
        "data/input/practice_dataset"
    )

    output_path = Path(
        "data/output"
    )

    # -------------------------
    # 2. Parse dataset
    # -------------------------

    print("Loading dataset...")

    parser = FolderParser()

    dataset = parser.parse(
        str(dataset_path)
    )

    print(
        f"Dataset loaded: {dataset.name}"
    )

    print(
        f"Images found: {len(dataset.images)}"
    )

    # -------------------------
    # 3. Create working dataset
    # -------------------------

    working_dataset = WorkingDataset(
        dataset
    )

    # -------------------------
    # 4. Configuration
    # -------------------------

    config = DatasetConfig(
        blur_threshold=60.0,
        min_width=224,
        min_height=224,
        batch_size=5,
    )

    # -------------------------
    # 5. Quarantine manager
    # -------------------------

    quarantine_manager = QuarantineManager(
        output_root=str(output_path),
        working_dataset=working_dataset,
    )

    clean_dataset_manager = CleanDatasetManager(
        output_root=str(output_path),
    )
    print("CLEAN ROOT:", clean_dataset_manager.clean_root)
    print("CLEAN ROOT EXISTS:", clean_dataset_manager.clean_root.exists())
    # -------------------------
    # 6. Action policy
    # -------------------------
    #
    # IMPORTANT:
    # First real run = FLAG ONLY.
    #
    # Nothing will be moved.
    #

    action_policy = ActionPolicy(
        analyzer_actions={
            "corruption": Action.QUARANTINE,
            "resolution": Action.FLAG,
            "blur": Action.FLAG,
            "duplicate": Action.FLAG,
        }
    )

    # -------------------------
    # 7. Create analyzers
    # -------------------------

    analyzers = [
        CorruptionAnalyzer(),
        ResolutionAnalyzer(),
        BlurAnalyzer(),
        DuplicateAnalyzer(),
    ]

    # -------------------------
    # 8. Create pipeline
    # -------------------------

    pipeline = Pipeline(
        analyzers=analyzers,
        working_dataset=working_dataset,
        config=config,
        quarantine_manager=quarantine_manager,
        action_policy=action_policy,
    )

    # -------------------------
    # 9. Run Dataset Doctor
    # -------------------------

    print()
    print("Running Dataset Doctor...")
    print()

    results = pipeline.run()
    clean_dataset_manager.export(
        working_dataset=working_dataset,
    )
    report_writer = ReportWriter()

    report_writer.write_json(
        results=results,
        output_path="data/output/report.json",
    )

    # -------------------------
    # 10. Display results
    # -------------------------

    print()
    print("=" * 50)
    print("DATASET DOCTOR RESULTS")
    print("=" * 50)

    for result in results:

        print()
        print(
            f"Analyzer: {result.analyzer}"
        )

        print(
            f"Images checked: "
            f"{result.images_checked}"
        )

        print(
            f"Issues found: "
            f"{result.issues_found}"
        )

        for finding in result.findings:

            print(
                f"  - {finding.image_id}"
            )

            print(
                f"    Type: "
                f"{finding.issue_type}"
            )

            print(
                f"    Severity: "
                f"{finding.severity}"
            )

            print(
                f"    Reason: "
                f"{finding.reason}"
            )

    print()
    print("=" * 50)

    print(
        f"Active images after analysis: "
        f"{working_dataset.total_images}"
    )

    print("=" * 50)


if __name__ == "__main__":
    main()