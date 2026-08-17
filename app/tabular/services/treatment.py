from pathlib import Path

import numpy as np
import pandas as pd

from app.tabular.services.preprocessing import (
    detect_feature_types,
    ORDINAL_MAPPINGS,
)


def treat_dataset(
    df: pd.DataFrame,
    output_path: str | Path,
    remove_duplicates: bool = True,
    remove_constant_columns: bool = True,
    clip_outliers: bool = False,
):
    """
    Apply recommended data-quality treatments to a dataset.

    Returns:
        treated_df
        treatment_report
    """

    df = df.copy()

    original_shape = df.shape

    actions = []

    # ---------------------------------------------------------
    # 1. Remove duplicate rows
    # ---------------------------------------------------------

    duplicates_removed = 0

    if remove_duplicates:

        duplicate_mask = df.duplicated()

        duplicates_removed = int(
            duplicate_mask.sum()
        )

        if duplicates_removed > 0:

            df = df.loc[
                ~duplicate_mask
            ].copy()

            actions.append({
                "action": "duplicate_removal",
                "rows_affected": duplicates_removed,
                "description": (
                    f"Removed {duplicates_removed:,} duplicate rows."
                ),
            })

    # ---------------------------------------------------------
    # 2. Detect feature types
    # ---------------------------------------------------------

    feature_types = detect_feature_types(df)

    numeric_columns = feature_types["numeric"]
    ordinal_columns = feature_types["ordinal"]
    nominal_columns = feature_types["nominal"]

    # ---------------------------------------------------------
    # 3. Missing numerical values
    # ---------------------------------------------------------

    numeric_missing_before = int(
        df[numeric_columns]
        .isna()
        .sum()
        .sum()
    ) if numeric_columns else 0

    numeric_imputed = 0

    for column in numeric_columns:

        missing_count = int(
            df[column].isna().sum()
        )

        if missing_count == 0:
            continue

        median = df[column].median()

        # If an entire column is missing, use 0
        # rather than leaving NaNs behind.
        if pd.isna(median):
            median = 0

        df[column] = df[column].fillna(median)

        numeric_imputed += missing_count

    if numeric_imputed > 0:

        actions.append({
            "action": "numeric_imputation",
            "columns_affected": len([
                c for c in numeric_columns
                if df[c].isna().sum() == 0
            ]),
            "values_affected": numeric_imputed,
            "method": "median",
            "description": (
                f"Filled {numeric_imputed:,} missing "
                "numeric values using column medians."
            ),
        })

    # ---------------------------------------------------------
    # 4. Missing categorical values
    # ---------------------------------------------------------

    categorical_columns = (
        ordinal_columns +
        nominal_columns
    )

    categorical_missing = 0

    for column in categorical_columns:

        missing_count = int(
            df[column].isna().sum()
        )

        if missing_count == 0:
            continue

        df[column] = df[column].fillna(
            "Missing"
        )

        categorical_missing += missing_count

    if categorical_missing > 0:

        actions.append({
            "action": "categorical_imputation",
            "columns_affected": len([
                c for c in categorical_columns
                if c in df.columns
            ]),
            "values_affected": categorical_missing,
            "method": "Missing category",
            "description": (
                f"Filled {categorical_missing:,} missing "
                "categorical values with 'Missing'."
            ),
        })

    # ---------------------------------------------------------
    # 5. Ordinal encoding
    # ---------------------------------------------------------

    ordinal_encoded = []

    for column in ordinal_columns:

        if column not in df.columns:
            continue

        mapping = ORDINAL_MAPPINGS.get(
            column,
            {}
        )

        if not mapping:
            continue

        df[column] = (
            df[column]
            .map(mapping)
        )

        # Unknown/unmapped values become NaN.
        # Fill them with the median ordinal value.
        median = df[column].median()

        if pd.isna(median):
            median = 0

        df[column] = (
            df[column]
            .fillna(median)
        )

        ordinal_encoded.append(column)

    if ordinal_encoded:

        actions.append({
            "action": "ordinal_encoding",
            "columns": ordinal_encoded,
            "method": "Ordinal encoding",
            "description": (
                f"Encoded {len(ordinal_encoded)} ordinal "
                "feature(s) while preserving their order."
            ),
        })

    # ---------------------------------------------------------
    # 6. One-hot encoding nominal columns
    # ---------------------------------------------------------

    nominal_before = len(nominal_columns)

    if nominal_columns:

        existing_nominal = [
            c for c in nominal_columns
            if c in df.columns
        ]

        if existing_nominal:

            df = pd.get_dummies(
                df,
                columns=existing_nominal,
                dtype=int,
            )

            actions.append({
                "action": "one_hot_encoding",
                "columns_affected": len(existing_nominal),
                "method": "One-hot encoding",
                "description": (
                    f"One-hot encoded {len(existing_nominal)} "
                    "nominal feature(s)."
                ),
            })

    # ---------------------------------------------------------
    # 7. Remove constant columns
    # ---------------------------------------------------------

    constant_columns = []

    if remove_constant_columns:

        for column in df.columns:

            if df[column].nunique(
                dropna=False
            ) <= 1:

                constant_columns.append(
                    column
                )

        if constant_columns:

            df = df.drop(
                columns=constant_columns
            )

            actions.append({
                "action": "constant_column_removal",
                "columns": constant_columns,
                "description": (
                    f"Removed {len(constant_columns)} "
                    "constant column(s)."
                ),
            })

    # ---------------------------------------------------------
    # 8. Optional IQR outlier clipping
    # ---------------------------------------------------------

    clipped_columns = []
    clipped_values = 0

    if clip_outliers:

        # Only process numeric columns that
        # still exist after transformations.
        current_numeric = df.select_dtypes(
            include=["number"]
        ).columns.tolist()

        for column in current_numeric:

            series = df[column]

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)

            iqr = q3 - q1

            if pd.isna(iqr) or iqr == 0:
                continue

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            mask = (
                (series < lower)
                | (series > upper)
            )

            affected = int(mask.sum())

            if affected == 0:
                continue

            df[column] = series.clip(
                lower,
                upper
            )

            clipped_columns.append(column)
            clipped_values += affected

        if clipped_values:

            actions.append({
                "action": "outlier_clipping",
                "columns": clipped_columns,
                "values_affected": clipped_values,
                "method": "IQR clipping",
                "description": (
                    f"Capped {clipped_values:,} "
                    "extreme values using the IQR rule."
                ),
            })

    # ---------------------------------------------------------
    # 9. Final cleanup
    # ---------------------------------------------------------

    # Convert boolean columns generated by some
    # pandas versions into integers.
    boolean_columns = df.select_dtypes(
        include=["bool"]
    ).columns

    for column in boolean_columns:
        df[column] = df[column].astype(int)

    # Any remaining numeric NaNs are filled with zero.
    # This is a final safety net.
    remaining_missing = int(
        df.isna().sum().sum()
    )

    if remaining_missing > 0:

        numeric_remaining = df.select_dtypes(
            include=["number"]
        ).columns

        for column in numeric_remaining:

            df[column] = df[column].fillna(
                df[column].median()
                if not pd.isna(df[column].median())
                else 0
            )

        categorical_remaining = df.select_dtypes(
            include=["object", "category"]
        ).columns

        for column in categorical_remaining:

            df[column] = df[column].fillna(
                "Missing"
            )

    # ---------------------------------------------------------
    # 10. Save treated dataset
    # ---------------------------------------------------------

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_path,
        index=False
    )

    # ---------------------------------------------------------
    # Treatment report
    # ---------------------------------------------------------

    report = {
        "status": "success",
        "original_rows": int(
            original_shape[0]
        ),
        "original_columns": int(
            original_shape[1]
        ),
        "treated_rows": int(
            df.shape[0]
        ),
        "treated_columns": int(
            df.shape[1]
        ),
        "duplicates_removed": duplicates_removed,
        "numeric_values_imputed": numeric_imputed,
        "categorical_values_filled": categorical_missing,
        "ordinal_columns_encoded": ordinal_encoded,
        "nominal_columns_encoded": nominal_before,
        "constant_columns_removed": constant_columns,
        "outlier_values_clipped": clipped_values,
        "remaining_missing_values": int(
            df.isna().sum().sum()
        ),
        "actions": actions,
        "output_path": str(output_path),
    }

    return df, report