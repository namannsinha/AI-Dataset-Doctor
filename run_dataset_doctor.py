from pathlib import Path

from app.analyzers.blur import BlurAnalyzer
from app.analyzers.clustering import ClusteringAnalyzer
from app.analyzers.corruption import CorruptionAnalyzer
from app.analyzers.duplicate import DuplicateAnalyzer
from app.analyzers.label_validation import (
    LabelValidationAnalyzer,
)
from app.analyzers.resolution import ResolutionAnalyzer

from app.clean.clean_dataset_manager import (
    CleanDatasetManager,
)

from app.clustering.cluster_manager import (
    ClusterManager,
)

from app.core.action_policy import ActionPolicy
from app.core.pipeline import Pipeline
from app.core.working_dataset import WorkingDataset

from app.embeddings.embedding_pipeline import (
    EmbeddingPipeline,
)
from app.embeddings.embedding_store import (
    EmbeddingStore,
)

from app.models import Action, DatasetConfig

from app.parsers.folder_parser import FolderParser

from app.quarantine.quarantine_manager import (
    QuarantineManager,
)

from app.reports.report_writer import ReportWriter


def main():

    # =========================
    # 1. Dataset paths
    # =========================

    dataset_path = Path(
        "data/input/practice_dataset"
    )

    output_path = Path(
        "data/output"
    )

    # =========================
    # 2. Parse dataset
    # =========================

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

    # =========================
    # 3. Create working dataset
    # =========================

    working_dataset = WorkingDataset(
        dataset
    )

    # =========================
    # 4. Load configuration
    # =========================
    #
    # All user-configurable settings
    # are loaded from DatasetConfig.
    #

    config = DatasetConfig()

    # =========================
    # 5. Create action policy
    # =========================

    action_policy = ActionPolicy(
        analyzer_actions=(
            config.get_analyzer_actions()
        )
    )

    # =========================
    # 6. Create managers
    # =========================

    quarantine_manager = QuarantineManager(
        output_root=str(output_path),
        working_dataset=working_dataset,
    )

    clean_dataset_manager = (
        CleanDatasetManager(
            output_root=str(output_path),
        )
    )

    # =========================
    # 7. Create analyzers
    # =========================
    #
    # These are the analyzers supported
    # by Dataset Doctor.
    #
    # DatasetConfig determines which
    # analyzers actually execute.
    #

    analyzers = [
        CorruptionAnalyzer(),
        ResolutionAnalyzer(),
        BlurAnalyzer(),
        DuplicateAnalyzer(),
    ]

    # =========================
    # 8. Create image pipeline
    # =========================

    pipeline = Pipeline(
        analyzers=analyzers,
        working_dataset=working_dataset,
        config=config,
        quarantine_manager=quarantine_manager,
        action_policy=action_policy,
    )

    # =========================
    # 9. Run Dataset Doctor
    # =========================

    print()
    print("Running Dataset Doctor...")
    print()

    results = pipeline.run()

    # =========================
    # 10. Embedding-dependent
    #     analyzers
    # =========================

    if (
        config.enable_clustering
        or config.enable_label_validation
    ):

        print()
        print("Generating embeddings...")
        print()

        embedding_store = EmbeddingStore(
            output_root=str(output_path),
        )

        embedding_pipeline = (
            EmbeddingPipeline(
                store=embedding_store,
            )
        )

        embedding_pipeline.run(
            working_dataset=working_dataset,
            config=config,
        )

        (
            stored_embeddings,
            stored_image_ids,
            stored_labels,
        ) = embedding_store.load()

        print(
            f"Embeddings generated and stored "
            f"for {len(stored_image_ids)} images."
        )

        # =========================
        # 11. Visual clustering
        # =========================

        if config.enable_clustering:

            print()
            print(
                "Running visual clustering..."
            )
            print()

            clustering_analyzer = (
                ClusteringAnalyzer()
            )

            clustering_result = (
                clustering_analyzer.process_embeddings(
                    embeddings=stored_embeddings,
                    image_ids=stored_image_ids,
                    config=config,
                )
            )

            # -------------------------
            # Store clustering result
            # -------------------------

            results.append(
                clustering_result
            )

            # -------------------------
            # Create cluster folders
            # -------------------------

            cluster_manager = ClusterManager(
                output_root=str(output_path),
            )

            cluster_manager.create_clusters(
                working_dataset=working_dataset,
                cluster_assignments=(
                    clustering_result
                    .cluster_assignments
                ),
                num_clusters=(
                    config.num_clusters
                ),
                output_dir=(
                    config.cluster_output_dir
                ),
            )

            # -------------------------
            # Display clustering result
            # -------------------------

            print(
                f"Clustering checked "
                f"{clustering_result.images_checked} "
                f"images."
            )

            print(
                f"Visual outliers found: "
                f"{clustering_result.issues_found}"
            )

        else:

            print(
                "Skipping visual clustering."
            )

        # =========================
        # 12. Label validation
        # =========================

        if config.enable_label_validation:

            print()
            print(
                "Running label validation..."
            )
            print()

            label_validation_analyzer = (
                LabelValidationAnalyzer()
            )

            label_validation_result = (
                label_validation_analyzer
                .process_embeddings(
                    embeddings=stored_embeddings,
                    image_ids=stored_image_ids,
                    labels=stored_labels,
                    config=config,
                )
            )

            # -------------------------
            # Store result
            # -------------------------

            results.append(
                label_validation_result
            )

            # -------------------------
            # Determine action
            # -------------------------

            label_validation_action = (
                action_policy.get_action(
                    label_validation_analyzer.name
                )
            )

            # -------------------------
            # Quarantine findings
            # -------------------------

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

            # -------------------------
            # Display result
            # -------------------------

            print(
                f"Label validation checked "
                f"{label_validation_result.images_checked} "
                f"images."
            )

            print(
                f"Label issues found: "
                f"{label_validation_result.issues_found}"
            )

        else:

            print(
                "Skipping label validation."
            )

    else:

        print()
        print(
            "Skipping embeddings: "
            "no embedding-dependent "
            "analyzers are enabled."
        )

    # =========================
    # 13. Export clean dataset
    # =========================

    clean_dataset_manager.export(
        working_dataset=working_dataset,
    )

    # =========================
    # 14. Generate report
    # =========================

    report_writer = ReportWriter()

    report_writer.write_json(
        results=results,
        output_path=(
            "data/output/report.json"
        ),
    )

    # =========================
    # 15. Display results
    # =========================

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