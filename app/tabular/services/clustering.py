import pandas as pd

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from app.tabular.services.preprocessing import prepare_features
from app.tabular.services.dimensionality import reduce_dimensions


def _get_cluster_counts(clusters):
    """
    Convert cluster labels into a JSON-safe count dictionary.
    """

    counts = pd.Series(clusters).value_counts().sort_index()

    return {
        str(int(cluster)): int(count)
        for cluster, count in counts.items()
    }


def _get_numeric_cluster_profiles(df, clusters, top_n=5):
    """
    Find numerical features that distinguish each cluster
    from the overall dataset.
    """

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    # Don't use obvious identifier columns for interpretation.
    numeric_columns = [
        column
        for column in numeric_columns
        if not (
            column.upper().startswith("SK_ID")
            or column.upper() == "ID"
        )
    ]

    if not numeric_columns:
        return {}

    working_df = df[numeric_columns].copy()

    global_means = working_df.mean()
    global_stds = working_df.std().replace(0, 1)

    profiles = {}

    for cluster_id in sorted(set(clusters)):

        mask = clusters == cluster_id

        cluster_df = working_df.loc[mask]

        cluster_means = cluster_df.mean()

        differences = (
            (cluster_means - global_means)
            / global_stds
        ).abs()

        top_features = differences.nlargest(
            top_n
        ).index.tolist()

        features = []

        for column in top_features:

            value = cluster_means[column]

            if pd.isna(value):
                continue

            direction = (
                "higher"
                if cluster_means[column]
                > global_means[column]
                else "lower"
            )

            features.append({
                "feature": column,
                "value": round(
                    float(value),
                    4
                ),
                "global_value": round(
                    float(global_means[column]),
                    4
                ),
                "direction": direction,
                "difference_score": round(
                    float(differences[column]),
                    4
                )
            })

        profiles[str(cluster_id)] = features

    return profiles


def _get_categorical_cluster_profiles(
    df,
    clusters,
    top_n=3
):
    """
    Find categorical values that are unusually common
    inside each cluster compared with the full dataset.
    """

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    if not categorical_columns:
        return {}

    profiles = {}

    cluster_series = pd.Series(
        clusters,
        index=df.index
    )

    for cluster_id in sorted(set(clusters)):

        cluster_mask = (
            cluster_series == cluster_id
        )

        cluster_size = int(
            cluster_mask.sum()
        )

        if cluster_size == 0:
            continue

        candidates = []

        for column in categorical_columns:

            column_data = df[column].astype(
                "object"
            )

            global_distribution = (
                column_data
                .value_counts(
                    normalize=True,
                    dropna=False
                )
            )

            cluster_distribution = (
                column_data[cluster_mask]
                .value_counts(
                    normalize=True,
                    dropna=False
                )
            )

            for value, cluster_ratio in (
                cluster_distribution.items()
            ):

                global_ratio = float(
                    global_distribution.get(
                        value,
                        0
                    )
                )

                difference = (
                    float(cluster_ratio)
                    - global_ratio
                )

                # Only consider values that are
                # meaningfully more common in this cluster.
                if difference > 0:

                    candidates.append({
                        "feature": column,
                        "value": (
                            "Missing"
                            if pd.isna(value)
                            else str(value)
                        ),
                        "cluster_percentage": round(
                            float(cluster_ratio) * 100,
                            2
                        ),
                        "global_percentage": round(
                            global_ratio * 100,
                            2
                        ),
                        "difference": round(
                            difference * 100,
                            2
                        )
                    })

        candidates.sort(
            key=lambda item: item["difference"],
            reverse=True
        )

        profiles[str(cluster_id)] = (
            candidates[:top_n]
        )

    return profiles


