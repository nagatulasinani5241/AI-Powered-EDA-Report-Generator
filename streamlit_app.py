import streamlit as st
import pandas as pd


from config import DEFAULT_DATASET


from eda import (
    load_dataset,
    dataset_overview,
    missing_values,
    duplicate_rows,
    summary_statistics,
    detect_outliers,
    correlation_matrix,
    groupby_analysis,
    generate_json_summary
)


from ai_report import (
    generate_ai_report,
    get_compact_summary,
    save_report
)




# =====================================================
# PAGE CONFIG
# =====================================================


st.set_page_config(
    page_title="AI Powered EDA Report Generator",
    page_icon="📊",
    layout="wide"
)




# =====================================================
# SESSION STATE
# =====================================================


defaults = {


    "df": None,


    "metadata": None,


    "overview": None,


    "eda_results": None,


    "groupby_result": None,


    "summary_json": None,


    "ai_report": None


}


for key, value in defaults.items():


    if key not in st.session_state:


        st.session_state[key] = value




# =====================================================
# TITLE
# =====================================================


st.title("📊 AI Powered EDA Report Generator")


st.write(
    "Upload any CSV or Excel dataset and automatically perform Exploratory Data Analysis with AI generated insights."
)




# =====================================================
# SIDEBAR
# =====================================================


st.sidebar.header("Dataset Selection")


uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset",
    type=["csv", "xlsx", "xls"]
)


use_default = st.sidebar.checkbox(
    "Use Default Titanic Dataset",
    value=True
)


st.sidebar.divider()


st.sidebar.header("Gemini Configuration")


api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password"
)




# =====================================================
# LOAD DATASET
# =====================================================


if st.sidebar.button("Load Dataset"):


    if uploaded_file is not None:


        df, metadata = load_dataset(uploaded_file)


    else:


        df, metadata = load_dataset(DEFAULT_DATASET)


    st.session_state.df = df


    st.session_state.metadata = metadata


    st.session_state.overview = dataset_overview(
        df,
        metadata
    )


    # Reset pipeline


    st.session_state.eda_results = None
    st.session_state.groupby_result = None
    st.session_state.summary_json = None
    st.session_state.ai_report = None


    st.success("Dataset Loaded Successfully")




# =====================================================
# DATASET SECTION
# =====================================================


if st.session_state.df is not None:


    df = st.session_state.df


    st.header("📁 Dataset")


    st.subheader("Preview")


    st.dataframe(
        df.head(),
        use_container_width=True
    )


    st.subheader("Overview")


    st.dataframe(
        st.session_state.overview["display"],
        use_container_width=True
    )






# =====================================================
# EDA ANALYSIS
# =====================================================


if st.session_state.df is not None:


    st.divider()


    st.header("🔍 Exploratory Data Analysis")


    if st.button("Run EDA Analysis"):


        with st.spinner("Running EDA..."):


            df = st.session_state.df


            results = {}


            results["missing"] = missing_values(df)


            results["duplicates"] = duplicate_rows(df)


            results["statistics"] = summary_statistics(df)


            results["outliers"] = detect_outliers(df)


            results["correlation"] = correlation_matrix(df)


            st.session_state.eda_results = results


        st.success("EDA Completed Successfully")




# =====================================================
# DISPLAY EDA RESULTS
# =====================================================


if st.session_state.eda_results is not None:


    results = st.session_state.eda_results


    st.divider()


    st.header("📈 EDA Results")


    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Missing Values",
            "Duplicates",
            "Statistics",
            "Outliers",
            "Correlation"
        ]
    )


    # -------------------------
    # Missing Values
    # -------------------------


    with tab1:


        st.subheader("Missing Value Analysis")


        st.dataframe(
            results["missing"]["display"],
            use_container_width=True
        )


    # -------------------------
    # Duplicate Rows
    # -------------------------


    with tab2:


        st.subheader("Duplicate Rows")


        st.write(results["duplicates"]["display"])


    # -------------------------
    # Summary Statistics
    # -------------------------


    with tab3:


        st.subheader("Summary Statistics")


        st.dataframe(
            results["statistics"]["display"],
            use_container_width=True
        )


    # -------------------------
    # Outlier Detection
    # -------------------------


    with tab4:


        st.subheader("Outlier Detection")


        st.dataframe(
            results["outliers"]["display"],
            use_container_width=True
        )


    # -------------------------
    # Correlation Matrix
    # -------------------------


    with tab5:


        st.subheader("Correlation Analysis")


        st.dataframe(
            results["correlation"]["display"],
            use_container_width=True
        )






