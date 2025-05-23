import yaml
import feedparser
import requests
from datetime import datetime, timedelta
import sys
import json
import os
from pathlib import Path
import pytz

def ensure_files_exist():
    """Ensure all required files exist"""
    # Create empty files if they don't exist
    Path('feed_status.json').touch(exist_ok=True)
    Path('VALID_SOURCES.md').touch(exist_ok=True)
    Path('status_badge.md').touch(exist_ok=True)
    Path('last_source_update.txt').touch(exist_ok=True)

def load_sources(yaml_file):
    """Load sources with error handling"""
    try:
        if not os.path.exists(yaml_file):
            print(f"Error: {yaml_file} not found")
            # Create a template sources.yml if it doesn't exist
            default_sources = {
                'sources': [
                    {
                        'name': 'Example Feed',
                        'url': 'https://example.com/feed.xml',
                        'category': 'Example',
                        'type': 'rss'
                    }
                ]
            }
            with open(yaml_file, 'w') as f:
                yaml.safe_dump(default_sources, f)
            return default_sources
        
        with open(yaml_file, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading sources: {str(e)}")
        return {'sources': []}

def verify_rss_feed(url):
    """Verify RSS feed with timeout and error handling"""
    try:
        # Add timeout to prevent hanging
        feed = feedparser.parse(url, timeout=10)
        
        if hasattr(feed, 'status'):
            if feed.status >= 400:
                return False, f"HTTP Error: {feed.status}"
        
        if feed.bozo:
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
        if not os.path.exists('last_source_update.txt'):
            return True
            
        with open('last_source_update.txt', 'r') as f:
            content = f.read().strip()
            if not content:  # Handle empty file
                return True
            last_update = datetime.fromisoformat(content)
        return datetime.now(pytz.UTC) - last_update >= timedelta(days=7)
    except Exception as e:
        print(f"Error checking update time: {str(e)}")
        return True

def update_sources_timestamp():
    """Update the timestamp of the last sources update"""
    try:
        with open('last_source_update.txt', 'w') as f:
            f.write(datetime.now(pytz.UTC).isoformat())
    except Exception as e:
        print(f"Error updating timestamp: {str(e)}")

def main():
    # Ensure all required files exist
    ensure_files_exist()
    
    results = {
        "timestamp": datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S"),
        "feeds": [],
        "summary": {
            "total": 0,
            "working": 0,
            "failed": 0
        }
    }

    try:
        sources = load_sources('sources.yml')
        
        for source in sources.get('sources', []):
            status, message = verify_rss_feed(source.get('url', ''))
            
            feed_result = {
                "name": source.get('name', 'Unknown'),
                "url": source.get('url', ''),
                "category": source.get('category', 'Uncategorized'),
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

        # Only exit with error if all feeds failed
        if results['summary']['working'] == 0:
            print("Error: All feeds failed validation")
            sys.exit(1)
        
        print(f"Validation complete: {results['summary']['working']}/{results['summary']['total']} feeds working")
        sys.exit(0)

    except Exception as e:
        print(f"Critical error during validation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
