"""
eda.py
--------------------------------------------------------
Contains all Exploratory Data Analysis (EDA) functions.
Each function returns:


{
    "title": "...",
    "display": ...,
    "json": ...
}
"""


import os


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


from config import FIG_SIZE, DPI, IQR_MULTIPLIER




# ==========================================================
# DATASET LOADING
# ==========================================================


def load_dataset(file):


    """
    Load CSV or Excel dataset.


    Supports:
    1. File path (Titanic/default dataset)
    2. Streamlit uploaded file
    """


    try:


        # ==========================================
        # Case 1: Uploaded Streamlit File
        # ==========================================


        if hasattr(file, "name"):




            filename = file.name.lower()




            if filename.endswith(".csv"):


                df = pd.read_csv(file)




            elif (
                filename.endswith(".xlsx")
                or filename.endswith(".xls")
            ):


                df = pd.read_excel(file)




            else:


                raise ValueError(
                    "Unsupported file format"
                )






        # ==========================================
        # Case 2: Local File Path
        # ==========================================


        else:




            filepath = str(file)




            if filepath.endswith(".csv"):


                df = pd.read_csv(filepath)




            elif (
                filepath.endswith(".xlsx")
                or filepath.endswith(".xls")
            ):


                df = pd.read_excel(filepath)




            else:


                raise ValueError(
                    "Unsupported file format"
                )




        # ==========================================
        # Metadata
        # ==========================================


        metadata = {


            "dataset_name": file.name if hasattr(file, "name") else str(file).split("/")[-1],
            "file_type": (file.name.split(".")[-1].upper()
                          if hasattr(file, "name")
                          else str(file).split(".")[-1].upper()),


            "rows": df.shape[0],


            "columns": df.shape[1],


            "column_names": list(df.columns),


            "data_types": df.dtypes.astype(str).to_dict()


        }




        return df, metadata






    except Exception as e:




        raise Exception(
            f"Dataset loading failed: {e}"
        )




