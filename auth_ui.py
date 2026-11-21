
import streamlit as st

from auth import (
    initialize_database,
    verify_admin,
    verify_faculty,
    create_faculty,
    get_all_faculty,
    deactivate_faculty,
    reset_faculty_password
)



def render_login():

    initialize_database()

    st.markdown("""
    <style>
    @keyframes login-fade-up {
        from {
            opacity: 0;
            transform: translateY(18px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes login-gradient-drift {
        0%, 100% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
    }

    @keyframes login-icon-float {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-7px);
        }
    }

    .login-left {
        background: linear-gradient(145deg, #102A43, #155E75, #0F766E);
        background-size: 180% 180%;
        padding: 45px 35px;
        border-radius: 20px;
        color: white;
        min-height: 490px;
        box-shadow: 0 12px 35px rgba(16, 42, 67, 0.15);
        animation:
            login-fade-up 650ms ease-out both,
            login-gradient-drift 18s ease-in-out infinite;
        transition: transform 220ms ease, box-shadow 220ms ease;
    }

    .login-left:hover {
        transform: translateY(-3px);
        box-shadow: 0 18px 42px rgba(16, 42, 67, 0.2);
    }

    .login-left h1 {
        color: white !important;
        font-size: 34px;
        line-height: 1.3;
        margin-top: 15px;
    }

    .login-left p {
        color: #E0F2F1 !important;
        line-height: 1.8;
        font-size: 15px;
    }

    .login-icon {
        font-size: 58px;
        margin-bottom: 15px;
        animation: login-icon-float 3s ease-in-out infinite;
    }

    .login-right {
        background: white;
        padding: 25px 22px;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 12px 35px rgba(16, 42, 67, 0.08);
        animation: login-fade-up 650ms 100ms ease-out both;
    }

    .login-right h2 {
        color: #102A43 !important;
        font-size: 28px;
    }

    .login-caption {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 20px;
    }

    div[data-testid="stForm"] {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px;
        animation: login-fade-up 650ms 180ms ease-out both;
    }

    div[data-testid="stFormSubmitButton"] button {
        background: #0F766E;
        color: white;
        border: none;
        border-radius: 9px;
        min-height: 45px;
        font-weight: 600;
        transition: transform 180ms ease, box-shadow 180ms ease,
            background-color 180ms ease;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background: #115E59;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(15, 118, 110, 0.22);
    }

    @media (max-width: 700px) {
        .login-left, .login-right {
            min-height: auto;
            padding: 25px;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        .login-left,
        .login-right,
        .login-icon,
        div[data-testid="stForm"] {
            animation: none !important;
            transition: none !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Main two-column login layout
    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:

        st.html("""
        <div class="login-left">
            <div class="login-icon">🎓</div>
            <h1>Question Paper<br>OBE Agent</h1>
            <p>
                An intelligent academic assessment workspace
                powered by Agentic AI.
            </p>
            <hr style="border-color:rgba(255,255,255,0.3);">
            <p>✦ Intelligent question paper generation</p>
            <p>✦ Outcome-Based Education mapping</p>
            <p>✦ Academic analysis and reporting</p>
            <p>✦ Secure faculty access</p>
            <br>
            <p style="font-size:13px; opacity:0.8;">
                KLE Technological University
            </p>
        </div>
        """)

    with right_col:

        st.html("""
        <div class="login-right">
            <h2>Welcome Back!</h2>
            <p class="login-caption">
                Sign in to access your academic workspace.
            </p>
        </div>
        """)

        login_type = st.radio(
            "Select account type",
            ["Faculty", "Administrator"],
            horizontal=True,
            key="login_account_type"
        )

        with st.form("login_form"):

            user_id = st.text_input(
                "Faculty ID" if login_type == "Faculty" else "Admin ID",
                placeholder="Enter your ID"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            submitted = st.form_submit_button(
                "Sign In →",
                use_container_width=True
            )

        if submitted:

            if not user_id.strip() or not password:
                st.error("Please enter both ID and password.")

            elif login_type == "Administrator":

                valid = verify_admin(user_id.strip(), password)

                if valid:
                    st.session_state.authenticated = True
                    st.session_state.user_role = "admin"
                    st.session_state.user_id = user_id.strip()
                    st.session_state.user_name = "Administrator"
                    st.session_state.active_page = "Home"
                    st.session_state.navigation_page = "Choose a page"
                    st.rerun()

                else:
                    st.error("Invalid administrator ID or password.")

            else:

                faculty = verify_faculty(user_id.strip(), password)

                if faculty:
                    st.session_state.authenticated = True
                    st.session_state.user_role = "faculty"
                    st.session_state.user_id = faculty["faculty_id"]
                    st.session_state.user_name = faculty["faculty_name"]
                    st.session_state.active_page = "Home"
                    st.session_state.navigation_page = "Choose a page"
                    st.rerun()

                else:
                    st.error("Invalid Faculty ID or password.")

def render_admin_panel():

    st.title("👥 Faculty Account Management")

    st.write(
        "Create faculty accounts and manage existing faculty access."
    )

    st.divider()

    st.subheader("Create Faculty Account")

    with st.form("create_faculty_form"):

        faculty_id = st.text_input("Faculty ID")
        faculty_name = st.text_input("Faculty Name")

        password = st.text_input(
            "Temporary Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Create Faculty Account",
            use_container_width=True
        )

    if submitted:

        if not faculty_id.strip() or not faculty_name.strip():
            st.error("Faculty ID and Faculty Name are required.")

        elif password != confirm_password:
            st.error("Passwords do not match.")

        elif len(password) < 8:
            st.error("Password must contain at least 8 characters.")

        else:

            success, message = create_faculty(
                faculty_id,
                faculty_name,
                password
            )

            if success:
                st.success(message)
            else:
                st.error(message)

    st.divider()

    st.subheader("Existing Faculty Accounts")

    faculty_list = get_all_faculty()

    if faculty_list:

        for faculty in faculty_list:

            faculty_id, name, created_at, active = faculty

            with st.expander(f"{name} — {faculty_id}"):

                st.write(f"Created: {created_at}")

                st.write(
                    f"Status: {'Active' if active else 'Inactive'}"
                )

                if active:

                    if st.button(
                        "Deactivate Account",
                        key=f"deactivate_{faculty_id}"
                    ):

                        success = deactivate_faculty(faculty_id)

                        if success:
                            st.success("Faculty account deactivated.")
                            st.rerun()
                        else:
                            st.error("Unable to deactivate this account.")

                with st.form(f"reset_{faculty_id}"):

                    new_password = st.text_input(
                        "New Password",
                        type="password"
                    )

                    confirm_new = st.text_input(
                        "Confirm New Password",
                        type="password"
                    )

                    reset = st.form_submit_button(
                        "Reset Faculty Password"
                    )

                    if reset:

                        if new_password != confirm_new:
                            st.error("Passwords do not match.")

                        elif len(new_password) < 8:
                            st.error(
                                "Password must contain at least 8 characters."
                            )

                        else:

                            success, message = reset_faculty_password(
                                faculty_id,
                                new_password
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

    else:
        st.info("No faculty accounts have been created yet.")
