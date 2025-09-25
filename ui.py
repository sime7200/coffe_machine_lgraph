import gradio as gr
from app import app 
from memory import init_db
import pyttsx3 # text to speech
import speech_recognition as sr # speech to text

init_db()
USER_ID = "anon"

def coffee_chat(user_input, history):
    """
    Called by Gradio when user submits a text input.
    """
    if user_input.lower() in ("exit", "quit"):
        return history + [[user_input, "Goodbye!"]]

    # execution of the graph
    state = app.invoke({"order": user_input, "user_id": USER_ID})
    msg = state.get("message", "⚠️ Errore: nessuna risposta generata.")

    # update chat (quets, repl)
    return history + [[user_input, msg]]


def speech_to_text(audio_path):
    if not audio_path:
        return ""
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio, language="en-US")
    except Exception as e:
        return f"Error: {e}"


def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return text


with gr.Blocks() as demo:
    gr.Markdown("# ☕ Smart Coffee Machine")
    chatbot = gr.Chatbot(value=[[None, "Hello! I'm your virtual Barista. What would you like to order today?"]])
    txt = gr.Textbox(placeholder="Write your order or ask a question...")
    btn_talk = gr.Button("🔊 Respond with voice")

    audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Or speak your order:")

    def handle_audio(audio_path, history):
        if not audio_path:
            return history
        text = speech_to_text(audio_path)
        if not text:
            return history + [["(no speech)", "⚠️ No audio detected."]]
        state = app.invoke({"order": text, "user_id": "anon"})
        msg = state.get("message", "⚠️ Errore: nessuna risposta generata.")
        return history + [[text, msg]]
    
    audio_input.change(handle_audio, [audio_input, chatbot], chatbot)

    txt.submit(coffee_chat, [txt, chatbot], chatbot)
    # clear box after submit
    txt.submit(lambda: "", None, txt)

    btn_talk.click(lambda h: text_to_speech(h[-1][1]) if h else "No response yet", [chatbot], None)
    

if __name__ == "__main__":
    demo.launch()
