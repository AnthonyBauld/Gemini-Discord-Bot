# Import libraries needed for the Discord bot
import os                  # For accessing environment variables
import discord            # Discord API library for bot functionality
import google.generativeai as genai  # For Gemini API text generation
from dotenv import load_dotenv  # To load environment variables from .env
import io                 # For handling PDF file bytes
import PyPDF2            # For extracting text from PDF files
import logging           # For logging errors to console
import re                # For regex pattern matching
from collections import defaultdict  # For per-user/channel conversation history

# Configure logging for error tracking
logging.basicConfig(
    level=logging.ERROR,  # Log only errors for minimal output
    format='%(asctime)s - %(levelname)s - %(message)s',  # Include timestamp
    handlers=[logging.StreamHandler()]  # Output to console only
)
logger = logging.getLogger(__name__)  # Create logger instance

# Load environment variables from .env file
load_dotenv()

# Bot configuration using environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # Discord bot token
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Gemini API key

# Validate environment variables
if not DISCORD_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Missing required environment variables")

# Initialize Gemini API client
genai.configure(api_key=GEMINI_API_KEY)  # Set up Gemini API key
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")  # Use Gemini 1.5 Flash model

# Define constants for bot configuration
MAX_HISTORY_LENGTH = 8  # Max number of message pairs (user + assistant)
DISCORD_MAX_CHARS = 2000  # Max characters for Discord messages

# Set up Discord client with required intents
intents = discord.Intents.default()  # Use default intents
intents.message_content = True      # Enable message content access
intents.messages = True             # Enable message events
intents.guilds = True              # Enable server access
intents.members = True             # Enable member access
client = discord.Client(intents=intents)  # Create Discord client

# Track conversation history per user and channel
conversation_history = defaultdict(list)  # Store messages by user_channel key

# Utility function: Split long messages for Discord
def split_message(text, limit=2000):
    """Split text into chunks up to limit chars for Discord messages."""
    return [text[i:i+limit] for i in range(0, len(text), limit)]

# Utility function: Detect simple questions
def is_simple_question(content: str) -> bool:
    """Identify short or simple questions for brief responses."""
    content = content.lower().strip()
    # Consider short messages (<10 words) as simple
    if len(content.split()) < 10:
        return True
    # Check for simple question starters
    simple_keywords = ['what is', 'who is', 'when is', 'where is', 'how many', 'define']
    return any(content.startswith(keyword) for keyword in simple_keywords)

# Utility function: Detect image generation requests
def is_image_generation_request(content: str) -> bool:
    """Check if the message is an image generation request."""
    # Use regex to match 'generate/create/draw' + 'image/picture/art'
    return bool(re.search(r'^(generate|create|draw)\s+.*\b(image|picture|art)\b', content, re.IGNORECASE))

