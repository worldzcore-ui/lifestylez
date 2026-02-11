import feedparser
import os
import shutil
import re
from groq import Groq
from jinja2 import Environment, FileSystemLoader

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Configurations
RSS_FEEDS = [
    "https://www.tmz.com/rss.xml",
    "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
]

def clean_filename(title):
    """Converts a title into a filename: 'Viral News!' -> 'viral-news.html'"""
    s = re.sub(r'[^a-zA-Z0-9\s]', '', title).lower()
    return s.replace(' ', '-').strip()[:50] + ".html"

def fetch_content():
    stories = []
    print("Fetching feeds...")
    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed)
            for entry in parsed.entries[:4]: # Top 4 from each
                # AI Rewrite for better reading
                prompt = f"Rewrite this news into two parts. 1. A catchy intro (20 words). 2. A main body paragraph (50 words). Input: {entry.title} - {entry.summary}"
                try:
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama3-8b-8192"
                    )
                    content = chat.choices[0].message.content
                    
                    # Basic splitting (AI usually returns separate lines)
                    parts = content.split('\n')
                    intro = parts[0] if len(parts) > 0 else "Breaking News"
                    body = " ".join(parts[1:]) if len(parts) > 1 else entry.summary
                    
                    filename = clean_filename(entry.title)
                    stories.append({
                        "title": entry.title,
                        "intro": intro,
                        "body": body,
                        "filename": filename
                    })
                except Exception as e:
                    print(f"AI Error: {e}")
        except:
            pass
            
    # Fallback if feeds fail
    if not stories:
        stories.append({
            "title": "Welcome to Lifestylez",
            "intro": "The latest viral updates appear here.",
            "body": "We are currently updating our feed systems.",
            "filename": "welcome.html"
        })
    return stories

def build_site():
    env = Environment(loader=FileSystemLoader('templates'))
    stories = fetch_content()
    
    # 1. Setup Directories
    if os.path.exists('articles'):
        shutil.rmtree('articles')
    os.makedirs('articles')

    # 2. Generate Individual Article Pages
    template_article = env.get_template('article.html')
    for story in stories:
        with open(f"articles/{story['filename']}", 'w') as f:
            f.write(template_article.render(story=story))
    print(f"Generated {len(stories)} article pages.")

    # 3. Generate Main Pages (Index, News)
    template_home = env.get_template('home.html')
    
    # Index (Viral)
    with open('index.html', 'w') as f:
        f.write(template_home.render(stories=stories))
    
    # News Page (Can filter or show all)
    with open('news.html', 'w') as f:
        f.write(template_home.render(stories=stories))

    # 4. Generate Static Pages
    template_page = env.get_template('base.html') # Simplified for about/privacy
    # (You can expand this if you have specific templates for them)
    with open('about.html', 'w') as f:
        f.write(template_home.render(stories=[])) # Placeholder
    
    with open('games.html', 'w') as f:
         # Use your previous games template here if you saved it
         pass 

    print("Site build complete.")

if __name__ == "__main__":
    build_site()
