import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px
import os

# =====================================================
# GEMINI API KEY
# =====================================================

GEMINI_API_KEY = "AQ.Ab8RN6IcBeRCgc9wFdvZ38zgqfwSldBNZCghxjs8AS2gCSGfWA"

genai.configure(api_key=GEMINI_API_KEY)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Attendance Management System",
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
    "<h4 style='text-align:center;'>Powered by Gemini AI</h4>",
    unsafe_allow_html=True
)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📌 Features")

    st.markdown("""
    ✅ Daily Attendance Entry

    ✅ Upload Attendance Excel

    ✅ Attendance Dashboard

    ✅ Risk Student Detection

    ✅ AI Parent Alert Generator

    ✅ AttendanceGPT Chatbot

    ✅ AI Attendance Report
    """)

# =====================================================
# DAILY ATTENDANCE ENTRY
# =====================================================

st.subheader("📝 Daily Attendance Entry")

with st.expander("Mark Attendance"):

    roll_no = st.text_input("Roll Number")

    student_name = st.text_input("Student Name")

    status = st.selectbox(
        "Status",
        ["Present", "Absent"]
    )

    if st.button("Save Attendance"):

        today = pd.Timestamp.now().date()

        new_record = pd.DataFrame({
            "Date":[today],
            "Roll No":[roll_no],
            "Student Name":[student_name],
            "Status":[status]
        })

        if os.path.exists("attendance_records.csv"):

            old_data = pd.read_csv(
                "attendance_records.csv"
            )

            old_data = pd.concat(
                [old_data,new_record],
                ignore_index=True
            )

            old_data.to_csv(
                "attendance_records.csv",
                index=False
            )

        else:

            new_record.to_csv(
                "attendance_records.csv",
                index=False
            )

        st.success(
            "Attendance Saved Successfully"
        )

# =====================================================
# FILE UPLOAD
# =====================================================

st.subheader("📂 Upload Attendance File")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel",
    type=["csv","xlsx"]
)

# =====================================================
# LOAD DATA
# =====================================================

def load_data(file):

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
# AI REPORT
# =====================================================

def generate_report(summary):

    prompt = f"""
You are an attendance analyst.

Analyze this attendance data.

Generate:

1. Attendance Summary
2. Students Below 75%
3. Students Below 60%
4. High Risk Students
5. Faculty Recommendations
6. Improvement Suggestions
7. Motivational Quote

Attendance Data:

{summary}
"""

    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    response = model.generate_content(
        prompt
    )

    return response.text

# =====================================================
# MAIN
# =====================================================

if uploaded_file:

    df = load_data(uploaded_file)

    st.success(
        "Attendance File Uploaded"
    )

    st.subheader("📋 Attendance Data")

    st.dataframe(df)

    attendance_summary = calculate_attendance(df)

    st.subheader("📊 Attendance Summary")

    st.dataframe(attendance_summary)

    # Metrics

    total_students = len(
        attendance_summary
    )

    avg_attendance = (
        attendance_summary[
            "Attendance %"
        ].mean()
    )

    low_students = len(
        attendance_summary[
            attendance_summary[
                "Attendance %"
            ] < 75
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
        "Below 75%",
        low_students
    )

    # Risk Students

    st.subheader(
        "⚠️ Risk Students"
    )

    risk_students = attendance_summary[
        attendance_summary[
            "Attendance %"
        ] < 75
    ]

    st.dataframe(
        risk_students
    )

    # Chart

    st.subheader(
        "📈 Attendance Chart"
    )

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

    # =================================================
    # AI PARENT ALERT
    # =================================================

    st.subheader(
        "📨 AI Parent Alert Generator"
    )

    selected_student = st.selectbox(
        "Select Student",
        attendance_summary[
            "Student Name"
        ]
    )

    if st.button(
        "Generate Parent Message"
    ):

        attendance = attendance_summary[
            attendance_summary[
                "Student Name"
            ] == selected_student
        ]["Attendance %"].values[0]

        prompt = f"""
Generate a formal parent message.

Student:
{selected_student}

Attendance:
{attendance:.2f}%

Mention:
- Low attendance
- Exam eligibility concern
- Request support
"""

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        response = model.generate_content(
            prompt
        )

        st.success(
            "Message Generated"
        )

        st.write(
            response.text
        )

    # =================================================
    # AI REPORT
    # =================================================

    st.subheader(
        "🤖 AI Attendance Report"
    )

    with st.spinner(
        "Generating AI Report..."
    ):

        report = generate_report(
            attendance_summary.to_string()
        )

    st.markdown(report)

    # =================================================
    # ATTENDANCE GPT
    # =================================================

    st.subheader(
        "💬 AttendanceGPT"
    )

    question = st.chat_input(
        "Ask about attendance..."
    )

    if question:

        prompt = f"""
You are an AI Attendance Assistant.

Attendance Data:

{attendance_summary.to_string()}

Question:

{question}

Answer professionally.
"""

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        response = model.generate_content(
            prompt
        )

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            st.write(response.text)

    st.success(
        "Analysis Complete"
    )

    st.balloons()

else:

    st.info(
        "Upload an attendance Excel/CSV file to begin."
    )
