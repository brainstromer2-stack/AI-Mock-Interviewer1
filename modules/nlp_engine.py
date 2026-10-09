import speech_recognition as sr
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configure Gemini with the API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def listen_and_transcribe():
    """Listens to the microphone and converts speech to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Adjust for ambient noise to improve accuracy
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            # Listen for up to 10 seconds of speech
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)
            text = recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return "Error: Listening timed out. Please try speaking again."
        except sr.UnknownValueError:
            return "Error: Could not understand the audio. Please speak clearly."
        except sr.RequestError as e:
            return f"Error: Could not request results; {e}"
        except Exception as e:
            return f"Error: {e}"

def evaluate_candidate_answer(question, answer, job_role):
    """Passes the Q&A to Gemini to evaluate technical accuracy and communication."""
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    You are a strict but fair expert technical interviewer evaluating a candidate for a {job_role} position.
    
    Interview Question: "{question}"
    Candidate's Answer: "{answer}"
    
    Evaluate the candidate's answer and format your response strictly with the following headers:
    
    **1. Knowledge Accuracy (1-10):** [Score and brief justification]
    **2. Communication Clarity:** [Assess how well they explained their thoughts]
    **3. What Was Missing:** [Key concepts or keywords they failed to mention]
    **4. Ideal Response Summary:** [1-2 sentences on how a top candidate would answer]
    
    Keep the tone professional and constructive.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Failed to generate feedback due to an API error: {e}"