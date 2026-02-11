import feedparser
import os
import random
from groq import Groq
from datetime import datetime
from email.utils import parsedate_to_datetime

# --- CONFIGURATION ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/FashionandStyle.xml", # US Lifestyle
    "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",      # UK Gossip
    "https://www.tmz.com/rss.xml"                                       # Viral Gossip
]

client = Groq(api_key=GROQ_API_KEY)

def fetch_stories():
    """Fetches top stories from RSS feeds."""
    stories = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]: # Get top 2 from each to mix it up
                stories.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.summary if 'summary' in entry else entry.title,
                    "published": entry.published
                })
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
    return stories

def rewrite_story(story):
    """Uses Groq to rewrite the story for 'Mr Universe' style."""
    prompt = f"""
    Act as a viral content writer for a site called 'Mr Universe'.
    Rewrite the following news story into a short, punchy, gossip-style summary (max 100 words).
    Use emojis. Make the title click-baity.
    
    Original Title: {story['title']}
    Original Summary: {story['summary']}
    
    Output format:
    TITLE: [New Title]
    BODY: [New Body]
    """
    
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        content = completion.choices[0].message.content
        
        # Simple parsing (You might need to adjust this based on actual output)
        lines = content.split('\n')
        new_title = lines[0].replace("TITLE:", "").strip()
        new_body = "\n".join(lines[1:]).replace("BODY:", "").strip()
        
        return {"title": new_title, "body": new_body, "orig_link": story['link']}
    except Exception as e:
        print(f"Error rewriting story: {e}")
        return None

def update_html(new_stories):
    """(Placeholder) We will add the HTML generation in Stage 2"""
    print(f"Generated {len(new_stories)} new stories.")
    # Here is where we will inject the Monetag link.

if __name__ == "__main__":
    raw_stories = fetch_stories()
    # Shuffle to mix US and UK news
    random.shuffle(raw_stories)
    
    processed_stories = []
    # Process only the top 3 to save API calls
    for story in raw_stories[:3]: 
        new_story = rewrite_story(story)
        if new_story:
            processed_stories.append(new_story)
            
    update_html(processed_stories)
