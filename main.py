import feedparser
import os
import random
from groq import Groq
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# --- CONTENT SOURCES ---
RSS_FEEDS = [
    "https://www.tmz.com/rss.xml",
    "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", 
    "https://www.dailymail.co.uk/tvshowbiz/index.rss"
]

STATIC_PAGES = {
    "about": {
        "title": "About Lifestylez",
        "content": "<p>Lifestylez is an AI-driven media platform dedicated to bringing you the fastest, most viral content from across the globe. Our automated systems scan thousands of sources every hour to curate the trends that matter.</p><p>Founded in 2024, we aim to redefine how news is consumed in the digital age.</p>"
    },
    "privacy": {
        "title": "Privacy Policy",
        "content": "<p><strong>1. Data Collection:</strong> We do not collect personal data directly. Third-party advertisers (Monetag) may use cookies.</p><p><strong>2. Usage:</strong> By using this site, you agree to our terms. Content is generated automatically.</p>"
    }
}

def fetch_and_rewrite():
    """Fetches real news and rewrites it."""
    stories = []
    print("Fetching news...")
    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed)
            for entry in parsed.entries[:2]: # Top 2 from each
                # Rewrite logic
                prompt = f"Rewrite this headline to be catchy/viral (max 10 words): {entry.title}. Then write a 20 word summary."
                try:
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama3-8b-8192"
                    )
                    content = chat.choices[0].message.content
                    stories.append({"title": entry.title, "body": content}) # Storing original title for Image Gen accuracy
                except:
                    stories.append({"title": entry.title, "body": "Click to read more about this trending story."})
        except Exception as e:
            print(f"Feed Error: {e}")
            
    # Fallback if empty
    if not stories:
        stories = [{"title": "Viral Trend Detected", "body": "Users are going crazy over this new lifestyle hack."}] * 6
        
    return stories

def build_site():
    env = Environment(loader=FileSystemLoader('templates'))
    stories = fetch_and_rewrite()
    
    # 1. Build Index (Viral)
    print("Building Index...")
    template_home = env.get_template('home.html')
    with open('index.html', 'w') as f:
        f.write(template_home.render(stories=stories))

    # 2. Build News/Blog (Same content for now, different layout potential)
    print("Building Blog...")
    with open('blog.html', 'w') as f:
        f.write(template_home.render(stories=stories)) # Reusing home layout for blog for now
        
    with open('news.html', 'w') as f:
        f.write(template_home.render(stories=stories))

    # 3. Build Games
    print("Building Games...")
    template_games = env.get_template('games.html')
    with open('games.html', 'w') as f:
        f.write(template_games.render())

    # 4. Build Static Pages (About, Privacy)
    print("Building Static Pages...")
    template_page = env.get_template('page.html')
    
    for page_name, data in STATIC_PAGES.items():
        with open(f'{page_name}.html', 'w') as f:
            f.write(template_page.render(title=data['title'], content=data['content']))

    print("🎉 Site Generation Complete!")

if __name__ == "__main__":
    build_site()
