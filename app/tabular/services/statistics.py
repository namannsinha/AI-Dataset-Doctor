import pandas as pd


def calculate_statistics(df):

    numeric_df = df.select_dtypes(include="number")

    statistics = {}

    for column in numeric_df.columns:

        series = numeric_df[column]

        statistics[column] = {
            "mean": round(float(series.mean()), 4),
            "median": round(float(series.median()), 4),
            "std": round(float(series.std()), 4),
            "min": round(float(series.min()), 4),
            "max": round(float(series.max()), 4),
            "q1": round(float(series.quantile(0.25)), 4),
            "q3": round(float(series.quantile(0.75)), 4)
        }

    return statistics