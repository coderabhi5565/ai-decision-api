import os

import requests
import streamlit as st


API_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)


st.set_page_config(
    page_title="AI Decision Assistant",
    page_icon="🤖",
    layout="centered"
)


def api_request(method, endpoint, token=None, data=None):
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(
        method,
        f"{API_URL}{endpoint}",
        headers=headers,
        json=data,
        timeout=120
    )

    try:
        body = response.json()
    except ValueError:
        body = {"detail": response.text}

    return response.status_code, body


if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None


st.title("🤖 AI Decision Assistant")
st.caption("AI-powered support ticket decision system")

# AUTHENTICATION
if st.session_state.token is None:

    login_tab, register_tab = st.tabs(
        ["Login", "Register"]
    )

    with login_tab:

        st.subheader("Login")

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):
            status_code, data = api_request(
                "POST",
                "/login",
                data={
                    "email": email,
                    "password": password
                }
            )

            if status_code == 200:
                st.session_state.token = data["access_token"]

                user_status, user_data = api_request(
                    "GET",
                    "/me",
                    token=st.session_state.token
                )

                if user_status == 200:
                    st.session_state.user = user_data

                st.success("Login successful!")
                st.rerun()

            else:
                st.error(
                    data.get(
                        "detail",
                        "Login failed"
                    )
                )

    with register_tab:

        st.subheader("Create Account")

        email = st.text_input(
            "Email",
            key="register_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        if st.button(
            "Register",
            use_container_width=True
        ):
            status_code, data = api_request(
                "POST",
                "/register",
                data={
                    "email": email,
                    "password": password
                }
            )

            if status_code == 201:
                st.success(
                    "Account created successfully. "
                    "You can now login."
                )
            else:
                st.error(
                    data.get(
                        "detail",
                        "Registration failed"
                    )
                )

    st.stop()
# LOGGED-IN APPLICATION

user = st.session_state.user

st.sidebar.success(
    f"Logged in as\n{user['email']}"
)

if st.sidebar.button(
    "Logout",
    use_container_width=True
):
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()


new_decision_tab, history_tab = st.tabs(
    ["New Decision", "History"]
)

# NEW DECISION
with new_decision_tab:

    st.header("New Support Ticket")

    message = st.text_area(
        "Customer message",
        placeholder=(
            "Example: My ₹3,500 order arrived "
            "damaged yesterday."
        ),
        height=150
    )

    if st.button(
        "Analyze Ticket",
        type="primary",
        use_container_width=True
    ):

        if not message.strip():
            st.warning(
                "Please enter a customer message."
            )

        else:

            with st.spinner(
                "Analyzing ticket with AI..."
            ):

                status_code, data = api_request(
                    "POST",
                    "/tickets",
                    token=st.session_state.token,
                    data={
                        "message": message
                    }
                )

            if status_code == 201:

                decision = data["decision"]

                st.success(
                    "Decision generated successfully!"
                )

                st.subheader("Decision")

                st.metric(
                    "Recommended Action",
                    decision["action"]
                )

                st.write(
                    "**Confidence:** "
                    f"{decision['confidence']:.2f}"
                )

                st.write("### Reason")

                st.write(
                    decision["reason"]
                )

                st.write("### Sources")

                for source in decision["sources"]:
                    st.write(f"- `{source}`")

            else:

                st.error(
                    data.get(
                        "detail",
                        "Failed to process ticket."
                    )
                )

# HISTORY

with history_tab:

    st.header("Decision History")

    status_code, data = api_request(
        "GET",
        "/tickets",
        token=st.session_state.token
    )

    if status_code == 200:

        if not data:
            st.info(
                "No tickets found."
            )

        else:

            for ticket in data:

                with st.expander(
                    f"Ticket #{ticket['id']}"
                ):

                    st.write(
                        "**Message:**"
                    )

                    st.write(
                        ticket["message"]
                    )

                    st.write(
                        f"**Created:** "
                        f"{ticket['created_at']}"
                    )

                    if ticket["decision"]:

                        decision = ticket["decision"]

                        st.divider()

                        st.write(
                            "**Action:** "
                            f"{decision['action']}"
                        )

                        st.write(
                            "**Confidence:** "
                            f"{decision['confidence']:.2f}"
                        )

                        st.write(
                            "**Reason:** "
                            f"{decision['reason']}"
                        )

                        st.write(
                            "**Sources:** "
                            + ", ".join(
                                decision["sources"]
                            )
                        )

    else:

        st.error(
            data.get(
                "detail",
                "Failed to load history."
            )
        )