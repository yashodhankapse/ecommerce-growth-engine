import streamlit as st
import pandas as pd
from datetime import datetime

# =====================================================================
# E-COMMERCE BUSINESS INTELLIGENCE APP  (College Project - Simple Version)
# =====================================================================
# This app has 2 types of users:
#   1) User     -> uploads a data file (CSV/Excel)
#   2) Analyst  -> looks at the file, analyzes it, and marks it done
#
# It also has a simple chatbot that can answer basic questions
# about the uploaded data.
# =====================================================================


st.set_page_config(page_title="E-Commerce Business Intelligence", page_icon="📊", layout="wide")


# ---------------------------------------------------------------------
# SHARED STORAGE
# ---------------------------------------------------------------------
# Normally, User login and Analyst login are two separate browser
# sessions, and Streamlit does NOT share data between sessions by
# default. To make the User's uploaded file visible to the Analyst,
# we need one "shared memory box" that both sides can read/write.
#
# @st.cache_resource creates that shared box. Unlike a normal variable,
# it is created ONLY ONCE and stays alive for everyone using the app,
# like a shared notebook kept on the server.
# ---------------------------------------------------------------------

@st.cache_resource
def get_shared_storage():
    return {"files": []}          # a list that will hold all uploaded files


storage = get_shared_storage()


# Fixed analyst account (for a real app, this would come from a database)
ANALYST_EMAIL = "analyst@ecommerce.com"
ANALYST_PASSWORD = "analyst123"


# ---------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------
# session_state remembers values for ONE user while they click around
# the app (otherwise Streamlit would forget everything on every click).

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# ---------------------------------------------------------------------
# SIMPLE HELPER FUNCTIONS
# ---------------------------------------------------------------------

def read_uploaded_file(uploaded_file):
    """Reads a CSV or Excel file into a pandas DataFrame (a table)."""
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)


def analyze_data(df):
    """A very simple 'analysis': basic stats about the data."""
    report = ""
    report += "Number of rows: " + str(df.shape[0]) + "\n"
    report += "Number of columns: " + str(df.shape[1]) + "\n\n"

    numeric_columns = df.select_dtypes(include="number").columns

    if len(numeric_columns) > 0:
        report += "Column averages:\n"
        for col in numeric_columns:
            avg = df[col].mean()
            report += "- " + col + ": " + str(round(avg, 2)) + "\n"

    missing_values = df.isnull().sum().sum()
    report += "\nMissing values in file: " + str(missing_values)

    return report


def chatbot_reply(question, df):
    """A simple rule-based chatbot. It looks for keywords in the
    question and replies with matching information. This is NOT real
    AI - it just checks 'if this word is in the question, say this'."""

    question = question.lower()

    if "hello" in question or "hi" in question:
        return "Hello! Ask me about the data - like 'how many rows' or 'summary'."

    if df is None:
        return "No data is selected yet. Please upload or select a file first."

    if "row" in question:
        return "This file has " + str(df.shape[0]) + " rows."

    if "column" in question:
        return "The columns are: " + ", ".join(df.columns)

    if "missing" in question:
        return "Missing values: " + str(df.isnull().sum().sum())

    if "summary" in question or "describe" in question:
        return "Here is a quick summary:\n" + str(df.describe())

    return "Sorry, I did not understand. Try asking about 'rows', 'columns', 'missing values' or 'summary'."


def show_chatbot(current_df):
    """Displays the chatbot section (chat history + input box)."""
    st.subheader("💬 Chatbot Assistant")

    for message in st.session_state.chat_messages:
        with st.chat_message(message["sender"]):
            st.write(message["text"])

    user_question = st.chat_input("Ask something about your data...")

    if user_question:
        st.session_state.chat_messages.append({"sender": "user", "text": user_question})
        bot_answer = chatbot_reply(user_question, current_df)
        st.session_state.chat_messages.append({"sender": "assistant", "text": bot_answer})
        st.rerun()


# =====================================================================
# LOGIN PAGE
# =====================================================================

