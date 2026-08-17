def calculate_ml_readiness(
    original_df,
    treated_df,
    treatment_report,
    preprocessing_info=None
):
    """
    Evaluate ML readiness of the treated dataset.
    """

    checks = []

    # ---------------------------------------------------------
    # 1. Missing values
    # ---------------------------------------------------------

    missing_cells = int(
        treated_df.isna().sum().sum()
    )

    if missing_cells == 0:
        checks.append({
            "name": "Missing values",
            "status": "passed",
            "message": "No missing values remain."
        })
    else:
        checks.append({
            "name": "Missing values",
            "status": "failed",
            "message": f"{missing_cells:,} missing values remain."
        })

    # ---------------------------------------------------------
    # 2. Infinite values
    # ---------------------------------------------------------

    numeric_df = treated_df.select_dtypes(
        include="number"
    )

    infinite_values = int(
        numeric_df.isin(
            [float("inf"), float("-inf")]
        ).sum().sum()
    )

    if infinite_values == 0:
        checks.append({
            "name": "Infinite values",
            "status": "passed",
            "message": "No infinite values detected."
        })
    else:
        checks.append({
            "name": "Infinite values",
            "status": "failed",
            "message": f"{infinite_values:,} infinite values detected."
        })

    # ---------------------------------------------------------
    # 3. Duplicate rows
    # ---------------------------------------------------------

    duplicate_rows = int(
        treated_df.duplicated().sum()
    )

    if duplicate_rows == 0:
        checks.append({
            "name": "Duplicate rows",
            "status": "passed",
            "message": "No duplicate rows remain."
        })
    else:
        checks.append({
            "name": "Duplicate rows",
            "status": "warning",
            "message": f"{duplicate_rows:,} duplicate rows remain."
        })

    # ---------------------------------------------------------
    # 4. Constant features
    # ---------------------------------------------------------

    constant_columns = [
        column
        for column in treated_df.columns
        if treated_df[column].nunique(
            dropna=False
        ) <= 1
    ]

    if not constant_columns:
        checks.append({
            "name": "Constant features",
            "status": "passed",
            "message": "No constant features remain."
        })
    else:
        checks.append({
            "name": "Constant features",
            "status": "warning",
            "message": (
                f"{len(constant_columns)} constant "
                "features remain."
            )
        })

    # ---------------------------------------------------------
    # 5. Categorical compatibility
    # ---------------------------------------------------------

    categorical_columns = treated_df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    if not categorical_columns:
        checks.append({
            "name": "Feature encoding",
            "status": "passed",
            "message": "All features have numerical representation."
        })
    else:
        checks.append({
            "name": "Feature encoding",
            "status": "warning",
            "message": (
                f"{len(categorical_columns)} categorical "
                "features remain."
            )
        })

    # ---------------------------------------------------------
    # 6. Feature count
    # ---------------------------------------------------------

    feature_count = treated_df.shape[1]

    if feature_count == 0:
        feature_status = "failed"
        feature_message = "No usable features remain."
    elif feature_count <= 500:
        feature_status = "passed"
        feature_message = (
            f"{feature_count} features available."
        )
    else:
        feature_status = "warning"
        feature_message = (
            f"{feature_count} features available; "
            "dimensionality may require reduction."
        )

    checks.append({
        "name": "Feature dimensionality",
        "status": feature_status,
        "message": feature_message
    })

    # ---------------------------------------------------------
    # 7. Sample / feature ratio
    # ---------------------------------------------------------

    rows = treated_df.shape[0]

    ratio = (
        rows / feature_count
        if feature_count > 0
        else 0
    )

    if ratio >= 100:
        ratio_status = "passed"
    elif ratio >= 20:
        ratio_status = "warning"
    else:
        ratio_status = "failed"

    checks.append({
        "name": "Samples per feature",
        "status": ratio_status,
        "message": (
            f"{rows:,} samples / "
            f"{feature_count:,} features = "
            f"{ratio:.2f}"
        )
    })

    # ---------------------------------------------------------
    # 8. Row integrity
    # ---------------------------------------------------------

    original_rows = len(original_df)
    treated_rows = len(treated_df)

    if original_rows == treated_rows:
        row_status = "passed"
        row_message = "No rows were lost during treatment."
    else:
        row_status = "warning"
        row_message = (
            f"Rows changed from "
            f"{original_rows:,} to "
            f"{treated_rows:,}."
        )

    checks.append({
        "name": "Row integrity",
        "status": row_status,
        "message": row_message
    })

    # ---------------------------------------------------------
    # Score
    # ---------------------------------------------------------

    score = 100

    penalties = {
        "missing_values": 25,
        "infinite_values": 20,
        "duplicates": 10,
        "constant_features": 10,
        "categorical_features": 10,
        "dimensionality": 10,
        "sample_feature_ratio": 10,
        "row_integrity": 5
    }

    if missing_cells > 0:
        score -= penalties["missing_values"]

    if infinite_values > 0:
        score -= penalties["infinite_values"]

    if duplicate_rows > 0:
        score -= penalties["duplicates"]

    if constant_columns:
        score -= penalties["constant_features"]

    if categorical_columns:
        score -= penalties["categorical_features"]

    if feature_count > 500:
        score -= penalties["dimensionality"]

    if ratio < 20:
        score -= penalties["sample_feature_ratio"]
    elif ratio < 100:
        score -= 5

    if original_rows != treated_rows:
        score -= penalties["row_integrity"]

    score = max(
        0,
        min(
            100,
            int(round(score))
        )
    )

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    if score >= 90:
        status = "ready"
    elif score >= 75:
        status = "mostly_ready"
    elif score >= 50:
        status = "needs_attention"
    else:
        status = "not_ready"

    # ---------------------------------------------------------
    # Treatment history
    # ---------------------------------------------------------

    original_columns = original_df.shape[1]
    treated_columns = treated_df.shape[1]

    values_imputed = (
        treatment_report.get(
            "numeric_values_imputed",
            0
        )
        +
        treatment_report.get(
            "categorical_values_filled",
            0
        )
    )

    return {
        "score": score,
        "status": status,

        "checks": checks,

        "original_shape": {
            "rows": int(original_rows),
            "columns": int(original_columns)
        },

        "treated_shape": {
            "rows": int(treated_rows),
            "columns": int(treated_columns)
        },

        "dataset_metrics": {
            "feature_count": int(feature_count),
            "numeric_features": int(
                len(numeric_df.columns)
            ),
            "categorical_features": int(
                len(categorical_columns)
            ),
            "samples_per_feature": round(
                ratio,
                2
            )
        },

        "treatment_history": {
            "values_imputed": int(values_imputed),
            "duplicates_removed": int(
                treatment_report.get(
                    "duplicates_removed",
                    0
                )
            ),
            "constant_columns_removed": len(
                treatment_report.get(
                    "constant_columns_removed",
                    []
                )
            ),
            "ordinal_columns_encoded": len(
                treatment_report.get(
                    "ordinal_columns_encoded",
                    []
                )
            ),
            "nominal_columns_encoded": int(
                treatment_report.get(
                    "nominal_columns_encoded",
                    0
                )
            ),
            "features_added": int(
                treated_columns - original_columns
            )
        }
    }