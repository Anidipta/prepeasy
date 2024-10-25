import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time
import subprocess 
def install_requirements():
    try:
        with open('requirements.txt') as f:
            required_packages = f.read().splitlines()
        
        for package in required_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            except subprocess.CalledProcessError as e:
                st.error(f"Failed to install package {package}: {e}")
    except Exception as e:
        st.error(f"Error reading requirements.txt: {e}")

def create_connection(db_file='database.db'):
    return sqlite3.connect(db_file)

def fetch_user_profile(roll_number):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, password FROM users WHERE roll_number=?", (roll_number,))
    profile = cursor.fetchone()
    conn.close()
    return profile

def update_user_password(roll_number, new_password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE roll_number = ?", (new_password, roll_number))
    conn.commit()
    conn.close()

def profiles(user_info):
    st.markdown("## 💬 User Profile")
    
    if user_info:
        name = user_info.get("name", "")
        roll_number = user_info.get("roll_number", "")
        st.subheader(f"**Name:** {name}")
        st.subheader(f"**Roll Number:** {roll_number}")

    st.markdown("### Change Password")
    new_password = st.text_input("New Password", type='password')
    
    if st.button("Update Password"):
        if new_password:
            update_user_password(roll_number, new_password)
            st.success("Password updated successfully!")
        else:
            st.error("Password cannot be empty.")

# Function to connect to the database
def connect_db(db_name='question.db'):
    conn = sqlite3.connect(db_name)
    return conn

# Function to retrieve questions based on paper code and year
def get_questions(paper_code, year):
    conn = connect_db()
    query = "SELECT * FROM questions WHERE course_code = ? AND year = ?"
    questions = pd.read_sql(query, conn, params=(paper_code, year))
    conn.close()
    return questions

# Save results to the database
def save_results(date, paper_code, year, correct_count, missed_count, wrong_count):
    conn = connect_db('test.db')
    conn.execute("""CREATE TABLE IF NOT EXISTS test_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_time TEXT,
                        subject TEXT,
                        year TEXT,
                        correct_answer INTEGER,
                        missed INTEGER,
                        wrong INTEGER
                    )""")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO test_records (date_time, subject, year, correct_answer, missed, wrong) VALUES (?, ?, ?, ?, ?, ?)", 
                 (timestamp, paper_code, year, correct_count, missed_count, wrong_count))
    conn.commit()
    conn.close()

# Main function to display the quiz
def show_quiz():
    st.title("Quiz Application")
    
    # CSS for styling
    st.markdown("""<style>
                    .stButton > button {
                        border: none;
                        text-align: center;
                        margin: 4px 2px;
                    }
                    </style>""", unsafe_allow_html=True)

    paper_code = st.sidebar.selectbox("Select Paper Code", ["CHEM1001"])
    year = st.sidebar.selectbox("Select Year", ["2014"])

    questions = get_questions(paper_code, year)
    if questions.empty:
        st.error("No questions found for the selected paper code and year.")
        return

    if "question_index" not in st.session_state:
        st.session_state.question_index = 0
        st.session_state.user_answers = {}
        st.session_state.start_time = time.time()  # Start timer when quiz begins

    question_index = st.session_state.question_index
    if question_index < len(questions):
        row = questions.iloc[question_index]

        st.header(f"Question {question_index + 1}: {row['question']}")
        option_selected = st.radio(
            "Select an option:",
            options=[row['option_a'], row['option_b'], row['option_c'], row['option_d']],
            index=0 if question_index not in st.session_state.user_answers else
            [row['option_a'], row['option_b'], row['option_c'], row['option_d']].index(st.session_state.user_answers[question_index]),
            key=question_index
        )
        if option_selected:
            st.session_state.user_answers[question_index] = option_selected

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("Previous") and question_index > 0:
            st.session_state.question_index -= 1
    with col3:
        if question_index == 9:  
            if st.button("Finish"):
                st.session_state.question_index += 1
        elif st.button("Next") and question_index < len(questions) - 1:
            st.session_state.question_index += 1

    # Analysis after finishing
    if question_index == len(questions) - 1 and st.session_state.question_index == len(questions):
        correct_count = 0
        total_questions = len(st.session_state.user_answers)
        missed_count = 0
        wrong_count = 0

        for idx, answer in st.session_state.user_answers.items():
            row = questions.iloc[idx]
            correct_answer_index = int(row['c'])  # Ensure this retrieves the index of the correct answer (1-based)
            correct_answer = row[['option_a', 'option_b', 'option_c', 'option_d']].iloc[correct_answer_index - 1]  # Adjust for 0-based indexing

            if answer == correct_answer:
                correct_count += 1
            elif answer:  
                wrong_count += 1
            else:  # If no answer was provided
                missed_count += 1

        # Calculate total time taken
        total_time_taken = time.time() - st.session_state.start_time
        save_results(datetime.now(), paper_code, year, correct_count, missed_count, wrong_count)

        # Display results
        st.success(f"You answered {correct_count} out of {total_questions} questions correctly!")
        st.write(f"Total Time Taken: {total_time_taken:.2f} seconds")
        st.write(f"Missed Questions: {missed_count}")
        st.write(f"Wrong Answers: {wrong_count}")
        st.balloons()  # Display balloons animation
        
        chart_data = pd.DataFrame({
            'Result': ['Correct', 'Missed', 'Wrong'],
            'Count': [correct_count, missed_count, wrong_count]
        })

        # Display a bar chart of quiz results
        st.bar_chart(chart_data.set_index('Result'))
        # Reset session state for the next quiz
        st.session_state.question_index = 0  
        st.session_state.user_answers = {}  # Clear user answers

