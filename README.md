# YouTube Channel Scraper

A Python script that scrapes YouTube channel information and video data.

## What it does

- Extracts channel information (name, subscribers, video count, etc.)
- Scrapes all videos from a channel with details (title, views, duration, etc.)
- Exports data to JSON format

## Setup Guide

1. First install uv for your operating system if you don't have already
`https://docs.astral.sh/uv/getting-started/installation/`

2. Clone the repo
```bash
git clone https://github.com/asharmalik19/youtube-scraper
```

3. Install dependencies
```bash
uv sync
```

4. Install chromium if you don't have already
```bash
uv playwright install chromium
```

## Usage

### Direct Usage

1. Edit the channel URL in `main.py`:
```python
url = 'https://www.youtube.com/@YourChannelName/streams'
```

2. Run the script:
```bash
uv run main.py
```

3. Data will be saved to `youtube_data.json`

### As a Module

```python
from main import scrape_youtube_channel
import json

# Scrape a channel
url = 'https://www.youtube.com/@SenateofPakistanOfficial/streams'
data = scrape_youtube_channel(url)

# Use the data
print(f"Channel: {data['user'][0]['channel_name']}")
print(f"Videos found: {len(data['videos'])}")

# Save to file
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

## Output Format

```json
{
  "user": [{
    "channel_name": "Channel Name",
    "subscriber_count": "5.99K subscribers",
    "videos_count": "397 videos",
    "description": "Channel description..."
  }],
  "videos": [{
    "title": "Video Title",
    "views_count": "1.2K",
    "video_duration": "2:08:42",
    "transcript": "Full transcript text...",
    "link": "https://youtube.com/watch?v=..."
  }]
}
```

## Notes

- Script runs in non-headless mode (browser window visible)
- Transcripts are fetched in Hindi by default