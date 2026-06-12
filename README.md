# 🕵️ Murder Mystery Detective Game

This project is an interactive Murder Mystery game where players act as detectives to solve a museum diamond theft.

## 🚀 Setup & Requirements

To run this application locally, you need Python installed along with the following library:

```bash
pip install streamlit
```

### API Key Configuration
The game uses AI to generate dynamic mysteries. Initially, I attempted to use the **Gemini API**, but due to technical compatibility issues and integration hurdles during development, the project was switched to use the **Groq API** (running Llama 3 models) for more reliable JSON generation.

**To use the AI features:**
1. Visit [Groq Console](https://console.groq.com/) and create a free API key.
2. Set it as an environment variable:
   - **Windows:** `setx GROK_API_KEY "your_key_here"`
   - **Mac/Linux:** `export GROK_API_KEY="your_key_here"`
3. Alternatively, if running via Streamlit, add it to `.streamlit/secrets.toml`.

*Note: If no API key is provided, the game will automatically fall back to a built-in "Museum Diamond Theft" case.*

## 🎮 How to Play
You can run the game in two ways:
1. **Terminal Version:** `python Main.py`
2. **Web Version (Recommended):** `streamlit run streamlit_app.py`

## 📂 Project Structure
- `streamlit_app.py`: The modern web-based UI.
- `Main.py`: The original command-line version.