if st.session_state.logged_in == False:

    st.title("📊 E-Commerce Business Intelligence")
    st.write("Login to continue")

    role = st.selectbox("Login as", ["User", "Analyst"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if role == "Analyst":
        st.caption("Demo Analyst login: analyst@ecommerce.com / analyst123")

    if st.button("Login"):

        if role == "User":
            if email != "" and password != "":
                st.session_state.logged_in = True
                st.session_state.role = "User"
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Please enter email and password.")

        else:  # role == "Analyst"
            # .strip() removes accidental spaces, .lower() ignores capital letters
            # This fixes the common bug of "Invalid Credentials" caused by a
            # stray space or different letter case when typing the email.
            entered_email = email.strip().lower()
            entered_password = password.strip()

            if entered_email == ANALYST_EMAIL and entered_password == ANALYST_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.role = "Analyst"
                st.rerun()
            else:
                st.error("Invalid Analyst credentials.")

    st.stop()   # stops the rest of the code from running on the login page


# =====================================================================
# USER DASHBOARD
# =====================================================================

if st.session_state.role == "User":

    st.title("👤 User Dashboard")
    st.write("Welcome, " + st.session_state.user_email)

    st.header("Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        df = read_uploaded_file(uploaded_file)

        st.write("Preview of your file:")
        st.dataframe(df.head())

        # Check if this file was already uploaded before (avoid duplicates)
        already_uploaded = False
        for f in storage["files"]:
            if f["filename"] == uploaded_file.name and f["uploader"] == st.session_state.user_email:
                already_uploaded = True

        if already_uploaded == False:
            new_file = {
                "filename": uploaded_file.name,
                "uploader": st.session_state.user_email,
                "uploaded_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "Pending",
                "data": df,
                "report": None,
            }
            storage["files"].append(new_file)
            st.success("File uploaded successfully!")

    st.header("My Files")

    my_files = []
    for f in storage["files"]:
        if f["uploader"] == st.session_state.user_email:
            my_files.append(f)

    if len(my_files) == 0:
        st.info("You have not uploaded any files yet.")
    else:
        for f in my_files:
            st.write("📄 " + f["filename"] + " — Status: " + f["status"])
            if f["status"] == "Completed":
                with st.expander("View Report"):
                    st.text(f["report"])

    st.divider()

    # Chatbot uses the user's most recently uploaded file (if any)
    last_df = my_files[-1]["data"] if len(my_files) > 0 else None
    show_chatbot(last_df)

    st.divider()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()


# =====================================================================
# ANALYST DASHBOARD
# =====================================================================

if st.session_state.role == "Analyst":

    st.title("📊 Analyst Dashboard")
    st.success("Welcome, Analyst!")

    all_files = storage["files"]

    pending_count = 0
    completed_count = 0
    for f in all_files:
        if f["status"] == "Pending":
            pending_count += 1
        if f["status"] == "Completed":
            completed_count += 1

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Files", len(all_files))
    col2.metric("Pending", pending_count)
    col3.metric("Completed", completed_count)

    st.header("Files Uploaded by Users")

    if len(all_files) == 0:
        st.info("No files uploaded yet.")
        selected_df = None
    else:
        file_names = []
        for f in all_files:
            file_names.append(f["filename"] + " (from " + f["uploader"] + ")")

        chosen = st.selectbox("Select a file to analyze", file_names)
        chosen_index = file_names.index(chosen)
        selected_file = all_files[chosen_index]
        selected_df = selected_file["data"]

        st.write("Preview:")
        st.dataframe(selected_df.head(10))

        # Simple built-in chart (no extra libraries needed)
        numeric_columns = selected_df.select_dtypes(include="number").columns
        if len(numeric_columns) > 0:
            chart_column = st.selectbox("Choose a column to chart", numeric_columns)
            st.line_chart(selected_df[chart_column])

        if st.button("Run Analysis and Mark Completed"):
            selected_file["report"] = analyze_data(selected_df)
            selected_file["status"] = "Completed"
            st.success("Analysis complete! The user can now see the report.")
            st.rerun()

        if selected_file["report"] is not None:
            st.subheader("Report")
            st.text(selected_file["report"])

    st.divider()
    show_chatbot(selected_df)

    st.divider()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()