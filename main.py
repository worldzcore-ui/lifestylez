import feedparser
import os
import random
from groq import Groq
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# --- CONFIGURATION ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

RSS_FEEDS = [
    "https://www.tmz.com/rss.xml",
    "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", 
    "https://rss.nytimes.com/services/xml/rss/nyt/FashionandStyle.xml",
    "https://www.dailymail.co.uk/tvshowbiz/index.rss"
]

# --- BACKUP CONTENT (Shows if AI/RSS fails) ---
# This ensures your site is NEVER empty and always shows ads.
BACKUP_STORIES = [
    {
        "title": "Viral Shock: You Won't Believe What Just Happened!",
        "body": "The internet is going crazy over this leaked footage. Experts are baffled. Click to see the exclusive video before it gets taken down! 😱"
    },
    {
        "title": "Celebrity Secret Revealed in New Interview",
        "body": "Fans are shocked after hearing this confession. This changes everything we knew about the star. See the full details now. 👀"
    },
    {
        "title": "Top 10 Lifestyle Hacks Trending in the UK",
        "body": "These simple tricks are saving people thousands. Number 4 is absolutely genius. You have to try this today! 🔥"
    },
    {
        "title": "Mystery Event in USA Causes Social Media Storm",
        "body": "Everyone is talking about this strange occurrence. Is it real or a hoax? See the photos that have everyone debating. 🤔"
    }
]

client = Groq(api_key=GROQ_API_KEY)

def fetch_stories():
    print("Fetching news from RSS feeds...")
    stories = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            # Take top 1 from each feed
            for entry in feed.entries[:1]:
                stories.append({
                    "title": entry.title,
                    "summary": entry.summary if 'summary' in entry else entry.title,
                    "link": entry.link
                })
        except Exception as e:
            print(f"Failed to fetch {feed_url}: {e}")
    return stories

def ai_rewrite(story):
    """Uses Groq to make the story viral."""
    if not GROQ_API_KEY:
        return None
        
    prompt = f"""
    Rewrite this news into a short, exciting 2-sentence gossip snippet (max 30 words). 
    Make it click-bait style. Use emojis.
    
    Original: {story['title']}
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.7
        )
        content = completion.choices[0].message.content.strip().replace('"', '')
        return {
            "title": story['title'], 
            "body": content
        }
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def generate_html(stories):
    print(f"Generating HTML with {len(stories)} stories...")
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('index.html')
    
    output = template.render(
        stories=stories,
        last_updated=datetime.now().strftime("%B %d, %Y - %I:%M %p UTC")
    )
    
    with open('index.html', 'w') as f:
        f.write(output)
    print("index.html saved successfully!")

if __name__ == "__main__":
    final_stories = []
    
    # 1. Try to Fetch & Rewrite
    try:
        raw_stories = fetch_stories()
        random.shuffle(raw_stories)
        
        for story in raw_stories[:5]:
            rewritten = ai_rewrite(story)
            if rewritten:
                final_stories.append(rewritten)
    except Exception as e:
        print(f"Critical Error in fetch process: {e}")

    # 2. FAILSAFE: If list is empty, use BACKUP content
    if not final_stories:
        print("⚠️ AI/Fetch failed or Key missing. Using BACKUP content.")
        final_stories = BACKUP_STORIES
    
    # 3. Save
    generate_html(final_stories)
