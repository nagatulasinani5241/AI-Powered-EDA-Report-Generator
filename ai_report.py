"""
ai_report.py
--------------------------------------------------------
AI Report Generation using Gemini
"""


import json
import google.generativeai as genai


from config import (
    AI_PROVIDER,
    GEMINI_MODEL,
    GEMINI_API_KEY
)




# =====================================================
# CONFIGURE GEMINI
# =====================================================


def configure_gemini(api_key):


    genai.configure(api_key=api_key)


    return genai.GenerativeModel(GEMINI_MODEL)




# =====================================================
# PREPARE AI SUMMARY
# =====================================================
def prepare_prompt_data(summary_json):
    """
    Prepare a compact JSON summary for AI report generation.
    """


    compact = {}


    # =====================================================
    # Dataset Information
    # =====================================================


    compact["dataset_information"] = summary_json.get(
        "dataset_information",
        {}
    )


    # =====================================================
    # Missing Values (Only Non-Zero)
    # =====================================================


    missing = summary_json.get(
        "missing_values",
        {}
    )


    filtered_missing = {}


    if isinstance(missing, dict):


        for column, count in missing.items():


            try:


                if count > 0:


                    filtered_missing[column] = count


            except:


                pass


    compact["missing_values"] = filtered_missing


    # =====================================================
    # Duplicate Rows
    # =====================================================


    compact["duplicate_rows"] = summary_json.get(
        "duplicate_rows",
        {}
    )


    # =====================================================
    # Summary Statistics
    # Keep only useful statistics
    # =====================================================


    statistics = summary_json.get(
        "summary_statistics",
        {}
    )


    compact_statistics = {}


    if isinstance(statistics, dict):


        for column, values in statistics.items():


            if isinstance(values, dict):


                compact_statistics[column] = {


                    "mean": values.get("mean"),


                    "median": values.get("50%"),


                    "min": values.get("min"),


                    "max": values.get("max")


                }


    compact["summary_statistics"] = compact_statistics


    # =====================================================
    # Top Correlations
    # =====================================================


    correlation = summary_json.get(
        "correlation_matrix",
        {}
    )


    correlation_list = []


    if isinstance(correlation, dict):


        visited = set()


        for col1, row in correlation.items():


            if not isinstance(row, dict):
                continue


            for col2, value in row.items():


                if col1 == col2:
                    continue


                key = tuple(sorted([col1, col2]))


                if key in visited:
                    continue


                visited.add(key)


                try:


                    correlation_list.append({


                        "Column 1": col1,


                        "Column 2": col2,


                        "Correlation": round(float(value), 3)


                    })


                except:


                    pass


    correlation_list = sorted(


        correlation_list,


        key=lambda x: abs(x["Correlation"]),


        reverse=True


    )[:5]


    compact["top_correlations"] = correlation_list


    # =====================================================
    # Outlier Analysis
    # =====================================================


    outliers = summary_json.get(
        "outlier_analysis",
        {}
    )


    compact_outliers = {}


    if isinstance(outliers, dict):


        for column, values in outliers.items():


            if isinstance(values, dict):


                compact_outliers[column] = values.get(
                    "outlier_count",
                    0
                )


    compact["outlier_analysis"] = compact_outliers


    # =====================================================
    # GroupBy Analysis
    # =====================================================


    groupby = summary_json.get(
        "groupby_analysis",
        []
    )


    if isinstance(groupby, list):


        compact["groupby_analysis"] = groupby[:5]


    else:


        compact["groupby_analysis"] = groupby


    return compact




# =====================================================
# BUILD PROMPT
# =====================================================


def build_prompt(summary):


    return f"""
        You are a Senior Data Analyst.


        Below is the EDA summary of a dataset.


        {json.dumps(summary, indent=2)}


        ------------------------------------------------


        Write a professional EDA report.


        Use exactly these headings:


        # Dataset Overview


        # Data Quality Assessment


        # Statistical Insights


        # Correlation Analysis


        # Outlier Analysis


        # GroupBy Insights


        # Business Recommendations


        # Suggested Visualizations


        # Conclusion


        Guidelines:


        - Explain insights rather than repeating values.
        - If a section has no data, write "No significant findings."
        - Use Markdown.
        """






# =====================================================
# GENERATE REPORT
# =====================================================
from google.generativeai.types import GenerationConfig




def generate_ai_report(summary_json, api_key):


    try:


        model = configure_gemini(api_key)


        summary = prepare_prompt_data(summary_json)


        prompt = build_prompt(summary)


        response = model.generate_content(
                    prompt,
                    generation_config=GenerationConfig(
                        temperature=0.2,
                        max_output_tokens=2000
                    )
                )
        return response.text


    except Exception as e:


        raise Exception(str(e))




def get_compact_summary(summary_json):
    """
    Return compact summary for UI preview.
    """


    return prepare_prompt_data(summary_json)


# =====================================================
# SAVE REPORT
# =====================================================


def save_report(report):


    with open(


        "output/EDA_Report.md",


        "w",


        encoding="utf-8"


    ) as file:


        file.write(report)
