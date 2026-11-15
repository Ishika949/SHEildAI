import streamlit as st

from utils import BASE_DIR, initialize_data

st.set_page_config(
    page_title="SHEild AI",
    page_icon=str(BASE_DIR / "assets" / "venus-shield-512.png"),
    layout="wide",
)

initialize_data()


def render_home():
    user = st.session_state.get("current_user")

    with st.sidebar:
        st.markdown("### SHEild AI")
        st.caption("Safety planning and community information")
        if user:
            st.caption(f"Signed in as {user['name']}")
            if st.button("Sign out", key="home_sign_out"):
                st.session_state.pop("current_user", None)
                st.rerun()

    intro_column, image_column = st.columns([1.3, 0.9], gap="large")
    with intro_column:
        st.title("Plan for everyday safety")
        st.write(
            "Find practical information, share a local report, or manage trusted contacts."
        )
    with image_column:
        st.image(
            str(BASE_DIR / "assets" / "images" / "img-app.png"),
            width="stretch",
        )

    st.warning(
        "If you are in immediate danger, move toward a populated place if you can and contact "
        "someone you trust or local emergency services."
    )

    st.space("large")
    st.subheader("Plan and learn")
    plan_column, share_column = st.columns(2, gap="large")
    with plan_column:
        with st.container(border=True):
            st.page_link(
                "pages/dashboard.py",
                label="Dashboard",
                icon=":material/contacts:",
            )
            st.caption("Manage trusted contacts and use SOS.")
            st.page_link(
                "pages/learning.py",
                label="Learning",
                icon=":material/menu_book:",
            )
            st.caption("Read about safety planning, rights, and getting help.")
    with share_column:
        with st.container(border=True):
            st.subheader("Ask and share")
            st.page_link(
                "pages/safety_guide.py",
                label="AI Chat",
                icon=":material/search:",
            )
            st.caption("Find answers in the guidance published on this site.")
            st.page_link(
                "pages/community_reports.py",
                label="Community Report",
                icon=":material/campaign:",
            )
            st.caption("Read reports or share a concern with the community.")

    st.space("large")
    if user:
        with st.container(border=True):
            st.subheader("Your account")
            st.success("You are signed in.")
            st.page_link("pages/profile.py", label="Open Profile")
    else:
        with st.container(border=True):
            st.subheader("Your account")
            st.write("Sign in to manage contacts or create an account.")
            login_column, signup_column = st.columns(2)
            login_column.page_link("pages/login.py", label="Login")
            signup_column.page_link("pages/signup.py", label="Sign Up")


navigation_pages = [
    st.Page(render_home, title="App", default=True),
    st.Page("pages/safety_guide.py", title="AI Chat"),
    st.Page("pages/community_reports.py", title="Community Report"),
    st.Page("pages/dashboard.py", title="Dashboard"),
    st.Page("pages/learning.py", title="Learning"),
]

if st.session_state.get("current_user"):
    navigation_pages.append(st.Page("pages/profile.py", title="Profile"))
else:
    navigation_pages.extend(
        [
            st.Page("pages/login.py", title="Login"),
            st.Page("pages/signup.py", title="Sign Up"),
        ]
    )

st.navigation(navigation_pages, position="sidebar").run()