# ==========================================================
# DATASET OVERVIEW
# ==========================================================
def dataset_overview(df, metadata):
    """
    Generate basic dataset information.
    """


    memory_usage = round(
        df.memory_usage(deep=True).sum() / 1024,
        2
    )


    numeric_columns = len(
        df.select_dtypes(include=np.number).columns
    )


    categorical_columns = len(
        df.select_dtypes(
            include=["object", "category"]
        ).columns
    )


    overview = pd.DataFrame({


        "Property": [
            "Dataset",
            "File Type",
            "Rows",
            "Columns",
            "Numeric Columns",
            "Categorical Columns",
            "Missing Values",
            "Duplicate Rows",
            "Memory Usage (KB)"
        ],


        "Value": [
            metadata["dataset_name"],
            metadata["file_type"],
            metadata["rows"],
            metadata["columns"],
            numeric_columns,
            categorical_columns,
            int(df.isnull().sum().sum()),
            int(df.duplicated().sum()),
            memory_usage
        ]
    })


    return {


        "title": "Dataset Overview",
        "display": overview,
        "json": {
            "dataset_name": metadata["dataset_name"],
            "file_type": metadata["file_type"],
            "rows": metadata["rows"],
            "columns": metadata["columns"],
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "missing_values": int(df.isnull().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "memory_usage_kb": memory_usage
        }
    }




# ==========================================================
# MISSING VALUES
# ==========================================================


def missing_values(df):


    missing = df.isnull().sum()


    missing = missing[missing > 0]


    display = pd.DataFrame({


        "Column": missing.index,


        "Missing Values": missing.values


    })


    return {


        "title": "Missing Value Analysis",


        "display": display,


        "json": missing.to_dict()


    }




# ==========================================================
# DUPLICATE ROWS
# ==========================================================


def duplicate_rows(df):


    duplicates = int(df.duplicated().sum())


    display = pd.DataFrame({


        "Duplicate Rows": [duplicates]


    })


    return {


        "title": "Duplicate Row Analysis",


        "display": display,


        "json": {


            "duplicate_rows": duplicates


        }


    }




# ==========================================================
# SUMMARY STATISTICS
# ==========================================================


def summary_statistics(df):


    summary = df.describe(include="all").fillna("-")


    return {


        "title": "Summary Statistics",


        "display": summary,


        "json": summary.astype(str).to_dict()


    }




# ==========================================================
# OUTLIER DETECTION
# ==========================================================


def detect_outliers(df):


    numeric_columns = df.select_dtypes(include=np.number).columns


    outliers = {}


    for column in numeric_columns:


        q1 = df[column].quantile(0.25)


        q3 = df[column].quantile(0.75)


        iqr = q3 - q1


        lower = q1 - (IQR_MULTIPLIER * iqr)


        upper = q3 + (IQR_MULTIPLIER * iqr)


        count = df[
            (df[column] < lower) |
            (df[column] > upper)
        ].shape[0]


        outliers[column] = count


    display = pd.DataFrame({


        "Column": list(outliers.keys()),


        "Outliers": list(outliers.values())


    })


    return {


        "title": "Outlier Detection",


        "display": display,


        "json": outliers


    }




# ==========================================================
# CORRELATION
# ==========================================================


def correlation_matrix(df):


    correlation = df.select_dtypes(include=np.number).corr().round(2)


    return {


        "title": "Correlation Matrix",


        "display": correlation,


        "json": correlation.to_dict()


    }




# ==========================================================
# GROUPBY ANALYSIS
# ==========================================================


def groupby_analysis(
    df,
    metric_columns,
    group_columns
):


    """
    Dataset aware groupby analysis
    """


    grouped = (


        df
        .groupby(group_columns)[metric_columns]
        .agg(
            [
                "count",
                "mean",
                "sum"
            ]
        )
        .reset_index()


    )


    # ===========================================
    # Flatten MultiIndex column names
    # ===========================================


    grouped.columns = [


        "_".join(col).strip("_")


        if isinstance(col, tuple)


        else col


        for col in grouped.columns


    ]




    return {


        "display": grouped,


        "json": grouped.to_dict(
            orient="records"
        )


    }




# ==========================================================
# VISUALIZATIONS
# ==========================================================


def generate_visualizations(df, output_folder):


    os.makedirs(output_folder, exist_ok=True)


    numeric = df.select_dtypes(include=np.number)


    # Histogram


    numeric.hist(figsize=(12, 8))


    plt.tight_layout()


    plt.savefig(


        os.path.join(output_folder, "histograms.png"),


        dpi=DPI


    )


    plt.close()


    # Boxplot


    plt.figure(figsize=(12, 6))


    numeric.boxplot(rot=45)


    plt.tight_layout()


    plt.savefig(


        os.path.join(output_folder, "boxplots.png"),


        dpi=DPI


    )


    plt.close()


    # Heatmap


    plt.figure(figsize=FIG_SIZE)


    sns.heatmap(


        numeric.corr(),


        annot=True,


        cmap="coolwarm",


        fmt=".2f"


    )


    plt.tight_layout()


    plt.savefig(


        os.path.join(output_folder, "correlation_heatmap.png"),


        dpi=DPI


    )


    plt.close()


    return {


        "title": "Visualizations",


        "display": "Plots saved successfully.",


        "json": {


            "histogram": "histograms.png",


            "boxplot": "boxplots.png",


            "heatmap": "correlation_heatmap.png"


        }


    }




# ==========================================================
# JSON SUMMARY
# ==========================================================
def generate_json_summary(
    overview,
    missing,
    duplicates,
    summary,
    outliers,
    correlation,
    groupby
):
    """
    Generate the final JSON summary.
    """


    return {


        "dataset_information": overview["json"],


        "missing_values": missing["json"],


        "duplicate_rows": duplicates["json"],


        "summary_statistics": summary["json"],


        "outlier_analysis": outliers["json"],


        "correlation_matrix": correlation["json"],


        "groupby_analysis": groupby["json"]


    }