# Utility function: Extract text from PDF
def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file bytes."""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))  # Read PDF from bytes
        full_text = ""
        # Extract text from each page
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
        return full_text.strip() or None  # Return None if empty
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return None

# Utility function: Summarize PDF text with Gemini
def summarize_text(text):
    """Generate a brief summary of text using Gemini API."""
    try:
        summary_prompt = (
            "Summarize the following document briefly, focusing on main points:\n\n" + text[:2000]
        )
        response = model.generate_content(summary_prompt)  # Call Gemini API
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini summarization error: {e}")
        return None

# Utility function: Build prompt with history
def build_prompt(history, user_prompt, is_simple):
    """Construct prompt with system message, history, and user input."""
    context_messages = [{
        "role": "system",
        "content": (
            "You are a helpful assistant. Provide clear and complete answers. "
            "For simple questions, respond in 2-3 sentences under 350 chars. "
            "For others, use a natural length, not too short or overly long."
        ) if is_simple else (
            "You are a helpful assistant. Provide clear and complete answers with a natural length—"
            "not too short, but not overly long. Aim for a balanced, informative response."
        )
    }]
    # Add recent history (up to MAX_HISTORY_LENGTH pairs)
    context_messages.extend(history[-MAX_HISTORY_LENGTH * 2:])
    context_messages.append({"role": "user", "content": user_prompt})
    # Combine messages into a single prompt
    combined_prompt = ""
    for msg in context_messages:
        if msg["role"] == "system":
            combined_prompt += f"System: {msg['content']}\n"
        elif msg["role"] == "user":
            combined_prompt += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            combined_prompt += f"Assistant: {msg['content']}\n"
    return combined_prompt

# Discord event: Handle bot startup
@client.event
async def on_ready():
    """Run when bot connects to Discord."""
    logger.error(f"🤖 Logged in as {client.user}")  # Log successful login

# Discord event: Handle incoming messages
@client.event
async def on_message(message):
    """Process messages when bot is mentioned or replied to."""
    if message.author.bot:
        return  # Ignore messages from bots

    # Create unique key for conversation history
    history_key = f"{message.author.id}_{message.channel.id}"
    prompt = message.content.strip()
    should_process = False

    # Check for bot mention
    if client.user.mentioned_in(message):
        prompt = prompt.replace(f"<@{client.user.id}>", "").strip()
        should_process = True
    # Check for reply to bot
    elif message.reference and message.reference.resolved and message.reference.resolved.author == client.user:
        should_process = True

    # Handle file attachments
    pdf_summary = None
    for attachment in message.attachments:
        if attachment.filename.lower().endswith(".pdf"):
            try:
                # Read PDF bytes
                file_bytes = await attachment.read()
                pdf_text = extract_text_from_pdf(file_bytes)
                if not pdf_text:
                    await message.channel.send("Could not extract text from PDF.")
                    return
                # Summarize PDF with Gemini
                pdf_summary = summarize_text(pdf_text)
                if not pdf_summary:
                    await message.channel.send("Failed to summarize PDF content.")
                    return
                break
            except Exception as e:
                logger.error(f"PDF processing error: {e}")
                await message.channel.send(f"Error processing PDF: {e}")
                return
        elif attachment.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            # Note image upload (no analysis)
            prompt = f"Image uploaded: {attachment.filename} (analysis not supported)"
            should_process = True
            break

    # Process valid messages
    if should_process and prompt:
        async with message.channel.typing():  # Show typing indicator
            if is_image_generation_request(prompt):
                # Placeholder for image generation (unsupported in Gemini 1.5 Flash)
                await message.channel.send(
                    "Image generation not supported with Gemini 1.5 Flash. "
                    "Contact administrator to enable a compatible model."
                )
                conversation_history[history_key].extend([
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": "Image generation not supported."}
                ])
            else:
                # Prepend PDF summary to prompt if available
                full_prompt = (
                    f"Context from attached PDF document:\n{pdf_summary}\n\nUser question:\n{prompt}"
                ) if pdf_summary else prompt

                # Build prompt with history and system message
                is_simple = is_simple_question(prompt)
                combined_prompt = build_prompt(conversation_history[history_key], full_prompt, is_simple)

                try:
                    # Query Gemini API
                    response = model.generate_content(combined_prompt)
                    reply = response.text.strip()

                    # Update conversation history
                    conversation_history[history_key].extend([
                        {"role": "user", "content": full_prompt},
                        {"role": "assistant", "content": reply}
                    ])
                    # Truncate history to MAX_HISTORY_LENGTH pairs
                    if len(conversation_history[history_key]) > MAX_HISTORY_LENGTH * 2:
                        conversation_history[history_key][:] = conversation_history[history_key][-MAX_HISTORY_LENGTH * 2:]

                    # Send response, split into chunks if needed
                    chunks = split_message(reply, DISCORD_MAX_CHARS)
                    for chunk in chunks:
                        await message.channel.send(chunk)

                except Exception as e:
                    logger.error(f"Gemini API error: {e}")
                    if "quota" in str(e).lower() or "rate" in str(e).lower():
                        await message.channel.send("Gemini API quota exceeded. Try again later.")
                    else:
                        await message.channel.send(f"Error with Gemini API: {e}")

# Run the bot with Discord token
client.run(DISCORD_TOKEN)
