import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px

# =====================================================
# GEMINI API KEY
# =====================================================

GEMINI_API_KEY = "AQ.Ab8RN6IcBeRCgc9wFdvZ38zgqfwSldBNZCghxjs8AS2gCSGfWA"

genai.configure(api_key=GEMINI_API_KEY)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Attendance System",
    page_icon="🎓",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp{
    background-color:#eef7ff;
}

.title{
    text-align:center;
    color:#003366;
}

.metric-box{
    padding:10px;
    border-radius:10px;
    background:#ffffff;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown(
    "<h1 class='title'>🎓 AI Attendance Management System</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<center><h4>Smart Attendance Analytics using Gemini AI</h4></center>",
    unsafe_allow_html=True
)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📌 How to Use")

    st.markdown("""
    1. Upload Attendance File

    2. AI calculates attendance

    3. Detects risk students

    4. Generates smart reports

    5. Faculty receives recommendations

    6. AI suggests intervention plans
    """)

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "📂 Upload Attendance Sheet",
    type=["csv","xlsx"]
)

# =====================================================
# LOAD FILE
# =====================================================

def load_file(file):

    if file.name.endswith(".csv"):
        return pd.read_csv(file)

    return pd.read_excel(file)

# =====================================================
# ATTENDANCE CALCULATION
# =====================================================

def calculate_attendance(df):

    total_classes = (
        df.groupby("Student Name")
        .size()
    )

    present_classes = (
        df[df["Status"]=="Present"]
        .groupby("Student Name")
        .size()
    )

    result = pd.DataFrame({
        "Total Classes":total_classes,
        "Present Classes":present_classes
    }).fillna(0)

    result["Attendance %"] = (
        result["Present Classes"] /
        result["Total Classes"]
    ) * 100

    result.reset_index(inplace=True)

    return result

# =====================================================
# GEMINI ANALYSIS
# =====================================================

def ai_analysis(summary):

    prompt = f"""

You are an AI Attendance Analyst.

Analyze the attendance data.

Generate:

1. Executive Summary

2. Attendance Overview Table

3. Students Below 75%

4. Students Below 60%

5. Attendance Risk Classification

Categories:
- Safe
- Moderate Risk
- High Risk

6. Possible Causes of Low Attendance

7. Student Engagement Insights

8. Faculty Recommendations

9. Parent Communication Suggestions

10. Smart Intervention Plan

11. Attendance Improvement Strategies

12. Motivational Quote

Attendance Data:

{summary}

Return professional report.
"""

    try:

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        return f"AI Error: {e}"

# =====================================================
# MAIN APP
# =====================================================

if uploaded_file:

    df = load_file(uploaded_file)

    st.success("✅ Attendance File Uploaded Successfully")

    st.subheader("📋 Raw Attendance Data")

    st.dataframe(df)

    attendance_summary = calculate_attendance(df)

    st.subheader("📊 Attendance Summary")

    st.dataframe(attendance_summary)

    # Metrics

    total_students = len(attendance_summary)

    avg_attendance = (
        attendance_summary["Attendance %"]
        .mean()
    )

    low_students = len(
        attendance_summary[
            attendance_summary["Attendance %"] < 75
        ]
    )

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "Students",
        total_students
    )

    c2.metric(
        "Average Attendance",
        f"{avg_attendance:.2f}%"
    )

    c3.metric(
        "Low Attendance",
        low_students
    )

    # Risk Students

    st.subheader("⚠️ At-Risk Students")

    risk_students = attendance_summary[
        attendance_summary["Attendance %"] < 75
    ]

    st.dataframe(risk_students)

    # Chart

    st.subheader("📈 Attendance Visualization")

    fig = px.bar(
        attendance_summary,
        x="Student Name",
        y="Attendance %",
        title="Attendance Percentage"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # AI Analysis

    st.subheader("🤖 AI Attendance Intelligence Report")

    with st.spinner(
        "Analyzing attendance using Gemini AI..."
    ):

        report = ai_analysis(
            attendance_summary.to_string()
        )

    st.markdown(report)

    st.success(
        "🎉 Attendance Analysis Completed"
    )

    st.balloons()

else:

    st.info(
        "Upload a CSV or Excel attendance sheet to begin."
    )
