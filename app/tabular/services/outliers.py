import pandas as pd


def _is_id_column(column: str) -> bool:
    """
    Detect identifier-like columns.

    IDs should not be treated as numerical measurements
    because their large/small values have no meaningful
    statistical interpretation.
    """

    name = column.upper()

    return (
        name.startswith("SK_ID")
        or name == "ID"
        or name.endswith("_ID")
        or name.endswith("_IDENTIFIER")
    )


def _is_discrete_column(series: pd.Series) -> bool:
    """
    Detect numerical variables that behave more like
    categorical/count variables than continuous measurements.
    """

    unique_values = series.nunique(dropna=True)

    # Binary / very small categorical domains
    if unique_values <= 10:
        return True

    # Small integer domains
    if pd.api.types.is_integer_dtype(series):
        if unique_values <= 25:
            return True

    return False


def _get_severity(
    outlier_percentage: float,
    skewness: float
) -> str:
    """
    Determine severity using both:
    1. How many observations are statistical extremes
    2. How strongly the distribution is skewed
    """

    absolute_skew = abs(skewness)

    # Extremely large statistical burden
    if outlier_percentage >= 15:
        return "critical"

    # Strongly skewed distributions can be problematic
    # even when the number of IQR outliers is relatively small.
    if absolute_skew >= 10:
        return "high"

    if outlier_percentage >= 5:
        return "high"

    if absolute_skew >= 5:
        return "high"

    if outlier_percentage >= 1:
        return "medium"

    if absolute_skew >= 2:
        return "medium"

    return "low"


def _get_interpretation(
    outlier_percentage: float,
    skewness: float
) -> str:
    """
    Generate a human-readable interpretation of the
    statistical finding.
    """

    absolute_skew = abs(skewness)

    if outlier_percentage < 1:
        return (
            "A small number of observations fall outside the "
            "typical IQR range. These may be legitimate extremes."
        )

    if absolute_skew >= 2:
        return (
            "The feature is strongly skewed and contains statistical "
            "extremes. These values may represent a legitimate long tail "
            "rather than data errors."
        )

    if absolute_skew >= 1:
        return (
            "The feature is moderately skewed and contains values outside "
            "the typical range. Review the distribution before modeling."
        )

    if outlier_percentage >= 15:
        return (
            "A substantial portion of observations fall outside the "
            "typical IQR range. The feature should be investigated carefully."
        )

    return (
        "Some observations fall outside the typical IQR range. "
        "Review extreme values before deciding whether treatment is needed."
    )


def detect_outliers(df):

    numeric_df = df.select_dtypes(
        include="number"
    )

    results = {}

    for column in numeric_df.columns:

        # -------------------------------------------------
        # 1. Ignore identifiers
        # -------------------------------------------------

        if _is_id_column(column):
            continue

        series = numeric_df[column].dropna()

        if len(series) == 0:
            continue

        # -------------------------------------------------
        # 2. Ignore discrete / categorical-like variables
        # -------------------------------------------------

        if _is_discrete_column(series):
            continue

        # -------------------------------------------------
        # 3. Calculate quartiles
        # -------------------------------------------------

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        # If all useful values are effectively identical,
        # there is no meaningful IQR-based outlier detection.
        if iqr == 0:
            continue

        # -------------------------------------------------
        # 4. Calculate IQR boundaries
        # -------------------------------------------------

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # -------------------------------------------------
        # 5. Detect outliers
        # -------------------------------------------------

        mask = (
            (series < lower_bound)
            | (series > upper_bound)
        )

        outlier_count = int(mask.sum())

        outlier_percentage = (
            outlier_count / len(series)
        ) * 100

        # No statistical outliers were found.
        # Do not include the column in the findings.
        if outlier_count == 0:
            continue

        # -------------------------------------------------
        # 6. Distribution information
        # -------------------------------------------------

        skewness = float(series.skew())

        severity = _get_severity(
            outlier_percentage,
            skewness
        )

        interpretation = _get_interpretation(
            outlier_percentage,
            skewness
        )

        # -------------------------------------------------
        # 7. Store detailed result
        # -------------------------------------------------

        results[column] = {

            "method": "IQR",

            "outlier_count":
                outlier_count,

            "outlier_percentage":
                round(
                    outlier_percentage,
                    2
                ),

            "severity":
                severity,

            "q1":
                round(
                    float(q1),
                    4
                ),

            "q3":
                round(
                    float(q3),
                    4
                ),

            "iqr":
                round(
                    float(iqr),
                    4
                ),

            "lower_bound":
                round(
                    float(lower_bound),
                    4
                ),

            "upper_bound":
                round(
                    float(upper_bound),
                    4
                ),

            "skewness":
                round(
                    skewness,
                    4
                ),

            "interpretation":
                interpretation
        }

    return results