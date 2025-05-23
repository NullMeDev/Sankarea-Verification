import yaml
import feedparser
import requests
from datetime import datetime, timedelta
import sys
import json
import os
from pathlib import Path
import pytz

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

def generate_markdown_report(results):
    """Generate a markdown report of valid sources"""
    markdown = [
        "# Valid RSS Sources\n",
        f"Last updated: {results['timestamp']} UTC\n",
        "\n## Summary\n",
        f"- Total Sources: {results['summary']['total']}\n",
        f"- Working Sources: {results['summary']['working']}\n",
        f"- Failed Sources: {results['summary']['failed']}\n\n",
        "## Working Sources by Category\n"
    ]

    # Group working sources by category
    categories = {}
    for feed in results['feeds']:
        if feed['working']:
            category = feed['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(feed)

    # Add each category and its working sources
    for category in sorted(categories.keys()):
        markdown.append(f"\n### {category}\n")
        for feed in sorted(categories[category], key=lambda x: x['name']):
            markdown.append(f"- [{feed['name']}]({feed['url']})\n")

    return ''.join(markdown)

def should_update_sources():
    """Check if we should update the sources list (every 7 days)"""
    try:
        with open('last_source_update.txt', 'r') as f:
            last_update = datetime.fromisoformat(f.read().strip())
        return datetime.now(pytz.UTC) - last_update >= timedelta(days=7)
    except FileNotFoundError:
        return True

def update_sources_timestamp():
    """Update the timestamp of the last sources update"""
    with open('last_source_update.txt', 'w') as f:
        f.write(datetime.now(pytz.UTC).isoformat())

def main():
    results = {
        "timestamp": datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S"),
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

    # Generate and update markdown report if needed
    if should_update_sources():
        markdown_content = generate_markdown_report(results)
        with open('VALID_SOURCES.md', 'w') as f:
            f.write(markdown_content)
        update_sources_timestamp()

    # Exit with error if any feeds failed
    if results['summary']['failed'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
