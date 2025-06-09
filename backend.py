import requests
import webbrowser
from datetime import datetime
import httpx
from bs4 import BeautifulSoup

# Replace with your actual API key, model, and referer
API_KEY = "YOUR_API_KEY"
MODEL = "deepseek/deepseek-chat-v3-0324:free"  # Or any other
REFERER = "siddharthshetty161616@gmail.com"

# Talk to AI
def ask_ai(prompt, chat_history):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": REFERER
    }

    messages = chat_history + [{"role": "user", "content": prompt}]
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={"model": MODEL, "messages": messages}
        )
        result = response.json()

        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"]
        else:
            return "❌ No valid response from AI."
    except Exception as e:
        return f"❌ Error talking to AI: {str(e)}"

# Site shortcuts
SITE_MAP = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "stack overflow": "https://stackoverflow.com",
    "chatgpt": "https://chat.openai.com"
}

# Check if user wants to open a site
def check_and_open_site(user_input: str) -> bool:
    user_input = user_input.lower()
    for name, url in SITE_MAP.items():
        if any(kw in user_input for kw in [f"open {name}", f"go to {name}", f"launch {name}"]):
            webbrowser.open(url)
            return True
    return False

def check_and_return_datetime(user_input: str) -> str | None:
    user_input = user_input.lower()
    
    if "time" in user_input and any(word in user_input for word in ["what", "current", "now", "tell"]):
        return datetime.now().strftime(" The current time is %I:%M %p")

    if "date" in user_input and any(word in user_input for word in ["what", "today", "current", "tell"]):
        return datetime.now().strftime(" Today's date is %A, %B %d, %Y")

    if "date and time" in user_input or "time and date" in user_input:
        return datetime.now().strftime(" %A, %B %d, %Y —  %I:%M %p")

    return None

# for web search from duckduck go
async def web_search_duckduckgo(query: str) -> str:
    try:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("a", class_="result__a", limit=3)

        if not results:
            return "Sorry, I couldn't find any relevant results."

        reply = "Here’s what I found on the web:\n"
        for result in results:
            title = result.text.strip()
            link = result['href']
            reply += f"- [{title}]({link})\n"
        return reply
    except Exception as e:
        return f"Web search failed: {e}"