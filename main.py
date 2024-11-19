from serpapi import GoogleSearch
import config
import os
from datetime import datetime
import time

def save_results(query, results):
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{query.replace(' ', '_')}_{timestamp}.txt"
    filepath = os.path.join(config.RESULTS_FOLDER, filename)
    
    # Save results to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Search Query: {query}\n")
        f.write(f"Search Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, result in enumerate(results[:config.MAX_RESULTS], 1):
            f.write(f"{i}. {result['title']}\n")
            f.write(f"   Link: {result['link']}\n")
            if 'snippet' in result:
                f.write(f"   Description: {result['snippet']}\n")
            f.write("\n")
    
    return filepath

def display_results(results):
    print(f"\nTop {config.MAX_RESULTS} Results:\n")
    for i, result in enumerate(results[:config.MAX_RESULTS], 1):
        print(f"{i}. {result['title']}")
        print(f"   Link: {result['link']}")
        if 'snippet' in result:
            print(f"   Description: {result['snippet']}")
        print()

def check_for_rss(url):
    """Enhanced check for RSS/Atom feeds with multiple detection methods."""
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, urlparse
    
    def is_valid_url(url):
        """Check if URL is valid and not a javascript or mailto link."""
        if not url:
            return False
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.scheme in ('http', 'https')
    
    def normalize_url(base_url, link):
        """Convert relative URLs to absolute URLs."""
        if not link:
            return None
        # Handle protocol-relative URLs
        if link.startswith('//'):
            return f'https:{link}'
        # Convert relative to absolute URL
        return urljoin(base_url, link)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rss_links = set()
        
        # 1. Check <link> tags for RSS/Atom feeds
        for link in soup.find_all('link'):
            if link.get('type') in [
                'application/rss+xml',
                'application/atom+xml',
                'application/rdf+xml',
                'application/xml',
                'text/xml'
            ]:
                href = normalize_url(url, link.get('href'))
                if href and is_valid_url(href):
                    rss_links.add(href)
        
        # 2. Check <a> tags with common RSS-related patterns
        rss_keywords = [
            'rss', 'feed', 'atom', 'syndication', 'xml', 'subscribe',
            'subscription', 'news feed', 'newsfeed', 'blog feed',
            'podcast', 'rdf', 'really simple syndication'
        ]
        
        for a in soup.find_all('a'):
            href = a.get('href', '')
            text = a.get_text().lower()
            
            # Check both href and text content
            if any(keyword in href.lower() or keyword in text for keyword in rss_keywords):
                full_url = normalize_url(url, href)
                if full_url and is_valid_url(full_url):
                    rss_links.add(full_url)
        
        # 3. Check common RSS feed paths
        common_paths = [
            '/feed',
            '/rss',
            '/atom',
            '/feeds',
            '/rss.xml',
            '/atom.xml',
            '/feed.xml',
            '/index.xml',
            '/blog/feed',
            '/blog/rss',
            '/news/feed',
            '/feed/rss',
            '/feed/atom',
            '/rss/feed',
            '/feed.rss',
            '/comments/feed',
            '/rss/news',
            '/blog.atom'
        ]
        
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        for path in common_paths:
            potential_feed = normalize_url(base_url, path)
            try:
                feed_response = requests.head(potential_feed, headers=headers, timeout=5)
                if feed_response.status_code == 200:
                    rss_links.add(potential_feed)
            except:
                continue
        
        # 4. Check for WordPress API endpoints
        if '/wp-content/' in response.text or '/wp-includes/' in response.text:
            wp_feeds = [
                '/feed/',
                '/comments/feed/',
                '/?feed=rss2',
                '/?feed=atom',
                '/wp-feed.php'
            ]
            for feed in wp_feeds:
                wp_feed_url = normalize_url(base_url, feed)
                try:
                    feed_response = requests.head(wp_feed_url, headers=headers, timeout=5)
                    if feed_response.status_code == 200:
                        rss_links.add(wp_feed_url)
                except:
                    continue
        
        # Filter out invalid URLs and duplicates
        valid_links = {link for link in rss_links if is_valid_url(link)}
        
        # Verify each link is actually an RSS feed
        confirmed_feeds = set()
        for link in valid_links:
            try:
                feed_response = requests.get(link, headers=headers, timeout=5)
                content_type = feed_response.headers.get('content-type', '').lower()
                if any(x in content_type for x in ['xml', 'rss', 'atom']) or \
                   any(x in feed_response.text.lower()[:1000] for x in ['<rss', '<feed', '<?xml']):
                    confirmed_feeds.add(link)
            except:
                continue
        
        return list(confirmed_feeds)
        
    except Exception as e:
        print(f"Error checking RSS for {url}: {str(e)}")
        return []

def save_rss_results(query, rss_links):
    """Save found RSS links to a file."""
    if not rss_links:
        return
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rss_{query.replace(' ', '_')}_{timestamp}.txt"
    filepath = os.path.join(config.RESULTS_FOLDER, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"RSS Links for: {query}\n")
        f.write(f"Search Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for link in rss_links:
            f.write(f"{link}\n")
    
    print(f"RSS links saved to: {filepath}")

def perform_search(query=None):
    # Get search query from user if not provided
    if query is None:
        query = input(config.SEARCH_PROMPT)
    
    # Set up the search parameters
    params = {
        "api_key": config.SERPAPI_KEY,
        "q": query,
        **config.SEARCH_CONFIG
    }
    
    try:
        # Perform the search
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check for news results specifically
        if "news_results" not in results:
            print(config.ERROR_NO_RESULTS)
            return
        
        news_results = results["news_results"]
        
        # Display results
        display_results(news_results)
        
        # Save results
        filepath = save_results(query, news_results)
        print(config.SAVE_SUCCESS.format(filepath))
        
        # Check for RSS feeds
        print("\nChecking for RSS feeds...")
        all_rss_links = []
        for result in news_results[:config.MAX_RESULTS]:
            rss_links = check_for_rss(result['link'])
            if rss_links:
                all_rss_links.extend(rss_links)
                print(f"Found RSS feed(s) at: {result['link']}")
        
        if all_rss_links:
            save_rss_results(query, all_rss_links)
        else:
            print("No RSS feeds found.")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_search_terms():
    """Read search terms from search_terms.txt file."""
    with open('data/search_terms.txt', 'r') as file:
        # Read lines and remove empty lines and whitespace
        terms = [line.strip() for line in file.readlines() if line.strip()]
    return terms

def main():
    print(config.WELCOME_MESSAGE)
    
    # Get search terms from file
    search_terms = get_search_terms()
    
    if not search_terms:
        print(config.ERROR_NO_TERMS)
        return
        
    # Process each search term
    for term in search_terms:
        print(f"\nProcessing search term: {term}")
        perform_search(term)
        time.sleep(2)  # Add delay between searches to avoid rate limiting
    
    print("\nAll searches completed!")

if __name__ == "__main__":
    main() 