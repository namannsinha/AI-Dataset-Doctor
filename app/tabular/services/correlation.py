import pandas as pd


def calculate_correlations(df):

    numeric_df = df.select_dtypes(
        include="number"
    )

    if numeric_df.shape[1] < 2:
        return {
            "message": "At least two numerical columns are required."
        }

    correlation_matrix = numeric_df.corr()

    correlations = []

    columns = correlation_matrix.columns

    for i in range(len(columns)):

        for j in range(i + 1, len(columns)):

            column_a = columns[i]
            column_b = columns[j]

            value = correlation_matrix.iloc[i, j]

            if pd.isna(value):
                continue

            correlations.append({
                "feature_1": column_a,
                "feature_2": column_b,
                "correlation": round(
                    float(value),
                    4
                ),
                "strength": get_strength(
                    abs(value)
                )
            })

    correlations.sort(
        key=lambda x: abs(x["correlation"]),
        reverse=True
    )

    return {
        "features": columns.tolist(),
        "correlations": correlations
    }


def get_strength(value):

    if value >= 0.8:
        return "very strong"

    if value >= 0.6:
        return "strong"

    if value >= 0.4:
        return "moderate"

    if value >= 0.2:
        return "weak"

    return "very weak"