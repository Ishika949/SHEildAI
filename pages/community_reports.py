import streamlit as st

from utils import (
    BASE_DIR,
    REPORT_CATEGORIES,
    URGENCY_LEVELS,
    load_reports,
    render_page_sidebar,
    save_report,
)

render_page_sidebar()
st.title("🛡️ SHEild AI")
st.header("📣 Community Report")
st.write("Read reports from the community or share a concern.")
st.image(
    str(BASE_DIR / "assets" / "images" / "img-report.png"),
    width="stretch",
)

st.subheader("📝 Share a concern")

with st.form("community_report_form"):
    category = st.selectbox("Concern type", REPORT_CATEGORIES)
    location = st.text_input("Area or landmark", max_chars=120)
    urgency = st.selectbox("Urgency", URGENCY_LEVELS, index=1)
    description = st.text_area(
        "What should the community know?",
        max_chars=1000,
        height=120,
    )
    submit = st.form_submit_button(
        "📤 Submit report",
        key="submit_community_report",
    )

if submit:
    try:
        save_report(category, location, urgency, description)
        st.success("Report published.")
    except (ValueError, OSError) as error:
        st.error(f"The report could not be saved: {error}")

st.divider()
st.subheader("Recent reports")

try:
    reports = load_reports()
except (OSError, ValueError) as error:
    st.error(f"Reports could not be loaded: {error}")
else:
    if not reports:
        st.info("No reports yet. New reports will appear here after submission.")
    for report in reports:
        st.subheader(report["category"])
        st.write(f"Location: {report['location']}")
        st.write(f"Urgency: {report['urgency']}")
        st.caption(report["date"])
        st.write(report["description"])
        st.divider()
