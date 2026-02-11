import feedparser
import os
import random
from groq import Groq
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# --- CONFIGURATION ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# RSS Feeds (Mix of US/UK Lifestyle & Gossip)
RSS_FEEDS = [
    "https://www.tmz.com/rss.xml",
    "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", 
    "https://rss.nytimes.com/services/xml/rss/nyt/FashionandStyle.xml",
    "https://www.dailymail.co.uk/tvshowbiz/index.rss"
]

client = Groq(api_key=GROQ_API_KEY)

def fetch_stories():
    print("Fetching news from RSS feeds...")
    stories = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            # Take top 2 from each feed to get a good mix
            for entry in feed.entries[:2]:
                stories.append({
                    "title": entry.title,
                    "summary": entry.summary if 'summary' in entry else entry.title,
                    "link": entry.link
                })
        except Exception as e:
            print(f"Failed to fetch {feed_url}: {e}")
    return stories

def ai_rewrite(story):
    """Uses Groq to make the story viral and short."""
    prompt = f"""
    Rewrite this news into a short, exciting 2-sentence gossip snippet (max 40 words). 
    Make it sound like a viral tweet. Do not use hashtags.
    
    Original: {story['title']} - {story['summary']}
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.7
        )
        # Clean up output
        content = completion.choices[0].message.content.strip().replace('"', '')
        return {
            "title": story['title'], # Keep original title or ask AI to rewrite it too
            "body": content
        }
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def generate_html(stories):
    print("Generating HTML...")
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
    # 1. Fetch
    raw_stories = fetch_stories()
    random.shuffle(raw_stories)
    
    # 2. Process (Rewrite top 6 stories)
    final_stories = []
    for story in raw_stories[:6]:
        rewritten = ai_rewrite(story)
        if rewritten:
            final_stories.append(rewritten)
    
    # 3. Save
    if final_stories:
        generate_html(final_stories)
    else:
        print("No stories found. Skipping update.")
