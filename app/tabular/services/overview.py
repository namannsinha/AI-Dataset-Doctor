import pandas as pd

from app.tabular.services.profiler import (
    get_basic_profile
)

from app.tabular.services.quality import (
    analyze_quality,
    calculate_health_score,
    get_health_score_breakdown
)

from app.tabular.services.statistics import (
    calculate_statistics
)

from app.tabular.services.outliers import (
    detect_outliers
)

from app.tabular.services.recommendations import (
    generate_recommendations
)

from app.tabular.services.correlation import (
    calculate_correlations
)

from app.tabular.services.clustering import (
    perform_clustering
)

from app.tabular.services.preprocessing import (
    detect_feature_types
)


def generate_overview(df, n_clusters=3):

    # -----------------------------
    # Basic profile
    # -----------------------------

    profile = get_basic_profile(df)

    # -----------------------------
    # Quality
    # -----------------------------

    # -----------------------------
    # Feature type detection
    # -----------------------------

    feature_types = detect_feature_types(df)

    feature_summary = {
        "numeric_count": len(
            feature_types["numeric"]
        ),
        "ordinal_count": len(
            feature_types["ordinal"]
        ),
        "nominal_count": len(
            feature_types["nominal"]
        ),
        "numeric_columns": feature_types["numeric"],
        "ordinal_columns": feature_types["ordinal"],
        "nominal_columns": feature_types["nominal"]
    }


    quality = analyze_quality(df)

    # -----------------------------
    # Statistics
    # -----------------------------

    statistics = calculate_statistics(df)

    # -----------------------------
    # Outliers
    # -----------------------------

    outliers = detect_outliers(df)

    # -----------------------------
    # Recommendations
    # -----------------------------

    recommendations = generate_recommendations(
        df,
        quality,
        outliers
    )

    # -----------------------------
    # Health score
    # -----------------------------

    # -----------------------------
    # Treatment prescription
    # -----------------------------

    treatment_prescription = []

    total_missing = int(
        df.isna().sum().sum()
    )

    if total_missing > 0:

        treatment_prescription.append({
            "action": "missing_value_imputation",
            "status": "recommended",
            "description": (
                f"{total_missing:,} missing values "
                "should be treated."
            )
        })

    if feature_types["ordinal"]:

        treatment_prescription.append({
            "action": "ordinal_encoding",
            "status": "recommended",
            "columns": feature_types["ordinal"],
            "description": (
                "Ordinal features should be encoded "
                "while preserving their natural ordering."
            )
        })

    if feature_types["nominal"]:

        treatment_prescription.append({
            "action": "one_hot_encoding",
            "status": "recommended",
            "columns": feature_types["nominal"],
            "description": (
                "Nominal categorical features can be "
                "converted using one-hot encoding."
            )
        })

    constant_columns = [
        column
        for column in df.columns
        if df[column].nunique(
            dropna=False
        ) <= 1
    ]

    if constant_columns:

        treatment_prescription.append({
            "action": "constant_column_removal",
            "status": "recommended",
            "columns": constant_columns,
            "description": (
                f"{len(constant_columns)} constant "
                "columns contain no useful variation."
            )
        })

    if not treatment_prescription:

        treatment_prescription.append({
            "action": "no_major_treatment",
            "status": "healthy",
            "description": (
                "No major automatic treatment is required."
            )
        })

    health_score = calculate_health_score(
        quality,
        outliers
    )

    health_breakdown = get_health_score_breakdown(
        quality,
        outliers
    )

    # -----------------------------
    # Correlations
    # -----------------------------

    correlations = calculate_correlations(df)

    # -----------------------------
    # Clustering
    # -----------------------------

    try:

        clustering = perform_clustering(
            df,
            n_clusters
        )

    except ValueError as e:

        clustering = {
            "available": False,
            "message": str(e)
        }

    # -----------------------------
    # Dataset preview
    # -----------------------------

    preview = df.head(10).copy()

    preview = preview.where(
        pd.notnull(preview),
        None
    )

    preview = preview.to_dict(
        orient="records"
    )

    # -----------------------------
    # Final response
    # -----------------------------

    return {

    "dataset": profile,

    "health_score": health_score,

    "health_breakdown": health_breakdown,

    "quality": quality,

    "statistics": statistics,

    "outliers": outliers,

    "correlations": correlations,

    "recommendations": recommendations,

    "feature_types": feature_summary,

    "treatment_prescription":
        treatment_prescription,

    "clustering": clustering,

    "preview": preview
}