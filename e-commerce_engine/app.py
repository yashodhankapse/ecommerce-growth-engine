import os
import uuid
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from backend.database import init_db
from backend.auth import register_user, authenticate_user
from backend.repository import (
    save_upload,
    get_uploads,
    get_upload,
    save_report,
    get_reports
)
from backend.analytics import (
    load_dataset,
    analyze_dataset,
    generate_report
)

st.set_page_config(
    page_title="E-Commerce BI",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

init_db()

st.markdown("""
<style>
.stApp {
    background-color: #f4f7ff;
}
[data-testid="stSidebar"] {
    background-color: #312e81;
}
.hero {
    padding: 25px;
    border-radius: 15px;
    background: linear-gradient(120deg, #4f46e5, #7c3aed);
    color: white;
}
.hero h1 {
    color: white;
}
</style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None

if "selected_upload_id" not in st.session_state:
    st.session_state.selected_upload_id = None


def show_hero(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def store_file(uploaded_file, user_id):
    filename = Path(uploaded_file.name).name
    unique_name = f"{user_id}_{uuid.uuid4().hex}_{filename}"
    path = UPLOAD_DIR / unique_name

    with open(path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return path


def display_dataset(df):
    if df.empty:
        st.warning("Dataset is empty.")
        return

    stats = analyze_dataset(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Records", stats["rows"])
    col2.metric("Columns", stats["columns"])
    col3.metric("Missing Values", stats["missing"])
    col4.metric("Duplicates", stats["duplicates"])

    st.subheader("Dataset Preview")
    st.dataframe(df.head(100), use_container_width=True)

    tab1, tab2, tab3 = st.tabs([
        "Charts",
        "Filter Data",
        "Statistics"
    ])

    with tab1:
        columns = df.columns.tolist()
        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        x_column = st.selectbox(
            "X-axis",
            columns,
            key="x_axis"
        )

        chart_type = st.selectbox(
            "Chart Type",
            ["Bar Chart", "Line Chart", "Histogram", "Pie Chart"],
            key="chart_type"
        )

        if chart_type == "Histogram":
            fig = px.histogram(df, x=x_column)

        elif chart_type == "Pie Chart":
            chart_data = (
                df[x_column]
                .astype(str)
                .value_counts()
                .head(15)
                .reset_index()
            )
            chart_data.columns = ["Category", "Count"]

            fig = px.pie(
                chart_data,
                names="Category",
                values="Count"
            )

        elif numeric_columns:
            y_column = st.selectbox(
                "Y-axis",
                numeric_columns,
                key="y_axis"
            )

            if chart_type == "Bar Chart":
                fig = px.bar(
                    df.head(500),
                    x=x_column,
                    y=y_column
                )
            else:
                fig = px.line(
                    df.head(500),
                    x=x_column,
                    y=y_column
                )

        else:
            st.info("No numeric columns available for this chart.")
            fig = None

        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        filter_column = st.selectbox(
            "Select column",
            df.columns.tolist(),
            key="filter_column"
        )

        if pd.api.types.is_numeric_dtype(df[filter_column]):
            values = df[filter_column].dropna()

            if values.empty:
                filtered_df = df.iloc[0:0]
            else:
                minimum = float(values.min())
                maximum = float(values.max())

                if minimum < maximum:
                    selected_range = st.slider(
                        "Select range",
                        min_value=minimum,
                        max_value=maximum,
                        value=(minimum, maximum)
                    )

                    filtered_df = df[
                        df[filter_column].between(
                            selected_range[0],
                            selected_range[1]
                        )
                    ]
                else:
                    filtered_df = df[
                        df[filter_column] == minimum
                    ]
        else:
            options = (
                df[filter_column]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_values = st.multiselect(
                "Select values",
                options,
                default=options[:5]
            )

            filtered_df = df[
                df[filter_column].astype(str).isin(selected_values)
            ]

        st.write("Filtered records:", len(filtered_df))
        st.dataframe(filtered_df, use_container_width=True)

        st.download_button(
            "Download Filtered CSV",
            filtered_df.to_csv(index=False).encode("utf-8"),
            "filtered_data.csv",
            "text/csv"
        )

    with tab3:
        st.subheader("Statistical Summary")
        st.dataframe(
            df.describe(include="all").transpose(),
            use_container_width=True
        )

        missing = pd.DataFrame({
            "Column": df.columns,
            "Missing Values": [
                df[column].isna().sum()
                for column in df.columns
            ]
        })

        st.subheader("Missing Values")
        st.dataframe(missing, use_container_width=True)


if st.session_state.user is None:
    left, right = st.columns(2)

    with left:
        show_hero(
            "E-Commerce BI",
            "Analyze your business data with interactive dashboards."
        )

        st.write("Upload datasets, create charts and generate reports.")

    with right:
        login_tab, register_tab = st.tabs(["Login", "Register"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                login_button = st.form_submit_button("Login")

            if login_button:
                user = authenticate_user(email, password)

                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        with register_tab:
            with st.form("register_form"):
                name = st.text_input("Full Name")
                new_email = st.text_input("Email")
                new_password = st.text_input(
                    "Password",
                    type="password"
                )
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password"
                )
                register_button = st.form_submit_button("Create Account")

            if register_button:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = register_user(
                        name,
                        new_email,
                        new_password
                    )

                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    st.stop()


user = st.session_state.user

with st.sidebar:
    st.title("E-Commerce BI")
    st.write("Welcome,", user["name"])
    st.write("Role:", user["role"])

    if user["role"] == "analyst":
        pages = [
            "Dashboard",
            "All Uploads",
            "Analyze Dataset",
            "Reports",
            "Profile"
        ]
    else:
        pages = [
            "Dashboard",
            "Upload Data",
            "My Uploads",
            "Published Reports",
            "Profile"
        ]

    page = st.radio("Navigation", pages)

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()


if page == "Dashboard":
    show_hero(
        f"Welcome, {user['name']}",
        "Your business intelligence dashboard"
    )

    uploads = (
        get_uploads()
        if user["role"] == "analyst"
        else get_uploads(user["id"])
    )

    reports = get_reports()

    col1, col2, col3 = st.columns(3)
    col1.metric("Datasets", len(uploads))
    col2.metric("Reports", len(reports))
    col3.metric("Role", user["role"].title())

    if uploads:
        st.dataframe(
            pd.DataFrame(uploads).drop(
                columns=["stored_path"],
                errors="ignore"
            ),
            use_container_width=True
        )
    else:
        st.info("Upload a dataset to get started.")


elif page == "Upload Data":
    show_hero("Upload Dataset", "Choose a CSV or Excel file")

    uploaded_file = st.file_uploader(
        "Select file",
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.dataframe(df.head(10), use_container_width=True)

            if st.button("Save Dataset"):
                path = store_file(uploaded_file, user["id"])

                save_upload(
                    user["id"],
                    uploaded_file.name,
                    str(path),
                    len(df),
                    len(df.columns)
                )

                st.success("Dataset uploaded successfully.")
                st.rerun()

        except Exception as error:
            st.error(f"File error: {error}")


elif page in ["My Uploads", "All Uploads"]:
    uploads = (
        get_uploads()
        if user["role"] == "analyst"
        else get_uploads(user["id"])
    )

    st.subheader("Dataset Library")

    if uploads:
        choices = {
            f"{item['id']} - {item['filename']}": item["id"]
            for item in uploads
        }

        selected = st.selectbox(
            "Choose dataset",
            list(choices.keys())
        )

        st.dataframe(
            pd.DataFrame(uploads).drop(
                columns=["stored_path"],
                errors="ignore"
            ),
            use_container_width=True
        )

        if st.button("Open Dataset"):
            st.session_state.selected_upload_id = choices[selected]

        upload_id = st.session_state.selected_upload_id

        if upload_id in [item["id"] for item in uploads]:
            item = get_upload(upload_id)

            if item and os.path.exists(item["stored_path"]):
                df = load_dataset(item["stored_path"])
                display_dataset(df)
            else:
                st.warning("Dataset file not found.")
    else:
        st.info("No datasets found.")


elif page == "Analyze Dataset":
    uploads = get_uploads()

    st.subheader("Analyze Dataset")

    if uploads:
        choices = {
            f"{item['id']} - {item['filename']}": item["id"]
            for item in uploads
        }

        selected = st.selectbox(
            "Choose dataset",
            list(choices.keys())
        )

        item = get_upload(choices[selected])

        if item and os.path.exists(item["stored_path"]):
            df = load_dataset(item["stored_path"])
            display_dataset(df)

            st.subheader("Publish Report")

            with st.form("report_form"):
                title = st.text_input(
                    "Report Title",
                    value=f"Analysis - {item['filename']}"
                )

                summary = st.text_area(
                    "Report Summary",
                    value=generate_report(df, item["filename"])
                )

                publish = st.form_submit_button("Publish Report")

            if publish:
                if title.strip() and summary.strip():
                    save_report(
                        choices[selected],
                        user["id"],
                        title,
                        summary
                    )
                    st.success("Report published.")
                    st.rerun()
                else:
                    st.error("Enter a report title and summary.")
    else:
        st.info("No datasets available.")


elif page in ["Reports", "Published Reports"]:
    st.subheader("Published Reports")

    reports = get_reports()

    if reports:
        for report in reports:
            with st.expander(report["title"]):
                st.write("Dataset:", report["filename"])
                st.write("Analyst:", report["analyst_name"])
                st.text(report["summary"])

                st.download_button(
                    "Download Report",
                    report["summary"],
                    file_name=f"report_{report['id']}.txt",
                    key=f"download_{report['id']}"
                )
    else:
        st.info("No reports published yet.")


elif page == "Profile":
    show_hero("My Profile", "Your account details")

    st.write("Name:", user["name"])
    st.write("Email:", user["email"])
    st.write("Role:", user["role"].title())


st.divider()
st.caption("E-Commerce Business Intelligence Dashboard")