import yaml
import feedparser
import requests
from datetime import datetime
import sys
import json

def load_sources(yaml_file):
    with open(yaml_file, 'r') as file:
        return yaml.safe_load(file)

def verify_rss_feed(url):
    try:
        feed = feedparser.parse(url)
        if feed.bozo:  # feedparser sets bozo to 1 if there's an error
            return False, f"Invalid RSS feed format: {feed.bozo_exception}"
        if not feed.entries:
            return False, "No entries found in feed"
        return True, "Feed is valid and contains entries"
    except Exception as e:
        return False, f"Error accessing feed: {str(e)}"

def main():
    results = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "feeds": [],
        "summary": {
            "total": 0,
            "working": 0,
            "failed": 0
        }
    }

    sources = load_sources('sources.yml')
    
    for source in sources['sources']:
        status, message = verify_rss_feed(source['url'])
        
        feed_result = {
            "name": source['name'],
            "url": source['url'],
            "category": source['category'],
            "working": status,
            "message": message
        }
        
        results['feeds'].append(feed_result)
        results['summary']['total'] += 1
        if status:
            results['summary']['working'] += 1
        else:
            results['summary']['failed'] += 1

    # Write results to file
    with open('feed_status.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Exit with error if any feeds failed
    if results['summary']['failed'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
