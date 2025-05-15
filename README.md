# Gemini 1.5 Flash Discord Bot

This Discord bot uses Google's Gemini 1.5 Flash model to answer user prompts when the bot is mentioned in chat. It supports conversational memory, PDF reading, and can be extended to handle images and videos.

---

## 🧱 Requirements

- Python 3.9+
- A Discord bot token (from [Discord Developer Portal](https://discord.com/developers/applications))
- A Google Gemini API key (from [Google AI Studio](https://studio.google.ai))
- `pip` (Python package installer)
  
---

## ⚙️ Setup Instructions

1. Create a `.env` file in the same directory with the following content:

    ```
    DISCORD_TOKEN=your-discord-bot-token-here
    GEMINI_API_KEY=your-gemini-api-key-here
    ```

2. Install dependencies:

    ```
    pip install discord.py google-generativeai python-dotenv PyPDF2
    ```

    *Optional:* Save dependencies to `requirements.txt`:

    ```
    pip freeze > requirements.txt
    ```

3. Run the bot:

    ```
    python bot.py
    ```

---

## 💡 Usage

Mention the bot in any server where it has permission. Example:


The bot will:

- Respond using Gemini 1.5 Flash
- Retain short conversation history
- Read and respond to PDF content in the same message
- (Optionally) support images and videos if extended

---

## 🧠 Features

- ✅ Gemini 1.5 Flash API support via `google-generativeai`
- ✅ Remembers recent conversation context (user-specific or global)
- ✅ Supports PDF document upload and answering within one message
- ✅ Environment-based secrets using `.env`
- ✅ Outputs concise but informative answers
- ✅ Gracefully handles quota, length, and format errors

---

## ⚠️ Troubleshooting

| Error                      | Solution                                           |
|----------------------------|---------------------------------------------------|
| API quota exceeded          | You’ve hit your Gemini limit. Check Google AI Console |
| content must be 2000 or fewer in length | Message too long. Gemini limits apply. Keep user prompts short. |
| ModuleNotFoundError        | Run pip install commands again or check your Python environment |
| Bot doesn’t reply          | Ensure MESSAGE CONTENT INTENT is enabled in Discord Dev Portal |

---

## 🚀 Extensions (Ideas)

- Handle image and video files using Gemini's multimodal support
- Add slash command support (`/ask`)
- Use persistent file-backed memory (SQLite or JSON store)
- Add rate limiting or moderation filters

---

## 🔐 Notes

Keep your `.env` file secret. Never upload it to GitHub or any public space.

