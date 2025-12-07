from flask import Flask, render_template, request, jsonify
from chatbot.test_chatbot_sansGemini import respond  

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    if question.strip() == "":
        return jsonify({"answer": "Veuillez poser une question."})
    answer = respond(question)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
