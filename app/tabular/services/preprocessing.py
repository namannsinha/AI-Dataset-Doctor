import pandas as pd
import numpy as np

from sklearn.preprocessing import (
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler
)

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer


# ---------------------------------------------------------
# Known ordinal mappings
# ---------------------------------------------------------

ORDINAL_MAPPINGS = {

    "NAME_EDUCATION_TYPE": {
        "Lower secondary": 0,
        "Secondary / secondary special": 1,
        "Incomplete higher": 2,
        "Higher education": 3,
        "Academic degree": 4,
    }

}


# ---------------------------------------------------------
# Detect column types
# ---------------------------------------------------------

def detect_feature_types(df):

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    ordinal_columns = [
        column
        for column in categorical_columns
        if column in ORDINAL_MAPPINGS
    ]

    nominal_columns = [
        column
        for column in categorical_columns
        if column not in ordinal_columns
    ]

    return {
        "numeric": numeric_columns,
        "ordinal": ordinal_columns,
        "nominal": nominal_columns,
    }


# ---------------------------------------------------------
# Apply ordinal encoding
# ---------------------------------------------------------

def apply_ordinal_encoding(df, ordinal_columns):

    result = df.copy()

    for column in ordinal_columns:

        mapping = ORDINAL_MAPPINGS[column]

        result[column] = (
            result[column]
            .map(mapping)
        )

    return result


# ---------------------------------------------------------
# Build ML feature matrix
# ---------------------------------------------------------

def prepare_features(df):

    df = df.copy()

    feature_types = detect_feature_types(df)

    numeric_columns = feature_types["numeric"]
    ordinal_columns = feature_types["ordinal"]
    nominal_columns = feature_types["nominal"]

    # Remove ID-like columns from ML features
    id_columns = []

    for column in numeric_columns:

        unique_ratio = (
            df[column].nunique(dropna=False)
            / max(len(df), 1)
        )

        if (
            unique_ratio > 0.95
            and column.upper().startswith(("SK_ID", "ID"))
        ):
            id_columns.append(column)

    numeric_columns = [
        column
        for column in numeric_columns
        if column not in id_columns
    ]

    # -----------------------------------------------------
    # Numeric pipeline
    # -----------------------------------------------------

    numeric_pipeline = PipelineWrapper(
        SimpleImputer(strategy="median"),
        StandardScaler()
    )

    # -----------------------------------------------------
    # Nominal pipeline
    # -----------------------------------------------------

    nominal_pipeline = PipelineWrapper(
        SimpleImputer(
            strategy="most_frequent"
        ),
        OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=False
        )
    )

    transformers = []

    if numeric_columns:
        transformers.append(
            (
                "numeric",
                numeric_pipeline.pipeline,
                numeric_columns
            )
        )

    if nominal_columns:
        transformers.append(
            (
                "nominal",
                nominal_pipeline.pipeline,
                nominal_columns
            )
        )

    # Ordinal columns are mapped manually,
    # then treated as numerical features.

    df = apply_ordinal_encoding(
        df,
        ordinal_columns
    )

    # Fill ordinal missing values
    for column in ordinal_columns:

        df[column] = df[column].fillna(
            df[column].median()
        )

    if ordinal_columns:

        transformers.append(
            (
                "ordinal",
                StandardScaler(),
                ordinal_columns
            )
        )

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop"
    )

    X = preprocessor.fit_transform(df)

    X = np.asarray(X)

    return X, {
        "numeric_columns": numeric_columns,
        "ordinal_columns": ordinal_columns,
        "nominal_columns": nominal_columns,
        "removed_id_columns": id_columns,
        "feature_count_after_encoding": X.shape[1],
    }


class PipelineWrapper:

    def __init__(self, *steps):

        from sklearn.pipeline import Pipeline

        self.pipeline = Pipeline(
            [
                (
                    f"step_{index}",
                    step
                )
                for index, step in enumerate(steps)
            ]
        )