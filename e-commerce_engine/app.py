import streamlit as st

st.set_page_config(
    page_title="E-Commerce Business Intelligence",
    page_icon="📊",
    layout="wide"
)

# ================= SESSION =================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None


# ================= CSS =================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0f172a, #312e81);
}

.login-box {
    background: white;
    padding: 45px;
    border-radius: 25px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.30);
}

.title {
    color: white;
    font-size: 48px;
    font-weight: 800;
}

.subtitle {
    color: #cbd5e1;
    font-size: 19px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
}

.metric {
    font-size: 30px;
    font-weight: 800;
    color: #312e81;
}

</style>
""", unsafe_allow_html=True)


# =================================================
# LOGIN PAGE
# =================================================

if not st.session_state.logged_in:

    left, right = st.columns([1.15, 0.85], gap="large")

    # ---------- LEFT ----------
    with left:

        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown(
            '<div class="title">📊 E-Commerce<br>'
            '<span style="color:#a78bfa;">Business Intelligence</span></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<p class="subtitle">'
            'Transform business data into powerful insights, '
            'interactive dashboards and intelligent decisions.'
            '</p>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <br>
        <h3 style="color:white;">🚀 Powerful Analytics</h3>

        <p class="subtitle">📈 Sales & Revenue Analysis</p>
        <p class="subtitle">👥 Customer Behaviour Analysis</p>
        <p class="subtitle">📦 Product Performance</p>
        <p class="subtitle">🤖 ML Predictions</p>
        <p class="subtitle">📋 Automated Business Reports</p>
        """, unsafe_allow_html=True)

        st.markdown(
            "<div style='font-size:90px;text-align:center;'>"
            "📊 🛒 📈 🤖"
            "</div>",
            unsafe_allow_html=True
        )


    # ---------- RIGHT ----------
    with right:

        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown(
            '<div class="login-box">'
            '<h1 style="text-align:center;color:#1e1b4b;">🔐 Welcome</h1>'
            '<p style="text-align:center;color:#64748b;">'
            'Select your account type to continue'
            '</p>',
            unsafe_allow_html=True
        )

        role = st.selectbox(
            "Login Type",
            ["👤 User", "📊 Analyst"]
        )

        email = st.text_input(
            "📧 Email",
            placeholder="Enter your email"
        )

        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Enter your password"
        )

        if st.button("🚀 Login", use_container_width=True):

            # USER LOGIN
            if role == "👤 User":

                if email and password:

                    st.session_state.logged_in = True
                    st.session_state.role = "User"
                    st.session_state.user_email = email
                    st.rerun()

                else:
                    st.error("Please enter email and password.")


            # ANALYST LOGIN
            else:

                if (
                    email == "analyst@ecommerce.com"
                    and password == "analyst123"
                ):

                    st.session_state.logged_in = True
                    st.session_state.role = "Analyst"
                    st.rerun()

                else:
                    st.error("❌ Invalid Analyst credentials.")

        st.markdown(
            "<hr>"
            "<p style='text-align:center;color:#64748b;'>"
            "🔒 Secure • 📊 Smart • ⚡ Fast"
            "</p></div>",
            unsafe_allow_html=True
        )

    st.stop()


# =================================================
# USER DASHBOARD
# =================================================

if st.session_state.role == "User":

    st.title("👤 User Dashboard")

    st.write(
        f"Welcome, **{st.session_state.user_email}**"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="card">'
            '<div class="metric">📤</div>'
            '<h3>Upload Data</h3>'
            '<p>Send your CSV or Excel file for analysis.</p>'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            '<div class="card">'
            '<div class="metric">⏳</div>'
            '<h3>Analysis Status</h3>'
            '<p>Track your analysis progress.</p>'
            '</div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '<div class="card">'
            '<div class="metric">📋</div>'
            '<h3>Final Report</h3>'
            '<p>Download your completed report.</p>'
            '</div>',
            unsafe_allow_html=True
        )

    st.divider()

    st.header("📤 Upload Your Business Data")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx"]
    )

    if uploaded_file:

        st.success(
            f"✅ {uploaded_file.name} uploaded successfully!"
        )

        st.info(
            "Your file is ready to be analyzed by the analyst."
        )

    st.divider()

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()


# =================================================
# ANALYST DASHBOARD
# =================================================

elif st.session_state.role == "Analyst":

    st.title("📊 Analyst Dashboard")

    st.success("Welcome Analyst!")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📥 Files Received", "0")

    with col2:
        st.metric("🔄 Processing", "0")

    with col3:
        st.metric("✅ Completed", "0")

    with col4:
        st.metric("📋 Reports", "0")

    st.divider()

    st.header("📥 User Data")

    st.info(
        "User-uploaded files will appear here."
    )

    st.header("🔍 Data Analysis")

    st.info(
        "Select a user file to start analysis."
    )

    st.header("📋 Reports")

    st.info(
        "Generated reports will be sent to the respective user."
    )

    st.divider()

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()