def load_data():
    # Connect to SQLite database and load data into a DataFrame
    conn = sqlite3.connect('test.db')
    query = "SELECT * FROM test_records"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def show_score_analysis():
    st.markdown("## 📊 Score Analysis")
    st.write("Analyze your performance and scores over time.")

    # Load data
    df = load_data()

    # Convert `date_time` to a datetime format
    df['date_time'] = pd.to_datetime(df['date_time'])
    
    # 1. Donut Chart for Subject Distribution
    st.markdown("### 1. Subject Distribution")
    subject_counts = df['subject'].value_counts()
    fig1, ax1 = plt.subplots(figsize=(7, 7))
    ax1.pie(subject_counts, labels=subject_counts.index, autopct='%1.1f%%', startangle=90, wedgeprops={'width':0.3})
    ax1.set_title("Subjects Attempted Distribution")
    st.pyplot(fig1)

    # 2. Time Series for Correct Answers Over Time
    st.markdown("### 2. Correct Answers Over Time")
    correct_answers_time = df.groupby('date_time')['correct_answer'].sum().reset_index()
    st.line_chart(data=correct_answers_time.set_index('date_time')['correct_answer'])

    # 3. Descriptive Analysis of Performance by Subject
    st.markdown("### 3. Descriptive Analysis of Performance by Subject")
    subject_summary = df.groupby('subject')[['correct_answer', 'missed', 'wrong']].mean().reset_index()
    for index, row in subject_summary.iterrows():
        st.write(f"- **{row['subject']}**: On average, there were {row['correct_answer']:.2f} correct answers, "
                 f"{row['missed']:.2f} missed answers, and {row['wrong']:.2f} wrong answers per test.")

    # 4. Bar Chart for Performance Breakdown
    st.markdown("### 4. Overall Performance Breakdown")
    performance_totals = df[['correct_answer', 'missed', 'wrong']].sum()
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.bar(performance_totals.index, performance_totals.values, color=['#1f77b4', '#ff7f0e', '#d62728'])
    ax2.set_title("Total Correct, Missed, and Wrong")
    st.pyplot(fig2)

    # 5. Time Series: Correct vs Missed vs Wrong
    st.markdown("### 5. Correct vs Missed vs Wrong Over Time")
    performance_time = df.groupby('date_time').sum().reset_index()
    st.area_chart(data=performance_time.set_index('date_time')[['correct_answer', 'missed', 'wrong']])

