import numpy as np
from sklearn.decomposition import PCA


def reduce_dimensions(
    X,
    variance_threshold=0.95,
    max_components=30,
):
    """
    Reduce a high-dimensional feature matrix while
    retaining approximately the requested amount of variance.
    """

    original_dimensions = X.shape[1]

    # No need for reduction when the feature space is already small.
    if original_dimensions <= max_components:
        return X, {
            "applied": False,
            "original_dimensions": original_dimensions,
            "reduced_dimensions": original_dimensions,
            "explained_variance": 100.0,
        }

    # Determine how many components are needed to preserve
    # the requested amount of information.
    probe = PCA()
    probe.fit(X)

    cumulative_variance = np.cumsum(
        probe.explained_variance_ratio_
    )

    components = (
        np.searchsorted(
            cumulative_variance,
            variance_threshold,
        )
        + 1
    )

    components = min(
        components,
        max_components,
    )

    components = max(
        components,
        2,
    )

    pca = PCA(
        n_components=components
    )

    X_reduced = pca.fit_transform(X)

    explained_variance = (
        pca.explained_variance_ratio_.sum()
        * 100
    )

    return X_reduced, {
        "applied": True,
        "original_dimensions": original_dimensions,
        "reduced_dimensions": components,
        "explained_variance": round(
            float(explained_variance),
            2,
        ),
    }


def reduce_to_2d(X):
    """
    Create a 2D PCA projection for visualization.
    """

    pca = PCA(
        n_components=2
    )

    points = pca.fit_transform(X)

    return points, {
        "pc1": round(
            float(
                pca.explained_variance_ratio_[0]
                * 100
            ),
            2,
        ),
        "pc2": round(
            float(
                pca.explained_variance_ratio_[1]
                * 100
            ),
            2,
        ),
    }