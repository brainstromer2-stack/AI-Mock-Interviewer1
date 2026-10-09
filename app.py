import streamlit as st
import cv2
from modules.cv_engine import analyze_posture_and_emotion
from modules.nlp_engine import listen_and_transcribe, evaluate_candidate_answer

# Set wide layout for side-by-side view
st.set_page_config(layout="wide", page_title="AI Mock Interviewer")

st.title("🤖 AI Multimodal Mock Interviewer")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Interview Settings")
    job_role = st.selectbox(
        "Select Target Role", 
        ["Cyber Security Analyst", "Python Developer", "Electronics/IoT Engineer", "Data Scientist"]
    )
    
    # Reset interview state
    if st.button("Restart Interview"):
        st.session_state.chat_history = []
        st.rerun()

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_q" not in st.session_state:
    st.session_state.current_q = f"Tell me about yourself and your experience relevant to a {job_role} role."

# --- Layout Setup ---
col1, col2 = st.columns([1, 1.2])

# --- Left Column: Computer Vision & Live Feed ---
with col1:
    st.subheader("Live Analysis (CV & Posture)")
    run_video = st.checkbox("Turn on Camera")
    FRAME_WINDOW = st.image([])
    
    # Placeholders for live metrics so they update cleanly
    metric_posture = st.empty()
    metric_emotion = st.empty()

    if run_video:
        camera = cv2.VideoCapture(0)
        while run_video:
            ret, frame = camera.read()
            if not ret:
                st.error("Failed to access webcam.")
                break
                
            # Analyze frame
            posture, emotion = analyze_posture_and_emotion(frame)
            
            # Display metrics live
            metric_posture.markdown(f"**Posture:** {posture}")
            metric_emotion.markdown(f"**Dominant Emotion:** {emotion}")
            
            # Convert BGR (OpenCV format) to RGB (Streamlit format)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame)
            
        camera.release()

# --- Right Column: NLP, Speech & Chat ---
with col2:
    st.subheader("Interview Interface")
    
    # Display the current question
    st.info(f"**Interviewer:** {st.session_state.current_q}")
    
    if st.button("🎤 Click to Speak Answer", use_container_width=True):
        with st.spinner("Listening... (Speak clearly into your microphone)"):
            user_text = listen_and_transcribe()
            
            if user_text and not user_text.startswith("Error"):
                st.success(f"**You:** {user_text}")
                
                # Evaluate the answer using Gemini
                with st.spinner("Analyzing response..."):
                    feedback = evaluate_candidate_answer(
                        st.session_state.current_q, 
                        user_text, 
                        job_role
                    )
                    
                    # Save to history
                    st.session_state.chat_history.append({
                        "Role": job_role,
                        "Q": st.session_state.current_q, 
                        "A": user_text, 
                        "Feedback": feedback
                    })
            else:
                st.error(user_text) # Displays the specific error caught by the try/except block

    # Display Chat/Feedback History
    if st.session_state.chat_history:
        st.markdown("### 📊 AI Feedback History")
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Q: {chat['Q']} (Role: {chat['Role']})", expanded=(i==0)):
                st.write(f"**Your Answer:** {chat['A']}")
                st.markdown(chat['Feedback'])