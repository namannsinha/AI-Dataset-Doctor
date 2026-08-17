def generate_recommendations(
    df,
    quality,
    outliers
):

    recommendations = []

    # =====================================================
    # MISSING VALUES
    # =====================================================

    for item in quality["missing_values"]:

        percentage = item["missing_percentage"]
        column = item["column"]

        if percentage == 0:
            continue

        if percentage >= 50:

            recommendations.append({
                "severity": "high",
                "column": column,
                "problem": "Very high missing values",
                "recommendation":
                    "Consider dropping this column or using a more advanced imputation strategy."
            })

        elif percentage >= 10:

            recommendations.append({
                "severity": "medium",
                "column": column,
                "problem": "Significant missing values",
                "recommendation":
                    "Consider median/mode imputation or investigate why values are missing."
            })

        else:

            recommendations.append({
                "severity": "low",
                "column": column,
                "problem": "Missing values detected",
                "recommendation":
                    "Consider imputing the missing values before modeling."
            })

    # =====================================================
    # DUPLICATES
    # =====================================================

    if quality["duplicate_rows"] > 0:

        recommendations.append({
            "severity": "medium",
            "column": None,
            "problem": "Duplicate rows detected",
            "recommendation":
                "Review duplicate records and remove them if they represent repeated observations."
        })

    # =====================================================
    # CONSTANT COLUMNS
    # =====================================================

    for column in quality["constant_columns"]:

        recommendations.append({
            "severity": "medium",
            "column": column,
            "problem": "Constant column",
            "recommendation":
                "Consider removing this column because it provides little predictive information."
        })

    # =====================================================
    # OUTLIERS
    # =====================================================

    for column, result in outliers.items():

        percentage = result["outlier_percentage"]
        severity = result["severity"]

        # Very small amount of statistical extremes
        # should not become a scary diagnosis.
        if percentage < 1:
            continue

        # Strongly skewed features
        if abs(result["skewness"]) >= 2:

            recommendations.append({
                "severity": severity,
                "column": column,
                "problem": "Skewed distribution with extreme values",
                "recommendation":
                    "Review the feature distribution. Consider robust scaling or controlled clipping rather than automatically removing these observations."
            })

        elif percentage >= 15:

            recommendations.append({
                "severity": "high",
                "column": column,
                "problem": "Large proportion of statistical extremes",
                "recommendation":
                    "Investigate this feature carefully. Consider robust preprocessing or controlled clipping before model training."
            })

        elif percentage >= 5:

            recommendations.append({
                "severity": "medium",
                "column": column,
                "problem": "Statistical extremes detected",
                "recommendation":
                    "Review extreme values before modeling. Robust scaling or controlled clipping may be appropriate."
            })

        else:

            recommendations.append({
                "severity": "low",
                "column": column,
                "problem": "Some statistical extremes detected",
                "recommendation":
                    "Review the feature distribution. These values may be legitimate and do not necessarily require removal."
            })

    return recommendations