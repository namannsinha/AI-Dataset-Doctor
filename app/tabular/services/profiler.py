import pandas as pd


def load_dataset(file_path: str):
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)

    elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        df = pd.read_excel(file_path)

    else:
        raise ValueError("Only CSV and Excel files are supported.")

    return df


def get_basic_profile(df):
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "memory_usage_mb": round(
            df.memory_usage(deep=True).sum() / (1024 * 1024), 2
        )
    }