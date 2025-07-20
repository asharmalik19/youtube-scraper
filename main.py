import json
import time
from urllib.parse import urljoin, urlparse, parse_qs

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

def extract_yt_channel_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    channel_name = soup.select_one('h2#title')
    about_container = soup.select_one('div#about-container')
    description = about_container.select_one('yt-attributed-string#description-container')
    table_rows = soup.select('tr.description-item')
    visible_rows = [row for row in table_rows if not row.has_attr('hidden')]

    for row in visible_rows:
        if row.select_one('yt-icon[icon="language"]'):
            user_handle = row
        elif row.select_one('yt-icon[icon="privacy_public"]'):
            country = row
        elif row.select_one('yt-icon[icon="info_outline"]'):
            join_date = row
        elif row.select_one('yt-icon[icon="person_radar"]'):
            subscriber_count = row
        elif row.select_one('yt-icon[icon="my_videos"]'):
            videos_count = row
        elif row.select_one('yt-icon[icon="trending_up"]'):
            views = row
        
    return {
        'user_handle': user_handle.text.strip() if user_handle else None,
        'subscriber_count': subscriber_count.text.strip() if subscriber_count else None,
        'videos_count': videos_count.text.strip() if videos_count else None,
        'views': views.text.strip() if views else None,
        'join_date': join_date.text.strip() if join_date else None,
        'country': country.text.strip() if country else None,
        'channel_name': channel_name.text.strip(),
        'description': description.text.strip() if description else None,
    }

def extract_yt_video_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.select_one('div#title')
    like_count = soup.select_one('button[title="I like this"]')
    views_count = soup.select_one('yt-formatted-string#info span')
    video_duration = soup.select_one('span.ytp-time-duration')
    upload_date = soup.select_one('#info-strings yt-formatted-string')

    return {
        'title': title.text.strip() if title else None,
        'like_count': like_count.text.strip() if like_count else None,
        'views_count': views_count.text.strip().split(' ')[0] if views_count else None,
        'video_duration': video_duration.text.strip() if video_duration else None,
        'upload_date': upload_date.text.strip() if upload_date else None
    }

def scroll(page):    
    previous_count = 0
    max_scrolls = 10  # Prevent infinite scrolling
    scroll_count = 0
    while scroll_count < max_scrolls:
        current_count = page.locator('a#video-title-link').count()    
        # Scroll down using Page Down key multiple times
        for _ in range(3):  
            page.keyboard.press('End')
            time.sleep(0.5)
        time.sleep(2)
        new_count = page.locator('a#video-title-link').count()
        if new_count == current_count:
            break  
        previous_count = new_count
        scroll_count += 1
    return page

def extract_transcript(link):
    parsed_url = urlparse(link)
    video_id = parse_qs(parsed_url.query).get('v', [None])[0] 
    if not video_id:
        return None      
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_fetch = ytt_api.fetch(video_id, languages=['hi'])
        transcript_text = [segment['text'] for segment in transcript_fetch]
        return ' '.join(transcript_text)
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None
    
def scrape_youtube_channel(url):
    """
    Scrapes YouTube channel videos.
    
    Note: If TimeoutError occurs on get_attribute('href'), add time.sleep(3-5) 
    before collecting video links to ensure page elements are fully loaded.
    """
    SLEEP_TIME_FOR_CHANNEL_PAGE = 4
    SLEEP_TIME_FOR_VIDEO_PAGE = 2
    
    result = {
        "user": [],
        "videos": []
    }   
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=0)
        page.locator('button.truncated-text-wiz__absolute-button').click()
        time.sleep(SLEEP_TIME_FOR_CHANNEL_PAGE)
        channel_data = extract_yt_channel_info(page.content())
        result["user"].append(channel_data)   
        page.locator('div#visibility-button').click()

        page = scroll(page)
        
        base_url = 'https://www.youtube.com/'
        yt_video_links = page.locator('a#video-title-link').all()
        print(f'found video links: {len(yt_video_links)}')
        yt_video_links = [urljoin(base_url, video.get_attribute('href')) for video in yt_video_links]
        for link in yt_video_links:
            page.goto(link)
            time.sleep(SLEEP_TIME_FOR_VIDEO_PAGE)
            video_data = extract_yt_video_info(page.content())
            video_data['link'] = link
            video_data['transcript_language'] = 'hi'
            video_data['transcript'] = extract_transcript(link)
            result['videos'].append(video_data)
            
        browser.close()
    return result

def main():
    url = 'https://www.youtube.com/@SenateofPakistanOfficial/streams'
    data = scrape_youtube_channel(url)
    print(json.dumps(data, indent=2))
    with open('youtube_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
