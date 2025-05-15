import os
import discord
import google.generativeai as genai
from dotenv import load_dotenv
import io
import PyPDF2  # for PDF text extraction

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

shared_history = []
MAX_HISTORY_LENGTH = 8  # Number of message pairs (user + assistant)

def split_message(text, limit=2000):
    return [text[i:i+limit] for i in range(0, len(text), limit)]

def extract_text_from_pdf(file_bytes):
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
        return full_text.strip()
    except Exception as e:
        print(f"[PDF Extraction Error] {e}")
        return None

def summarize_text(text):
    try:
        summary_prompt = (
            "Summarize the following document briefly, focusing on main points:\n\n" + text[:2000]
        )
        response = model.generate_content(summary_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[Gemini Summarization Error] {e}")
        return None

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # Check if message mentions the bot
    if client.user.mentioned_in(message):
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()
        pdf_summary = None

        # Check if there's a PDF attached
        pdf_attachments = [att for att in message.attachments if att.filename.lower().endswith(".pdf")]

        if pdf_attachments:
            # For simplicity, take only the first PDF if multiple attached
            pdf_bytes = await pdf_attachments[0].read()
            pdf_text = extract_text_from_pdf(pdf_bytes)
            if not pdf_text:
                await message.channel.send("Could not extract text from PDF.")
                return

            pdf_summary = summarize_text(pdf_text)
            if not pdf_summary:
                await message.channel.send("Failed to summarize PDF content.")
                return

        # If there's a PDF summary, prepend it to the prompt so the model can use it immediately
        if pdf_summary:
            full_prompt = (
                "Context from attached PDF document:\n" + pdf_summary + "\n\n"
                "User question:\n" + prompt
            )
        else:
            full_prompt = prompt

        context_messages = [{
            "role": "system",
            "content": (
                "You are a helpful assistant. Provide clear and complete answers with a natural length—"
                "not too short, but not overly long. Aim for a balanced, informative response."
            )
        }]

        recent_history = shared_history[-MAX_HISTORY_LENGTH * 2:]
        context_messages.extend(recent_history)
        context_messages.append({"role": "user", "content": full_prompt})

        combined_prompt = ""
        for msg in context_messages:
            if msg["role"] == "system":
                combined_prompt += f"System: {msg['content']}\n"
            elif msg["role"] == "user":
                combined_prompt += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                combined_prompt += f"Assistant: {msg['content']}\n"

        try:
            response = model.generate_content(combined_prompt)
            reply = response.text.strip()

            shared_history.append({"role": "user", "content": full_prompt})
            shared_history.append({"role": "assistant", "content": reply})

            if len(shared_history) > MAX_HISTORY_LENGTH * 2:
                shared_history[:] = shared_history[-MAX_HISTORY_LENGTH * 2:]

            chunks = split_message(reply)
            for chunk in chunks:
                await message.channel.send(chunk)

        except Exception as e:
            print(f"[Gemini API Error] {e}")
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                await message.channel.send("Gemini API quota exceeded. Try again later.")
            else:
                await message.channel.send("Error with Gemini API.")

client.run(DISCORD_TOKEN)
