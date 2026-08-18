from pathlib import Path
from app.analyzers.corruption import CorruptionAnalyzer
from app.analyzers.resolution import ResolutionAnalyzer
from app.analyzers.blur import BlurAnalyzer
from app.analyzers.duplicate import DuplicateAnalyzer
from app.analyzers.clustering import ClusteringAnalyzer
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
from app.embeddings.embedding_pipeline import EmbeddingPipeline
from app.embeddings.embedding_store import EmbeddingStore
from app.analyzers.label_validation import (
    LabelValidationAnalyzer,
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
        enable_clustering=True,
        num_clusters=5,
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
            "blur": Action.QUARANTINE,
            "duplicate": Action.QUARANTINE,
            "clustering": Action.FLAG,
            "label_validation": Action.FLAG,
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

    # -------------------------
    # 10. Generate embeddings
    # -------------------------

    print()
    print("Generating embeddings...")
    print()

    # Create embedding store first
    embedding_store = EmbeddingStore(
        output_root=str(output_path),
    )

    # Give the store to the pipeline
    embedding_pipeline = EmbeddingPipeline(
        store=embedding_store,
    )

    embedding_pipeline.run(
        working_dataset=working_dataset,
        config=config,
    )

    stored_embeddings, stored_image_ids, stored_labels = (
        embedding_store.load()
    )
    print(
            f"Embeddings generated and stored for "
            f"{len(stored_image_ids)} images."
    )

    # -------------------------
    # 11. Run clustering
    # -------------------------

    print()
    print("Running visual clustering...")
    print()

    clustering_analyzer = ClusteringAnalyzer()

    clustering_result = (
        clustering_analyzer.process_embeddings(
            embeddings=stored_embeddings,
            image_ids=stored_image_ids,
            config=config,
        )
    )
    results.append(clustering_result)

    clustering_action = action_policy.get_action(
        clustering_analyzer.name
    )

    if clustering_action == Action.QUARANTINE:

        for finding in clustering_result.findings:

            quarantine_manager.quarantine(
                finding=finding,
                analyzer_name=clustering_analyzer.name,
            )

    print(
        f"Clustering checked "
        f"{clustering_result.images_checked} images."
    )

    print(
        f"Visual outliers found: "
        f"{clustering_result.issues_found}"
    )

    # -------------------------
    # 12. Run label validation
    # -------------------------

    print()
    print("Running label validation...")
    print()

    label_validation_analyzer = (
        LabelValidationAnalyzer()
    )

    label_validation_result = (
        label_validation_analyzer.process_embeddings(
            embeddings=stored_embeddings,
            image_ids=stored_image_ids,
            labels=stored_labels,
            config=config,
        )
    )

    results.append(
        label_validation_result
    )

    label_validation_action = (
        action_policy.get_action(
            label_validation_analyzer.name
        )
    )

    if (
        label_validation_action
        == Action.QUARANTINE
    ):

        for finding in (
            label_validation_result.findings
        ):

            quarantine_manager.quarantine(
                finding=finding,
                analyzer_name=(
                    label_validation_analyzer.name
                ),
            )

    print(
        f"Label validation checked "
        f"{label_validation_result.images_checked} "
        f"images."
    )

    print(
        f"Label issues found: "
        f"{label_validation_result.issues_found}"
    )
    # -------------------------
    # 12. Export clean dataset
    # -------------------------

    clean_dataset_manager.export(
        working_dataset=working_dataset,
    )

    # -------------------------
    # 13. Generate report
    # -------------------------

    report_writer = ReportWriter()

    report_writer.write_json(
        results=results,
        output_path="data/output/report.json",
    )

    # -------------------------
    # 14. Display results
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