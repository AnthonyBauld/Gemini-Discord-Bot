# Gemini Discord Bot

This Discord bot uses the Gemini API (`gemini-1.5-flash-latest`) from Google to provide conversational responses, summarize PDF attachments, and acknowledge image uploads. It responds to mentions or replies, processes PDFs by summarizing their content, and notes unsupported image uploads or generation requests. The bot maintains conversation history per user and channel and logs errors to the console without persistent storage.

## Features
- **Text Responses**: Answers questions or processes text input using the Gemini API, with short responses (2-3 sentences, <350 chars) for simple questions (e.g., “What is AI?”) and detailed answers for complex queries (<2000 chars).
- **PDF Summarization**: Summarizes uploaded PDFs (up to 2000 chars for summarization) and uses the summary as context for responses.
- **Image Upload Handling**: Acknowledges uploaded images (`.jpg`, `.jpeg`, `.png`) with a placeholder response (analysis not supported).
- **Image Generation**: Not supported with `gemini-1.5-flash-latest`; responds with a placeholder message. Contact your administrator to enable a compatible Gemini model.
- **Conversation History**: Tracks per-user, per-channel history, limited to 8 message pairs (user + assistant) for context.
- **Typing Indicator**: Shows a typing indicator while processing responses.
- **Console-Only Logging**: Logs errors (e.g., API failures, PDF issues) to the console using `logging.ERROR`, with no disk storage.
- **Server Terminology**: Uses “server” instead of “guild” in logs and documentation for clarity.

## Setup Instructions

### Prerequisites
- **Python 3.8+**: Ensure Python is installed (`python --version` or `python3 --version`).
- **Discord Bot Token**: Create a bot at [Discord Developer Portal](https://discord.com/developers/applications).
- **Gemini API Key**: Obtain from Google at [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey).
- **GitHub Repository**: Clone or download this repository to your local machine.

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/gemini-discord-bot.git
   cd gemini-discord-bot
   ```

2. **Create and Configure `.env`**
   - Create a `.env` file in the project root (`/Users/anthonybauld/Desktop/Stuff/Gemini Discord Bot/`).
   - Add your Discord bot token and Gemini API key:
     ```env
     DISCORD_TOKEN=your_discord_bot_token
     GEMINI_API_KEY=your_gemini_api_key
     ```
   - Replace `your_discord_bot_token` with your bot’s token from the Discord Developer Portal.
   - Replace `your_gemini_api_key` with your API key from Google.
   - Example `.env`:
     ```env
     DISCORD_TOKEN=MTAzMjE2NjE3NjEyMzQ1Njc4.YcZx9w.ABC123xyz
     GEMINI_API_KEY=your_gemini_key
     ```
   - Save `.env` and keep it secure (excluded by `.gitignore`).

3. **Install Dependencies**
   ```bash
   pip install discord.py python-dotenv PyPDF2 google-generativeai
   ```
   - Ensure `pip` matches your Python version (try `pip3` or `python3 -m pip` if needed).
   - Dependencies:
     - `discord.py`: Discord API interaction.
     - `python-dotenv`: Load `.env` variables.
     - `PyPDF2`: PDF text extraction.
     - `google-generativeai`: Gemini API client.

4. **Run the Bot**
   ```bash
   cd "/Users/anthonybauld/Desktop/Stuff/Gemini Discord Bot"
   python bot.py
   ```
   - Or use `python3 bot.py` if required.
   - The bot will log in and start processing messages.

5. **Invite the Bot to Servers**
   - In the Discord Developer Portal, go to **OAuth2 > URL Generator**.
   - Select `bot` scope and the **Send Messages** permission.
   - Copy the generated URL and use it to invite the bot to your servers.
   - Ensure the bot has “Send Messages” permission in each server.

6. **Verify Bot Behavior**
   - Check console logs for startup:
     ```
     2025-05-18 21:39:45,123 - ERROR - 🤖 Logged in as Bot#1234
     ```
   - In Discord, test by:
     - Mentioning the bot: `@Bot What is AI?`
     - Replying to a bot message.
     - Uploading a PDF to summarize its content.
     - Uploading an image (e.g., `.jpg`) to see the placeholder response.
     - Requesting an image: `@Bot generate image of a cat` (expect unsupported message).
   - Confirm the bot shows a typing indicator and sends responses (text, summaries, or error messages).
   - Logs show errors only (e.g., “Gemini API error”, “PDF extraction error”).

## Usage
- **Text Queries**: Mention the bot (e.g., `@Bot`) or reply to its messages with questions or prompts.
  - Simple questions (e.g., “What is AI?”) get 2-3 sentence responses (<350 chars).
  - Complex queries get detailed answers (<2000 chars).
- **PDF Uploads**: Attach a PDF; the bot extracts text, summarizes it (up to 2000 chars), and uses the summary as context.
- **Image Uploads**: Upload `.jpg`, `.jpeg`, or `.png` files; the bot responds with “Image uploaded: [filename] (analysis not supported)”.
- **Image Generation**: Commands like “generate image of [description]” return “Image generation not supported with Gemini 1.5 Flash.” Use a compatible Gemini model for image generation (requires admin configuration).

## Troubleshooting
- **Bot Doesn’t Start**
  - Check `.env` for correct `DISCORD_TOKEN` and `GEMINI_API_KEY` at `/Users/anthonybauld/Desktop/Stuff/Gemini Discord Bot/.env`.
  - Verify dependencies: `pip install discord.py python-dotenv PyPDF2 google-generativeai`.
  - Ensure Python 3.8+: `python --version`.
  - Look for logs like “ValueError: Missing required environment variables”.

- **Bot Doesn’t Respond**
  - Check logs for “Gemini API error” (invalid API key, quota exceeded) or “PDF processing error”.
  - Ensure bot is mentioned (e.g., `@Bot`) or replied to.
  - Verify “Send Messages” permission in the server.
  - Test Gemini API with a simple script (see [Google AI Studio docs](https://makersuite.google.com/)).

- **PDF Summarization Fails**
  - Logs show “PDF extraction error” or “Could not extract text from PDF” if the PDF is empty or malformed.
  - Ensure the PDF has extractable text (not scanned images).
  - Try a different PDF; summarization is capped at 2000 chars.

- **Image Generation Unsupported**
  - Logs show no error; bot responds with “Image generation not supported.”
  - Confirm prompt starts with “generate/create/draw” and includes “image/picture/art” (e.g., “generate image of a cat”).
  - Contact your administrator to enable a Gemini model with image generation (e.g., Imagen).

- **Logs**
  - All logs are console-only, using `logging.ERROR`.
  - Example errors: “Gemini API error: Invalid API key”, “PDF extraction error: Invalid PDF structure”.
  - Note: Login uses `logger.error` (unusual for non-errors, as coded).

## Contributing
- Fork the repository and submit pull requests for improvements.
- Suggest features (e.g., image generation support, custom activity status).

## License
MIT License. See [LICENSE](LICENSE) for details.
