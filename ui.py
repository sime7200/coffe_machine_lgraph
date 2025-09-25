import gradio as gr
from app import app  # il grafo compilato
from memory import init_db

# inizializza memoria (una volta sola)
init_db()
USER_ID = "anon"

def coffee_chat(user_input, history):
    """
    Questa funzione viene chiamata da Gradio
    """
    if user_input.lower() in ("exit", "quit"):
        return history + [[user_input, "Arrivederci!"]]

    # execution of the graph
    state = app.invoke({"order": user_input, "user_id": USER_ID})
    msg = state.get("message", "⚠️ Errore: nessuna risposta generata.")

    # update chat (quets, repl)
    return history + [[user_input, msg]]


with gr.Blocks() as demo:
    gr.Markdown("# ☕ Smart Coffee Machine")
    chatbot = gr.Chatbot(value=[[None, "Hello! I'm your virtual Barista. What would you like to order today?"]])
    txt = gr.Textbox(placeholder="Write your order or ask a question...")

    txt.submit(coffee_chat, [txt, chatbot], chatbot)
    # clear box after submit
    txt.submit(lambda: "", None, txt)
    

if __name__ == "__main__":
    demo.launch()