# Define the main function
def get_past_question_papers():
    data = {
        "Subject": [
            "Mathematics", "Mathematics", "Mathematics", "Mathematics", "Mathematics", 
            "Chemistry", "Chemistry", "Chemistry", "Chemistry", "Chemistry", 
            "Electrical Engineering", "Electrical Engineering", "Electrical Engineering", 
            "Electrical Engineering", "Electrical Engineering", 
            "Mechanical Engineering", "Mechanical Engineering", "Mechanical Engineering", 
            "Mechanical Engineering", "Mechanical Engineering"
        ],
        "Year": [
            "2014", "2015", "2016", "2017", "2018", 
            "2014", "2015", "2016", "2017", "2018", 
            "2014", "2015", "2016", "2017", "2018", 
            "2014", "2015", "2016", "2017", "2018"
        ],
        "Paper": [
            "MATH1101 2014", "MATH1101 2015", "MATH1101 2016", "MATH1101 2017", "MATH1101 2018",
            "CHEM1001 2014", "CHEM1001 2015", "CHEM1001 2016", "CHEM1001 2017", "CHEM1001 2018",
            "ELEC1001 2014", "ELEC1001 2015", "ELEC1001 2016", "ELEC1001 2017", "ELEC1001 2018",
            "MECH1101 2014", "MECH1101 2015", "MECH1101 2016", "MECH1101 2017", "MECH1101 2018"
        ],
        "Link": [
            "pyq/MATH1101_2014.pdf", "pyq/MATH1101_2015.pdf", "pyq/MATH1101_2016.pdf", 
            "pyq/MATH1101_2017.pdf", "pyq/MATH1101_2018.pdf", 
            "pyq/CHEM1001_2014.pdf", "pyq/CHEM1001_2015.pdf", "pyq/CHEM1001_2016.pdf", 
            "pyq/CHEM1001_2017.pdf", "pyq/CHEM1001_2018.pdf",
            "pyq/ELEC1001_2014.pdf", "pyq/ELEC1001_2015.pdf", "pyq/ELEC1001_2016.pdf", 
            "pyq/ELEC1001_2017.pdf", "pyq/ELEC1001_2018.pdf",
            "pyq/MECH1101_2014.pdf", "pyq/MECH1101_2015.pdf", "pyq/MECH1101_2016.pdf", 
            "pyq/MECH1101_2017.pdf", "pyq/MECH1101_2018.pdf"
        ]
    }
    df = pd.DataFrame(data)

    year = st.sidebar.selectbox("Filter by Year", ["All Years", "2014", "2015", "2016", "2017", "2018", "2019"])
    subject_filter = st.sidebar.selectbox("Filter by Subject", ["All Subjects"] + df["Subject"].unique().tolist())

    if year != "All Years":
        df = df[df["Year"] == year]

    if subject_filter != "All Subjects":
        df = df[df["Subject"] == subject_filter]

    subjects = df["Subject"].unique()
    for subject in subjects:
        st.header(f"{subject} Papers 🎓")
        subject_papers = df[df["Subject"] == subject]
        
        for _, row in subject_papers.iterrows():
            with st.expander(f"{row['Paper']} 📝"):
                st.markdown(f"**Year:** {row['Year']}")
                
                # Create buttons for download
                pdf_path = row['Link']
                try:
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="Download PDF ⬇️",
                            data=pdf_file,
                            file_name=pdf_path.split('/')[-1],
                            mime='application/pdf'
                        )
                except FileNotFoundError:
                    st.error("PDF file not found!")

# Connect to the database and fetch students count
def get_student_count():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    student_count = cursor.fetchone()[0]
    conn.close()
    return student_count

# Connect to test.db and fetch upcoming tests
def get_upcoming_tests():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        SELECT subject, year, date_time
        FROM test_records
        WHERE date_time > ?
    ''', (current_datetime,))
    tests = cursor.fetchall()
    conn.close()
    return tests

def delete_test(test_id):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM test_records WHERE id = ?", (test_id,))
    conn.commit()
    conn.close()
    
def show_overview():
    st.markdown("## Dashboard Overview")
    
    # Fetch upcoming tests and count them
    upcoming_tests = get_upcoming_tests()
    total_upcoming_tests = len(upcoming_tests)

    # Fetch total student count
    student_count = get_student_count()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📝 Upcoming Tests")
        st.info(f"{total_upcoming_tests} Upcoming Tests")
        st.write("Prepare for upcoming tests with our comprehensive resources and practice materials!")
        
        st.markdown("#### 📚 Study Materials")
        st.write("Access a variety of study guides, notes, and video tutorials tailored for your courses.")

    with col2:
        st.markdown("### 👨‍🎓 Students Enrolled")
        st.success(f"{student_count} Students")
        st.write("Join our growing community of learners with over 50 students currently enrolled.")
        st.markdown("### ⭐ High Achievers")
        st.warning("Top Scorers")
        st.write("Meet our outstanding students excelling in various subjects!")

    # Data Visualization Placeholder
    st.markdown("### 📊 Performance Overview")
    st.line_chart([1, 2, 3, 4, 5])  # Replace with actual performance data

    # Display Upcoming Tests Details
    st.markdown("### 📅 Upcoming Tests Details")

    # Convert upcoming tests to a DataFrame for easier manipulation
    df_tests = pd.DataFrame(upcoming_tests, columns=['Subject', 'Year', 'Date'])
    df_tests['Date'] = pd.to_datetime(df_tests['Date'])  # Ensure date is in datetime format

    if not df_tests.empty:
        unique_years = df_tests['Date'].dt.year.unique()
        unique_months = df_tests['Date'].dt.month_name().unique()

        # Sidebar filters
        selected_year = st.selectbox("Select Year", sorted(unique_years, reverse=True))
        selected_month = st.selectbox("Select Month", unique_months)

        # Filter DataFrame based on selected year and month
        filtered_tests = df_tests[
            (df_tests['Date'].dt.year == selected_year) &
            (df_tests['Date'].dt.month_name() == selected_month)
        ]

        # Display the first 4 filtered tests in a boxed layout
        st.markdown("### Filtered Upcoming Tests:")
        if not filtered_tests.empty:
            num_tests_to_display = min(3, len(filtered_tests))  # Display a maximum of 4 tests
            for i in range(num_tests_to_display):
                test = filtered_tests.iloc[i]
                st.markdown(f"**Subject:** {test['Subject']}  \n**Year:** {test['Year']}  \n**Date:** {test['Date'].strftime('%Y-%m-%d %H:%M')}")
                st.markdown("---")
        else:
            st.write("No upcoming tests for the selected year and month.")
    else:
        st.write("No upcoming tests available.")
    # FAQs Section
    faqs = {
        "What types of tests can I prepare for on this platform?": "Our platform offers a wide variety of tests, including standardized exams, competitive exams, and subject-specific assessments.",
        "How do I access the practice tests?": "To access the practice tests, simply create an account or log in. Navigate to the 'Tests' section.",
        "Is there a fee for accessing the practice materials?": "While many resources are free, some premium content may require a subscription.",
        "How are the questions structured in the practice tests?": "Our practice tests consist of multiple-choice questions (MCQs).",
        "Can I track my progress?": "Yes! Our platform allows you to track your performance over time.",
        "Are there any resources for exam strategies or tips?": "Absolutely! We provide various resources on effective exam strategies.",
        "How often are new tests added?": "We continuously update our database with new tests and resources.",
        "Can I suggest new features or tests?": "We welcome feedback! Please reach out through the contact page.",
        "What should I do if I encounter technical issues?": "Visit our support page or contact our technical support team.",
        "How can I contact customer support?": "You can contact our customer support team via the 'Contact Us' section."
    }

    st.markdown("### ❓ Frequently Asked Questions")

    for question, answer in faqs.items():
        with st.expander(question):
            st.write(answer)
    
def create_database(db_file='database.db'):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_number TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    ''')
    conn.commit()
    conn.close()

