from pathlib import Path
import shutil

from app.analyzers.blur import BlurAnalyzer
from app.analyzers.clustering import ClusteringAnalyzer
from app.analyzers.corruption import CorruptionAnalyzer
from app.analyzers.duplicate import DuplicateAnalyzer
from app.analyzers.label_validation import LabelValidationAnalyzer
from app.analyzers.resolution import ResolutionAnalyzer
from app.clean.clean_dataset_manager import CleanDatasetManager
from app.core.action_policy import ActionPolicy
from app.core.pipeline import Pipeline
from app.core.working_dataset import WorkingDataset
from app.embeddings.embedding_pipeline import EmbeddingPipeline
from app.embeddings.embedding_store import EmbeddingStore
from app.models import Action, DatasetConfig
from app.parsers.folder_parser import FolderParser
from app.quarantine.quarantine_manager import QuarantineManager
from app.reports.report_writer import ReportWriter


def export_clusters(
    working_dataset,
    cluster_assignments: dict[str, int],
    output_dir: Path,
) -> None:
    """Copy active images into folders according to their cluster assignment."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clear previous cluster exports so folders from an older run do not remain.
    for item in output_dir.iterdir():
        if (
            item.is_dir()
            and item.name.startswith("cluster_")
            and item.name.removeprefix("cluster_").isdigit()
        ):
            shutil.rmtree(item)

    images_by_id = {
        image.id: image
        for image in working_dataset.iter_images()
    }

    copied = 0
    skipped = 0

    for image_id, cluster_id in cluster_assignments.items():
        image = images_by_id.get(image_id)

        if image is None:
            skipped += 1
            continue

        source = Path(image.path)
        if not source.is_file():
            source = Path(image.original_path)

        if not source.is_file():
            print(f"Warning: source file not found for image {image_id}; skipping.")
            skipped += 1
            continue

        cluster_dir = output_dir / f"cluster_{cluster_id}"
        cluster_dir.mkdir(parents=True, exist_ok=True)

        destination = cluster_dir / source.name
        if destination.exists():
            destination = cluster_dir / f"{image_id}_{source.name}"

        shutil.copy2(source, destination)
        copied += 1

    print(f"Clustered images exported: {copied}")
    if skipped:
        print(f"Images skipped during cluster export: {skipped}")
    print(f"Cluster output: {output_dir}")


def main(
    dataset_path: Path = Path("data/input/practice_dataset"),
    output_path: Path = Path("data/output"),
    *,
    blur_threshold: float = 60.0,
    min_width: int = 224,
    min_height: int = 224,
    batch_size: int = 5,
    enable_clustering: bool = True,
    num_clusters: int = 2,
    enable_label_validation: bool = True,
    analyzer_actions: dict[str, str] | None = None,
) -> None:
    # 1. Dataset and output paths

    # 2. Parse dataset
    print("Loading dataset...")
    parser = FolderParser()
    dataset = parser.parse(str(dataset_path))

    print(f"Dataset loaded: {dataset.name}")
    print(f"Images found: {len(dataset.images)}")

    # 3. Create the working dataset
    working_dataset = WorkingDataset(dataset)

    # 4. Configuration
    # Set num_clusters here to control the number of cluster folders.
    config = DatasetConfig(
        blur_threshold=blur_threshold,
        min_width=min_width,
        min_height=min_height,
        batch_size=batch_size,
        enable_clustering=enable_clustering,
        num_clusters=num_clusters,
        enable_label_validation=enable_label_validation,
    )

    print(f"Configured clusters: {config.num_clusters}")
    print(f"Clustering enabled: {config.enable_clustering}")

    # 5. Managers
    quarantine_manager = QuarantineManager(
        output_root=str(output_path),
        working_dataset=working_dataset,
    )
    clean_dataset_manager = CleanDatasetManager(
        output_root=str(output_path),
    )

    # 6. Actions: use DatasetConfig as the source of truth.
    default_actions = config.get_analyzer_actions()

    if analyzer_actions is not None:
        for name, action in analyzer_actions.items():
            if name not in default_actions:
                raise ValueError(f"Unknown analyzer: {name}")

            default_actions[name] = Action(action)

    action_policy = ActionPolicy(
        analyzer_actions=default_actions
    )

    # 7. Core analyzers
    analyzers = [
        CorruptionAnalyzer(),
        ResolutionAnalyzer(),
        BlurAnalyzer(),
        DuplicateAnalyzer(),
    ]

    # 8. Run core pipeline
    pipeline = Pipeline(
        analyzers=analyzers,
        working_dataset=working_dataset,
        config=config,
        quarantine_manager=quarantine_manager,
        action_policy=action_policy,
    )

    print("\nRunning Dataset Doctor...\n")
    results = pipeline.run()
    
    # 9. Run embedding-dependent analyzers only when needed.
    clustering_enabled = (
        config.enable_clustering
        and action_policy.get_action("clustering") != Action.IGNORE
    )
    label_validation_enabled = (
        config.enable_label_validation
        and action_policy.get_action("label_validation") != Action.IGNORE
    )

    if clustering_enabled or label_validation_enabled:
        print("\nGenerating embeddings...\n")

        embedding_store = EmbeddingStore(
            output_root=str(output_path)
        )
        embedding_pipeline = EmbeddingPipeline(
            store=embedding_store
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

        # 10. Visual clustering
        if clustering_enabled:
            print("\nRunning visual clustering...\n")

            clustering_analyzer = ClusteringAnalyzer()
            clustering_result = clustering_analyzer.process_embeddings(
                embeddings=stored_embeddings,
                image_ids=stored_image_ids,
                config=config,
            )
            results.append(clustering_result)

            print(
                f"Configured clusters: {config.num_clusters}"
            )
            print(
                f"Clustering checked "
                f"{clustering_result.images_checked} images."
            )
            print(
                f"Visual outliers found: "
                f"{clustering_result.issues_found}"
            )

            export_clusters(
                working_dataset=working_dataset,
                cluster_assignments=(
                    clustering_analyzer.cluster_assignments
                ),
                output_dir=output_path / "clusters",
            )

            if (
                action_policy.get_action("clustering")
                == Action.QUARANTINE
            ):
                for finding in clustering_result.findings:
                    quarantine_manager.quarantine(
                        finding=finding,
                        analyzer_name=clustering_analyzer.name,
                    )
        else:
            print("\nClustering disabled or ignored; skipping.")

        # 11. Label validation
        if label_validation_enabled:
            print("\nRunning label validation...\n")

            label_validation_analyzer = LabelValidationAnalyzer()
            label_validation_result = (
                label_validation_analyzer.process_embeddings(
                    embeddings=stored_embeddings,
                    image_ids=stored_image_ids,
                    labels=stored_labels,
                    config=config,
                )
            )
            results.append(label_validation_result)

            print(
                f"Label validation checked "
                f"{label_validation_result.images_checked} images."
            )
            print(
                f"Label issues found: "
                f"{label_validation_result.issues_found}"
            )

            if (
                action_policy.get_action("label_validation")
                == Action.QUARANTINE
            ):
                for finding in label_validation_result.findings:
                    quarantine_manager.quarantine(
                        finding=finding,
                        analyzer_name=label_validation_analyzer.name,
                    )
        else:
            print("\nLabel validation disabled or ignored; skipping.")
    else:
        print(
            "\nSkipping embeddings: clustering and label validation "
            "are both disabled or ignored."
        )


    # 12. Export remaining active images and report
    clean_dataset_manager.export(working_dataset=working_dataset)

    report_writer = ReportWriter()
    report_writer.write_json(
        results=results,
        output_path=str(output_path / "report.json"),
    )

    # 13. Display summary
    print("\n" + "=" * 50)
    print("DATASET DOCTOR RESULTS")
    print("=" * 50)

    for result in results:
        print(f"\nAnalyzer: {result.analyzer}")
        print(f"Images checked: {result.images_checked}")
        print(f"Issues found: {result.issues_found}")

        for finding in result.findings:
            print(f"  - {finding.image_id}")
            print(f"    Type: {finding.issue_type}")
            print(f"    Severity: {finding.severity}")
            print(f"    Reason: {finding.reason}")

    print("\n" + "=" * 50)
    print(f"Active images after analysis: {working_dataset.total_images}")
    print("=" * 50)


if __name__ == "__main__":
    main()
