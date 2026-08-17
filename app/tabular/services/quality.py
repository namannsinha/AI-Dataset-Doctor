def analyze_quality(df):

    missing = df.isnull().sum()

    missing_data = []

    for column in df.columns:
        count = int(missing[column])

        missing_data.append({
            "column": column,
            "missing_count": count,
            "missing_percentage": round(
                (count / len(df)) * 100,
                2
            )
        })

    # -------------------------------------------------
    # Duplicate rows
    # -------------------------------------------------

    duplicate_count = int(
        df.duplicated().sum()
    )

    # -------------------------------------------------
    # Data types
    # -------------------------------------------------

    data_types = []

    for column in df.columns:
        data_types.append({
            "column": column,
            "dtype": str(df[column].dtype),
            "unique_values": int(
                df[column].nunique()
            )
        })

    # -------------------------------------------------
    # Constant columns
    # -------------------------------------------------

    constant_columns = [
        column
        for column in df.columns
        if df[column].nunique(
            dropna=False
        ) <= 1
    ]

    # -------------------------------------------------
    # Near-constant columns
    # -------------------------------------------------

    near_constant_columns = []

    for column in df.columns:

        if len(df) == 0:
            continue

        value_counts = (
            df[column]
            .value_counts(
                dropna=False,
                normalize=True
            )
        )

        if len(value_counts) > 1:

            dominant_percentage = (
                float(value_counts.iloc[0]) * 100
            )

            if dominant_percentage >= 99:
                near_constant_columns.append({
                    "column": column,
                    "dominant_percentage": round(
                        dominant_percentage,
                        2
                    )
                })

    # -------------------------------------------------
    # High-cardinality categorical columns
    # -------------------------------------------------

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns

    high_cardinality_columns = []

    for column in categorical_columns:

        unique_count = int(
            df[column].nunique(dropna=True)
        )

        if len(df) > 0:

            unique_ratio = (
                unique_count / len(df)
            )

            if unique_ratio >= 0.5:
                high_cardinality_columns.append({
                    "column": column,
                    "unique_values": unique_count,
                    "unique_ratio": round(
                        unique_ratio * 100,
                        2
                    )
                })

    # -------------------------------------------------
    # Infinite values
    # -------------------------------------------------

    numeric_df = df.select_dtypes(
        include="number"
    )

    infinite_values = int(
        numeric_df.isin(
            [float("inf"), float("-inf")]
        ).sum().sum()
    )

    # -------------------------------------------------
    # Highly skewed numerical columns
    # -------------------------------------------------

    highly_skewed_columns = []

    for column in numeric_df.columns:

        series = numeric_df[column].dropna()

        if len(series) < 3:
            continue

        skewness = float(series.skew())

        if abs(skewness) >= 2:
            highly_skewed_columns.append({
                "column": column,
                "skewness": round(
                    skewness,
                    4
                )
            })

    # -------------------------------------------------
    # Dataset-level missing statistics
    # -------------------------------------------------

    total_missing = int(
        df.isnull().sum().sum()
    )

    total_cells = (
        len(df) * len(df.columns)
    )

    missing_ratio = (
        total_missing / total_cells
        if total_cells > 0
        else 0
    )

    # -------------------------------------------------
    # Return
    # -------------------------------------------------

    return {

        "missing_values":
            missing_data,

        "total_missing_values":
            total_missing,

        "missing_ratio":
            round(
                missing_ratio * 100,
                2
            ),

        "duplicate_rows":
            duplicate_count,

        "duplicate_percentage":
            round(
                (duplicate_count / len(df)) * 100,
                2
            ) if len(df) > 0 else 0,

        "data_types":
            data_types,

        "constant_columns":
            constant_columns,

        "near_constant_columns":
            near_constant_columns,

        "high_cardinality_columns":
            high_cardinality_columns,

        "infinite_values":
            infinite_values,

        "highly_skewed_columns":
            highly_skewed_columns
    }

# =========================================================
# HEALTH SCORE HELPERS
# =========================================================

def _calculate_outlier_penalty(outliers):
    """
    Calculate statistical-risk penalty.

    Outliers are not automatically considered bad data.

    The penalty depends on:

    1. Percentage of observations affected
    2. Severity of the detected outliers

    Maximum penalty = 10 points.
    """

    if not outliers:
        return 0.0

    severity_weights = {
        "low": 0.25,
        "medium": 0.50,
        "high": 0.75,
        "critical": 1.00
    }

    weighted_burden = 0.0
    total_weight = 0.0

    for result in outliers.values():

        percentage = float(
            result.get(
                "outlier_percentage",
                0
            )
        )

        severity = result.get(
            "severity",
            "low"
        )

        weight = severity_weights.get(
            severity,
            0.25
        )

        # 20% affected = maximum normalized burden
        burden = min(
            percentage / 20.0,
            1.0
        )

        weighted_burden += (
            burden * weight
        )

        total_weight += weight

    if total_weight == 0:
        return 0.0

    average_burden = (
        weighted_burden /
        total_weight
    )

    penalty = average_burden * 10

    return min(
        penalty,
        10.0
    )