create_database()

def signup(conn, name, roll_number, password):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE roll_number = ?", (roll_number,))
    if cursor.fetchone():
        st.error("Roll number already exists. Please Login.")
        return False
    cursor.execute("INSERT INTO users (name, roll_number, password) VALUES (?, ?, ?)", 
                   (name, roll_number, password))
    conn.commit()
    return True

def check_credentials(conn, roll_number, password):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE roll_number = ? AND password = ?", 
                   (roll_number, password))
    return cursor.fetchone()

st.set_page_config(page_title="Interactive Dashboard", layout="wide", initial_sidebar_state="expanded")
install_requirements()
conn = create_connection()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'current_section' not in st.session_state:
    st.session_state.current_section = 'Overview'

if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

if not st.session_state.logged_in:
    choice = st.sidebar.selectbox("Login/Signup", ["Login", "Signup"])
    if choice == "Login":
        roll_number = st.text_input("Roll Number")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            user = check_credentials(conn, roll_number, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_info = {"name": user[1], "roll_number": roll_number}
                st.session_state.current_section = 'Overview'
                st.success("Logged in successfully!")
            else:
                st.error("Invalid roll number or password.")
    elif choice == "Signup":
        with st.form("signup_form"):
            name = st.text_input("Name")
            roll_number = st.text_input("Roll Number")
            password = st.text_input("Password", type='password')
            confirm_password = st.text_input("Confirm Password", type='password')
            if st.form_submit_button("Sign Up"):
                if password != confirm_password:
                    st.error("Passwords do not match.")
                elif not any(char.isdigit() for char in password) or not any(char in '!@#$%^&*()_+' for char in password):
                    st.error("Password must contain at least 1 number and 1 special character.")
                else:
                    if signup(conn, name, roll_number, password):
                        st.success("Signup successful! Please log in.")
else:
    for button_text, section in {"Overview 📝": "Overview", "Question Papers 📑": "Question Papers",
                                 "Score Analysis 📊": "Score Analysis", "Quizzes 📋": "Quizzes",
                                 "Profile 💬": "Profile"}.items():
        if st.sidebar.button(button_text):
            st.session_state.current_section = section

    current_section = st.session_state.current_section
    if current_section == 'Overview':
        show_overview()
    elif current_section == 'Question Papers':
        get_past_question_papers()
    elif current_section == 'Score Analysis':
        show_score_analysis()
    elif current_section == 'Quizzes':
        show_quiz()
    elif current_section == 'Profile':
        profiles(st.session_state.user_info)

st.sidebar.markdown(f"#### Current Time: {datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')}")
