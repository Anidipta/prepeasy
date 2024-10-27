# 📝 Prepe@sy - Student Exam Preparation Platform

**Prepe@sy** is a web application designed to help students prepare for exams by offering a vast collection of practice questions, insightful analytics, and a user-friendly interface. The platform is built using **Streamlit** and utilizes multiple databases to manage and track users' progress.

🌐 **[Visit Prepe@sy](https://prepeasy.streamlit.app/)**

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Streamlit

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/prepeasy.git
   cd prepeasy
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   ```bash
   streamlit run All.py
   ```

## 🛠️ Tools & Technologies Used

- **Streamlit:** For building the web interface.
- **SQLite:** For managing databases (`database.db`, `profile.db`, `question.db`, `test.db`).
- **Python:** Core programming language for backend logic.

## 📋 Features

- **📚 Question Practice:** Students can access and practice questions sorted by subject and year.
- **📊 Analytics:** Provides detailed insights to help students track their progress.
- **🖥️ User-Friendly Interface:** Designed for easy navigation and a seamless user experience.
- **🔍 Efficient Search:** Students can quickly find the papers they need.
- **📅 Progress Tracking:** Allows users to see their improvement over time.

## 🧩 Methodology

1. **Database Connection:** The app establishes connections to multiple SQLite databases using functions like `create_connection` and `connect_db`, ensuring smooth data access.
2. **User Management:** Functions such as `signup`, `fetch_user_profile`, and `check_credentials` handle user registration, login, and profile retrieval securely.
3. **Quiz System:** The app retrieves and displays questions using `get_questions` and `show_quiz`, allowing users to practice by subject and year.
4. **Result Saving & Analysis:** After quizzes, `save_results` stores user performance, and `show_score_analysis` generates detailed insights, helping users track progress.
5. **Administrative Control:** Functions like `delete_test` and `get_student_count` allow for efficient management and monitoring of quizzes and user data.
6. **Data Initialization & Handling:** `create_database` and `load_data` ensure databases are set up and data is managed efficiently across sessions.
7. **User-Friendly Interface:** Built with Streamlit, the platform offers an intuitive and easy-to-navigate UI for students to enhance their exam preparation.

## 🏃‍♂️ Usage

1. **Navigating the Dashboard:** The dashboard offers a centralized view of your study progress, providing easy access to practice questions and analytics.
2. **Selecting Questions:** Choose questions by subject or year, and start practicing. You can filter them based on difficulty and other criteria.
3. **Tracking Performance:** After each quiz, get detailed feedback on your performance, including strengths and areas for improvement.

## 📑 Databases

- **`database.db`:** Stores general app data and configurations.
- **`profile.db`:** Handles user profile data including login information.
- **`question.db`:** Contains all questions, categorized by subject and year, along with correct answers.
- **`test.db`:** Used for testing purposes to validate app features without affecting the main databases.

## 🧪 Testing

Make sure the `test.db` is correctly set up for testing features. Run tests to verify the functionality of different modules.

## 📝 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## 🤝 Contributing

We welcome contributions! If you’d like to improve the app, please fork the repository and create a pull request.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.
