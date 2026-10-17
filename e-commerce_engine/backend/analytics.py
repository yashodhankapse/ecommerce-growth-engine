import pandas as pd


def load_dataset(file_path):
    filename = str(file_path).lower()

    if filename.endswith(".csv"):
        return pd.read_csv(file_path)

    if filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(file_path)

    raise ValueError("Unsupported file format.")


def analyze_dataset(df):
    numeric_columns = (
        df.select_dtypes(include="number")
        .columns.tolist()
    )

    categorical_columns = (
        df.select_dtypes(
            include=["object", "category", "bool"]
        )
        .columns.tolist()
    )

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing": int(df.isna().sum().sum()),
        "duplicates": int(df.duplicated().sum()),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "missing_by_column": df.isna().sum().to_dict()
    }


def generate_report(df, filename):
    stats = analyze_dataset(df)

    lines = [
        f"Dataset: {filename}",
        f"Total records: {stats['rows']}",
        f"Total columns: {stats['columns']}",
        f"Missing values: {stats['missing']}",
        f"Duplicate rows: {stats['duplicates']}",
        "",
        "Numeric Column Analysis:"
    ]

    if stats["numeric_columns"]:
        for column in stats["numeric_columns"]:
            lines.append(
                f"{column}: "
                f"Average = {df[column].mean():.2f}, "
                f"Maximum = {df[column].max()}"
            )
    else:
        lines.append("No numeric columns found.")

    return "\n".join(lines)