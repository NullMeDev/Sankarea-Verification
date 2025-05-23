# RSS Feed Validator

Validates RSS feeds from the `sources.yml` file every 6 hours using GitHub Actions and publishes a curated list of working sources weekly.

## Status

$(cat status_badge.md)

## Features

- Validates RSS feed format and content
- Checks feed accessibility
- Generates detailed status report
- Updates status badge automatically
- Runs every 6 hours and on push
- Creates artifacts with detailed results
- **Weekly Publishing**: Auto-updates `VALID_SOURCES.md` every 7 days with working feeds

## Valid Sources

See [`VALID_SOURCES.md`](VALID_SOURCES.md) for the current list of working RSS feeds, automatically updated weekly.

## Usage

1. Update `sources.yml` with your feeds
2. Feeds are automatically verified every 6 hours
3. Check Actions tab for detailed results
4. Status badge in README shows current state
5. Download artifacts for detailed report
6. Check `VALID_SOURCES.md` for the latest working feeds list

## Manual Verification

You can manually trigger the verification:

1. Go to Actions tab
2. Select "Verify RSS Feeds" workflow
3. Click "Run workflow"

## Report Format

The verification creates two main outputs:

### 1. feed_status.json
```json
{
  "timestamp": "2025-05-23 07:42:01",
  "feeds": [
    {
      "name": "Example Feed",
      "url": "https://example.com/feed.xml",
      "category": "Technology",
      "working": true,
      "message": "Feed is valid and contains entries"
    }
  ],
  "summary": {
    "total": 50,
    "working": 48,
    "failed": 2
  }
}