# =====================================================
# GROUPBY ANALYSIS
# =====================================================


if st.session_state.eda_results is not None:


    st.divider()


    st.header("📊 GroupBy Business Analysis")


    df = st.session_state.df


    numeric_columns = list(
        df.select_dtypes(include="number").columns
    )


    categorical_columns = list(
        df.select_dtypes(exclude="number").columns
    )


    # ------------------------------------
    # Suggest business metric columns
    # ------------------------------------


    business_keywords = [


        "sales",
        "revenue",
        "amount",
        "price",
        "profit",
        "income",
        "salary",
        "fare",
        "cost"


    ]


    suggested_columns = [


        col


        for col in numeric_columns


        if any(
            word in col.lower()
            for word in business_keywords
        )


    ]


    st.subheader("Metric Columns")


    metric_columns = st.multiselect(


        "Select Numeric Columns",


        numeric_columns,


        default=suggested_columns


    )


    st.subheader("Group Columns")


    group_columns = st.multiselect(


        "Select Categorical Columns",


        categorical_columns


    )


    if st.button("Run GroupBy Analysis"):


        if len(metric_columns) == 0:


            st.warning("Select at least one metric column.")


        elif len(group_columns) == 0:


            st.warning("Select at least one group column.")


        else:


            with st.spinner("Running GroupBy Analysis..."):


                st.session_state.groupby_result = groupby_analysis(


                    df,


                    metric_columns,


                    group_columns


                )


            st.success("GroupBy Analysis Completed")






# =====================================================
# DISPLAY GROUPBY RESULT
# =====================================================


if st.session_state.groupby_result is not None:


    st.subheader("GroupBy Result")


    st.dataframe(


        st.session_state.groupby_result["display"],


        use_container_width=True,


        hide_index=True


    )






# =====================================================
# GENERATE JSON SUMMARY
# =====================================================


if st.session_state.eda_results is not None:


    st.divider()


    st.header("📄 Generate AI Input JSON")


    if st.button("Create JSON Summary"):


        groupby = (


            st.session_state.groupby_result


            if st.session_state.groupby_result is not None


            else {


                "display": {},


                "json": {}


            }


        )


        summary = generate_json_summary(


            st.session_state.overview,


            st.session_state.eda_results["missing"],


            st.session_state.eda_results["duplicates"],


            st.session_state.eda_results["statistics"],


            st.session_state.eda_results["outliers"],


            st.session_state.eda_results["correlation"],


            groupby


        )


        st.session_state.summary_json = summary


        st.success("JSON Summary Created Successfully")


# =====================================================
# AI INPUT SUMMARY
# =====================================================


if st.session_state.summary_json is not None:


    st.subheader("🤖 AI Input Preview")


    compact_summary = get_compact_summary(


        st.session_state.summary_json


    )


    with st.expander("View AI Input JSON", expanded=False):


        st.json(compact_summary)








# =====================================================
# AI REPORT GENERATION
# =====================================================


if st.session_state.summary_json is not None:


    st.divider()


    st.header("🤖 AI Report Generation")


    if not api_key:


        st.info(
            "Please enter your Gemini API Key from the sidebar."
        )


    else:


        if st.button("Generate AI Report"):


            with st.spinner("Generating AI Report..."):


                try:


                    report = generate_ai_report(


                        st.session_state.summary_json,


                        api_key


                    )


                    st.session_state.ai_report = report


                    save_report(report)


                    st.success(
                        "AI Report Generated Successfully!"
                    )


                except Exception as e:


                    st.error(
                        f"Error: {e}"
                    )










# =====================================================
# DISPLAY AI REPORT
# =====================================================


if st.session_state.ai_report is not None:


    st.divider()


    st.header("📑 AI Generated Report")


    st.markdown(
        st.session_state.ai_report
    )




# =====================================================
# DOWNLOAD REPORT
# =====================================================


if st.session_state.ai_report is not None:


    st.download_button(


        label="📥 Download Report",


        data=st.session_state.ai_report,


        file_name="EDA_Report.md",


        mime="text/markdown"


    )



