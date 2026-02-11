import feedparser
import os
import shutil
import re
from groq import Groq
from jinja2 import Environment, FileSystemLoader

# --- CONFIGURATION ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

RSS_FEEDS = [
    "https://www.tmz.com/rss.xml",
    "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/FashionandStyle.xml"
]

# --- CONTENT FOR STATIC PAGES ---
STATIC_CONTENT = {
    "about": {
        "title": "About Lifestylez",
        "body": """
            <h1 class='text-4xl font-bold mb-6 text-pink-500'>About Us</h1>
            <p class='text-xl mb-4'>Welcome to Lifestylez, the future of automated media.</p>
            <p class='text-gray-400'>Our AI-driven engine scans the globe 24/7 to bring you the latest viral hits, gaming news, and lifestyle trends before anyone else.</p>
            <p class='mt-6'>Contact us at: hello@lifestylez.ai</p>
        """
    },
    "privacy": {
        "title": "Privacy Policy",
        "body": """
            <h1 class='text-4xl font-bold mb-6 text-pink-500'>Privacy Policy</h1>
            <p class='mb-4'><strong>1. Data Collection:</strong> We do not store your personal data. We use third-party advertising partners who may use cookies.</p>
            <p class='mb-4'><strong>2. Content:</strong> All content on this site is generated for entertainment purposes.</p>
        """
    }
}

def clean_filename(title):
    s = re.sub(r'[^a-zA-Z0-9\s]', '', title).lower()
    return s.replace(' ', '-').strip()[:50] + ".html"

def fetch_content():
    stories = []
    print("Fetching feeds...")
    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed)
            for entry in parsed.entries[:2]: # Top 2 from each feed
                try:
                    # AI Rewriting
                    prompt = f"Rewrite this headline to be viral (max 10 words): {entry.title}. Then write a 50 word summary."
                    chat = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama3-8b-8192"
                    )
                    content = chat.choices[0].message.content
                    parts = content.split('\n')
                    title = parts[0].replace('"', '').strip()
                    body = " ".join(parts[1:]).strip()
                    
                    stories.append({
                        "title": title,
                        "intro": body[:100] + "...",
                        "body": body,
                        "filename": clean_filename(title),
                    })
                except Exception as e:
                    print(f"AI Error: {e}")
        except:
            pass
            
    # Fallback content to prevent empty site
    if not stories:
        stories = [
            {"title": "Viral Game Trends 2024", "intro": "Check this out...", "body": "Full story inside.", "filename": "viral-game.html"},
            {"title": "New Tech Shocking Experts", "intro": "You won't believe...", "body": "Read more.", "filename": "tech-shock.html"},
        ]
    return stories

def build_site():
    print("🚀 Building Site...")
    env = Environment(loader=FileSystemLoader('templates'))
    stories = fetch_content()
    
    # 1. SETUP FOLDERS
    if os.path.exists('articles'):
        shutil.rmtree('articles')
    os.makedirs('articles')

    # 2. GENERATE ARTICLE PAGES (Deep Links)
    # We pass path="../" so the nav knows to go back up a level
    template_article = env.get_template('article.html')
    for story in stories:
        with open(f"articles/{story['filename']}", 'w') as f:
            f.write(template_article.render(
                story=story, 
                path="../", 
                active_page="news"
            ))

    # 3. GENERATE HOME (Index)
    template_home = env.get_template('home.html')
    with open('index.html', 'w') as f:
        f.write(template_home.render(
            stories=stories, 
            path="", 
            active_page="home"
        ))
        
    # 4. GENERATE NEWS
    with open('news.html', 'w') as f:
        f.write(template_home.render(
            stories=stories, 
            path="", 
            active_page="news"
        ))

    # 5. GENERATE GAMES
    # Check if games.html template exists, otherwise use base/home
    try:
        template_games = env.get_template('games.html')
        with open('games.html', 'w') as f:
            f.write(template_games.render(
                path="", 
                active_page="games"
            ))
    except:
        print("⚠️ games.html template not found. Please create it.")

    # 6. GENERATE STATIC PAGES (About, Privacy)
    # We reuse a simple page template or base
    template_page = env.get_template('base.html') 
    # Create a simple "page.html" structure on the fly using inheritance if needed, 
    # but here we will just inject content into the base "content" block if you have a page.html.
    # To keep it simple, let's assume you have a 'page.html' template. 
    # If not, we will create a simple generic file write:
    
    for page, data in STATIC_CONTENT.items():
        # Using a simple HTML structure for static pages
        html_content = f"""
        {{% extends "base.html" %}}
        {{% block content %}}
        <div class="max-w-3xl mx-auto px-4 py-12">
            <div class="bg-gray-900 border border-gray-800 p-8 rounded-2xl">
                {data['body']}
            </div>
        </div>
        {{% endblock %}}
        """
        # Save this temporary template and render it
        with open(f'templates/temp_{page}.html', 'w') as f:
            f.write(html_content)
            
        temp_template = env.get_template(f'temp_{page}.html')
        with open(f'{page}.html', 'w') as f:
            f.write(temp_template.render(path="", active_page=page))
            
        os.remove(f'templates/temp_{page}.html') # Cleanup

    print("✅ Site Generation Complete. All pages connected.")

if __name__ == "__main__":
    build_site()
