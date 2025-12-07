# gui_chatbot_launcher.py
import tkinter as tk
from tkinter import scrolledtext
from chatbot.chatbot import respond
# to test without Gemini API access, uncomment the next line :
# from chatbot.test_chatbot_sansGemini import respond


# ----------------------
# Interface graphique Tkinter
# ----------------------
def send_question():
    question = entry.get()
    if question.strip() == "":
        return
    chat_window.config(state=tk.NORMAL)
    chat_window.insert(tk.END, f"Vous: {question}\n")
    entry.delete(0, tk.END)
    response = respond(question)
    chat_window.insert(tk.END, f"Chatbot: {response}\n\n")
    chat_window.config(state=tk.DISABLED)
    chat_window.yview(tk.END)

root = tk.Tk()
root.title("Chatbot Médical - Gemini")

chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=25, state=tk.DISABLED)
chat_window.pack(padx=10, pady=10)

entry = tk.Entry(root, width=60)
entry.pack(side=tk.LEFT, padx=10, pady=10)
entry.bind("<Return>", lambda event: send_question())

send_button = tk.Button(root, text="Envoyer", command=send_question)
send_button.pack(side=tk.LEFT, padx=5)

root.mainloop()
