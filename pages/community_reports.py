import sqlite3

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
st.title("Community Report")

intro_column, image_column = st.columns([1.3, 0.9], gap="large")
with intro_column:
    st.write("Read reports from the community or share a concern.")
with image_column:
    st.image(
        str(BASE_DIR / "assets" / "images" / "img-report.png"),
        width="stretch",
    )

st.space("medium")
try:
    reports = load_reports()
except (OSError, sqlite3.Error, ValueError) as error:
    st.error(f"Reports could not be loaded: {error}")
else:
    if not reports:
        st.info("No reports yet. New reports will appear here after submission.")
    for report in reports:
        with st.container(border=True):
            category_column, urgency_column, date_column = st.columns([1.2, 1, 1])
            category_column.markdown(f"**{report['category']}**")
            urgency_column.write(f"{report['urgency']} urgency")
            date_column.caption(report["date"])
            st.subheader(report["location"])
            st.write(report["description"])

st.space("large")
st.subheader("Share a concern")

with st.form("community_report_form"):
    category = st.selectbox("Concern type", REPORT_CATEGORIES)
    location = st.text_input("Area or landmark", max_chars=120)
    urgency = st.selectbox("Urgency", URGENCY_LEVELS, index=1)
    description = st.text_area(
        "What should the community know?",
        max_chars=1000,
        height=120,
    )
    submit = st.form_submit_button("Submit report")

if submit:
    try:
        save_report(category, location, urgency, description)
        st.success("Report published.")
        st.rerun()
    except (ValueError, OSError, sqlite3.Error) as error:
        st.error(f"The report could not be saved: {error}")
