from langchain_pipeline.chatbot_efficient import respond

print("Chatbot médical (Gemini + Neo4j)")
while True:
    user_input = input("Question: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    print("Réponse:", respond(user_input))