# =========================================================
# HEALTH SCORE COMPONENTS
# =========================================================

def calculate_health_score_components(
    quality,
    outliers
):
    """
    Calculate every component of the health score.

    This is the single source of truth for the scoring
    system. Both calculate_health_score() and the API
    breakdown use these exact values.
    """

    # =====================================================
    # 1. COMPLETENESS
    # Maximum penalty: 35
    # =====================================================

    missing_percentage = float(
        quality.get(
            "missing_ratio",
            0
        )
    )

    missing_penalty = min(
        missing_percentage,
        35
    )

    # =====================================================
    # 2. DATA INTEGRITY
    # Maximum penalty: 15
    # =====================================================

    duplicate_percentage = float(
        quality.get(
            "duplicate_percentage",
            0
        )
    )

    duplicate_penalty = min(
        duplicate_percentage * 0.5,
        15
    )

    # =====================================================
    # 3. STRUCTURAL QUALITY
    # Maximum penalty: 10
    # =====================================================

    constant_count = len(
        quality.get(
            "constant_columns",
            []
        )
    )

    total_columns = max(
        len(
            quality.get(
                "data_types",
                []
            )
        ),
        1
    )

    constant_ratio = (
        constant_count /
        total_columns
    )

    constant_penalty = min(
        constant_ratio * 100,
        10
    )

    # =====================================================
    # 4. STATISTICAL RISK
    # Maximum penalty: 10
    # =====================================================

    outlier_penalty = (
        _calculate_outlier_penalty(
            outliers
        )
    )

    # =====================================================
    # TOTAL
    # =====================================================

    total_penalty = (
        missing_penalty
        + duplicate_penalty
        + constant_penalty
        + outlier_penalty
    )

    score = max(
        0,
        min(
            100,
            round(
                100 - total_penalty
            )
        )
    )

    return {
        "score": score,

        "penalties": {
            "missing": round(
                missing_penalty,
                2
            ),

            "duplicates": round(
                duplicate_penalty,
                2
            ),

            "constant_columns": round(
                constant_penalty,
                2
            ),

            "outliers": round(
                outlier_penalty,
                2
            )
        },

        "maximum_penalties": {
            "missing": 35,
            "duplicates": 15,
            "constant_columns": 10,
            "outliers": 10
        }
    }


# =========================================================
# HEALTH SCORE
# =========================================================

def calculate_health_score(
    quality,
    outliers
):

    components = (
        calculate_health_score_components(
            quality,
            outliers
        )
    )

    return components["score"]


# =========================================================
# EXPLAINABLE HEALTH BREAKDOWN
# =========================================================

def get_health_score_breakdown(
    quality,
    outliers
):
    """
    Return a frontend-friendly explanation of the score.
    """

    components = (
        calculate_health_score_components(
            quality,
            outliers
        )
    )

    penalties = components["penalties"]

    # -----------------------------------------------------
    # Convert penalty into component health score
    # -----------------------------------------------------

    completeness_score = round(
        35 - penalties["missing"],
        2
    )

    integrity_score = round(
        15 - penalties["duplicates"],
        2
    )

    structure_score = round(
        10 - penalties["constant_columns"],
        2
    )

    statistical_score = round(
        10 - penalties["outliers"],
        2
    )

    # -----------------------------------------------------
    # Human-readable status
    # -----------------------------------------------------

    score = components["score"]

    if score >= 90:
        status = "excellent"
        message = (
            "The dataset is in excellent condition "
            "with only minor statistical concerns."
        )

    elif score >= 75:
        status = "good"
        message = (
            "The dataset is in good condition, "
            "but some issues should be reviewed before modeling."
        )

    elif score >= 50:
        status = "needs_attention"
        message = (
            "The dataset has several quality issues "
            "that should be addressed before modeling."
        )

    else:
        status = "critical"
        message = (
            "The dataset requires significant cleaning "
            "before it should be used for modeling."
        )

    return {

        "score": score,

        "status": status,

        "message": message,

        "components": {

            "completeness": {
                "score": completeness_score,
                "maximum": 35,
                "penalty": penalties["missing"],
                "maximum_penalty": 35
            },

            "integrity": {
                "score": integrity_score,
                "maximum": 15,
                "penalty": penalties["duplicates"],
                "maximum_penalty": 15
            },

            "structure": {
                "score": structure_score,
                "maximum": 10,
                "penalty": penalties["constant_columns"],
                "maximum_penalty": 10
            },

            "statistical_risk": {
                "score": statistical_score,
                "maximum": 10,
                "penalty": penalties["outliers"],
                "maximum_penalty": 10,
                "outlier_columns": len(outliers)
            }
        },

        "penalties": penalties
    }