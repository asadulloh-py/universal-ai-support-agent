import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant"
)

conversation_history = {}

SYSTEM_PROMPT = """You are a professional AI customer support agent for a business.
Your responsibilities:
- Answer customer questions clearly and professionally
- Remember conversation context
- Always be polite and helpful
- Respond in the same language the customer uses"""

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    conversation_history[user_id].append({
        "role": "user",
        "content": user_message
    })
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history[user_id])
    
    response = llm.invoke(messages)
    reply = response.content
    
    conversation_history[user_id].append({
        "role": "assistant", 
        "content": reply
    })
    
    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    print("AI Support Agent is running...")
    app.run_polling()

if __name__ == "__main__":
    main()