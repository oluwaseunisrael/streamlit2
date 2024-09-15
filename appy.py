import streamlit as st
from analysis import clean_text, tokenize_and_filter, analyze_emotions, sentiment_analysis, plot_emotions
from database import create_comments_table, insert_comment, get_all_comments, create_users_table, insert_user, authenticate_user, reset_password
from datetime import datetime

# Create the database tables if they don't exist
create_users_table()
create_comments_table()

# Initialize the session state variables if not already present
if 'page' not in st.session_state:
    st.session_state.page = "Login"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Horizontal navigation bar
if st.session_state.logged_in:
    st.markdown(
        """
        <style>
        div[data-testid="stHorizontalBlock"] > div:first-child {
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    nav_options = st.columns([1, 1, 1])
    with nav_options[0]:
        if st.button("Home", key="nav_home"):
            st.session_state.page = "Home"
    with nav_options[1]:
        if st.button("Feedback", key="nav_feedback"):
            st.session_state.page = "Feedback"
    with nav_options[2]:
        if st.button("About Us", key="nav_about"):
            st.session_state.page = "About Us"
else:
    if st.session_state.page not in ["Login", "Register", "Reset Password"]:
        nav_options = st.columns([1, 1])
        with nav_options[0]:
            if st.button("Login", key="nav_login"):
                st.session_state.page = "Login"
        with nav_options[1]:
            if st.button("Register", key="nav_register"):
                st.session_state.page = "Register"

# Page Content
if st.session_state.page == "Login":
    st.title("Login")
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')

    if st.button("Login", key="login_button"):
        if not username or not password:
            st.error("Please provide both username and password.")
        else:
            user = authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.page = "Home"
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

    if st.button("Forgot Password?", key="forgot_password_button"):
        st.session_state.page = "Reset Password"
        st.experimental_rerun()

    if st.button("Register", key="login_register_button"):
        st.session_state.page = "Register"
        st.experimental_rerun()

elif st.session_state.page == "Register":
    st.title("Register")
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    email = st.text_input('Email')

    if st.button("Register", key="register_button"):
        if not username or not password or not email:
            st.error("Please fill out all fields.")
        else:
            insert_user(username, password, email)
            st.success("User registered successfully! Please login.")
            st.session_state.page = "Login"
            st.experimental_rerun()

    if st.button("Back to Login", key="register_back_button"):
        st.session_state.page = "Login"
        st.experimental_rerun()

elif st.session_state.page == "Reset Password":
    st.title("Reset Password")
    username = st.text_input('Username')
    new_password = st.text_input('New Password', type='password')

    if st.button("Reset Password", key="reset_password_button"):
        if not username or not new_password:
            st.error("Please provide both username and new password.")
        else:
            reset_password(username, new_password)
            st.success("Password reset successfully! Please login.")
            st.session_state.page = "Login"
            st.experimental_rerun()

    if st.button("Back to Login", key="reset_back_button"):
        st.session_state.page = "Login"
        st.experimental_rerun()

elif st.session_state.page == "Home" and st.session_state.get('logged_in'):
    st.title("Welcome to Route Based Road")
    st.subheader("Leave your comment for others to assess the road")

    name = st.text_input('Name', 'Enter Your Name!')
    comment = st.text_area("Comment", value="Enter your comment here")
    origin_city = st.text_input('Origin City', 'Enter your origin city')
    origin_area = st.text_input('Origin Area', 'Enter your origin area')
    destination_city = st.text_input('Destination City', 'Enter your destination city')
    destination_area = st.text_input('Destination Area', 'Enter your destination area')

    if st.button("Submit", key="submit_comment_button"):
        if not name or not comment or not origin_city or not origin_area or not destination_city or not destination_area:
            st.error("Please fill out all fields.")
        else:
            cleansed_text = clean_text(comment)
            final_words = tokenize_and_filter(cleansed_text)
            emotions = analyze_emotions(final_words)
            sentiment = sentiment_analysis(cleansed_text)

            st.write(f"Sentiment: {sentiment.capitalize()}")

            insert_comment(name, comment, sentiment, origin_city, origin_area, destination_city, destination_area)
            st.write("Comment submitted successfully!")

            st.session_state.page = "Feedback"
            st.experimental_rerun()

elif st.session_state.page == "Feedback" and st.session_state.get('logged_in'):
    st.title("Feedback")
    st.subheader("Read comments from others")

    comments = get_all_comments()

    for comment in comments:
        # Name
        st.write(f"Name: {comment[1]}")
        # Comment
        st.write(f"Comment: {comment[2]}")
        # Sentiment
        st.write(f"Sentiment: {comment[3].capitalize()}")
        # Route
        st.write(f"Route: {comment[4]} ({comment[5]}) to {comment[6]} ({comment[7]})")

        if len(comment) > 8 and comment[8]:
            timestamp = datetime.strptime(comment[8], '%Y-%m-%d %H:%M:%S')
            st.write(f"Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"Formatted Date: {timestamp.strftime('%B %d, %Y')}")

        # Emotion Analysis
        cleansed_text = clean_text(comment[2])
        final_words = tokenize_and_filter(cleansed_text)
        emotion_counts = analyze_emotions(final_words)

        fig = plot_emotions(emotion_counts)
        st.pyplot(fig)

        st.write("---")

elif st.session_state.page == "About Us" and st.session_state.get('logged_in'):
    st.title("About Us")
    st.write("About us content")