def perform_clustering(
    df,
    n_clusters=3
):
    """
    Perform mixed-type clustering.

    Pipeline:

    Raw dataframe
        ↓
    Numeric + ordinal + nominal detection
        ↓
    Missing-value handling
        ↓
    Ordinal encoding
        ↓
    One-hot encoding
        ↓
    Scaling
        ↓
    PCA dimensionality reduction
        ↓
    K-Means
        ↓
    Cluster interpretation
        ↓
    2D PCA visualization
    """

    if len(df) < n_clusters:
        raise ValueError(
            f"Dataset must contain at least "
            f"{n_clusters} rows."
        )

    # ---------------------------------------------------------
    # 1. Prepare mixed-type features
    # ---------------------------------------------------------

    X, feature_metadata = prepare_features(
        df
    )

    if X.shape[1] < 2:
        raise ValueError(
            "Not enough usable features for clustering."
        )

    # ---------------------------------------------------------
    # 2. Dimensionality reduction
    # ---------------------------------------------------------

    X_reduced, reduction_info = (
        reduce_dimensions(
            X,
            variance_threshold=0.95,
            max_components=30
        )
    )

    # ---------------------------------------------------------
    # 3. K-Means
    # ---------------------------------------------------------

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    clusters = model.fit_predict(
        X_reduced
    )

    # ---------------------------------------------------------
    # 4. Cluster counts
    # ---------------------------------------------------------

    cluster_counts = _get_cluster_counts(
        clusters
    )

    # ---------------------------------------------------------
    # 5. Cluster interpretation
    # ---------------------------------------------------------

    numeric_profiles = (
        _get_numeric_cluster_profiles(
            df,
            clusters
        )
    )

    categorical_profiles = (
        _get_categorical_cluster_profiles(
            df,
            clusters
        )
    )

    cluster_profiles = []

    for cluster_id in sorted(
        set(clusters)
    ):

        cluster_key = str(
            int(cluster_id)
        )

        count = cluster_counts[
            cluster_key
        ]

        percentage = (
            count / len(df)
        ) * 100

        cluster_profiles.append({

            "cluster": int(
                cluster_id
            ),

            "records": count,

            "percentage": round(
                percentage,
                2
            ),

            "numeric_signals":
                numeric_profiles.get(
                    cluster_key,
                    []
                ),

            "categorical_signals":
                categorical_profiles.get(
                    cluster_key,
                    []
                )
        })

    # ---------------------------------------------------------
    # 6. PCA 2D visualization
    # ---------------------------------------------------------

    pca_2d = PCA(
        n_components=2
    )

    pca_data = pca_2d.fit_transform(
        X
    )

    visualization_data = []

    # Limit points sent to frontend.
    # We sample evenly rather than simply taking
    # the first 1000 rows.
    max_points = 1000

    if len(pca_data) > max_points:

        sample_indices = (
            pd.Series(range(len(pca_data)))
            .sample(
                n=max_points,
                random_state=42
            )
            .sort_values()
            .tolist()
        )

    else:

        sample_indices = list(
            range(len(pca_data))
        )

    for index in sample_indices:

        visualization_data.append({

            "x": round(
                float(
                    pca_data[index][0]
                ),
                4
            ),

            "y": round(
                float(
                    pca_data[index][1]
                ),
                4
            ),

            "cluster": int(
                clusters[index]
            )
        })

    # ---------------------------------------------------------
    # 7. Explained variance
    # ---------------------------------------------------------

    explained_variance = {

        "pc1": round(
            float(
                pca_2d
                .explained_variance_ratio_[0]
                * 100
            ),
            2
        ),

        "pc2": round(
            float(
                pca_2d
                .explained_variance_ratio_[1]
                * 100
            ),
            2
        )
    }

    # ---------------------------------------------------------
    # 8. Sample data
    # ---------------------------------------------------------

    result = df.copy()

    result["cluster"] = clusters

    sample_data = result.head(
        100
    ).copy()

    sample_data = sample_data.where(
        pd.notnull(sample_data),
        None
    )

    sample_data = sample_data.to_dict(
        orient="records"
    )

    # ---------------------------------------------------------
    # 9. Final response
    # ---------------------------------------------------------

    return {

        "n_clusters":
            n_clusters,

        "method":
            "K-Means",

        "features_used":
            feature_metadata,

        "dimensionality_reduction":
            reduction_info,

        "cluster_counts":
            cluster_counts,

        "cluster_profiles":
            cluster_profiles,

        "pca": {

            "explained_variance":
                explained_variance,

            "points":
                visualization_data
        },

        "data":
            sample_data
    }