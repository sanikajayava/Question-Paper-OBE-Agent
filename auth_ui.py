
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
    .login-background {
        max-width: 1050px;
        margin: 35px auto 10px auto;
        border-radius: 25px;
        overflow: hidden;
        box-shadow: 0 18px 45px rgba(38, 54, 120, 0.15);
        border: 1px solid #e0e7ff;
    }

    .login-left {
        background: linear-gradient(
            145deg,
            #111c3b,
            #334b91,
            #7956c8
        );
        padding: 55px 35px;
        color: white;
        min-height: 440px;
    }

    .login-left h1 {
        color: white !important;
        font-size: 34px;
        line-height: 1.25;
    }

    .login-left p {
        color: #e0e8ff;
        line-height: 1.8;
    }

    .login-icon {
        font-size: 65px;
        margin-bottom: 18px;
    }

    .login-right {
        background: white;
        padding: 35px;
        min-height: 440px;
    }

    .login-right h2 {
        color: #253b73 !important;
    }

    .login-caption {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 25px;
    }

    [data-testid="stForm"] {
        background: #f8faff;
        border: 1px solid #e0e7ff;
        border-radius: 15px;
        padding: 22px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-background">
        <div style="
            display:grid;
            grid-template-columns: 1fr 1fr;
        ">
            <div class="login-left">
                <div class="login-icon">🎓</div>
                <h1>Question Paper<br>OBE Agent</h1>
                <p>
                    An intelligent academic assessment workspace
                    powered by Agentic AI.
                </p>
                <hr style="border-color:rgba(255,255,255,0.25);">
                <p>✦ Intelligent question paper generation</p>
                <p>✦ Outcome-Based Education mapping</p>
                <p>✦ Academic analysis and reporting</p>
                <p>✦ Secure faculty access</p>
            </div>
            <div class="login-right">
                <h2>Welcome Back!</h2>
                <p class="login-caption">
                    Sign in to access your academic workspace.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Login form is placed below the welcome panel.
    # This keeps all Streamlit inputs functional.

    login_type = st.radio(
        "Select account type",
        ["Faculty", "Administrator"],
        horizontal=True
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
            return

        if login_type == "Administrator":

            valid = verify_admin(
                user_id.strip(),
                password
            )

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

            faculty = verify_faculty(
                user_id.strip(),
                password
            )

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
