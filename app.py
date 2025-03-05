import requests
from dotenv import load_dotenv
import os

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Youtube APIs
YOUTUBE_SEARCH_API_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_API_URL = "https://www.googleapis.com/youtube/v3/videos"

# Reddit API
REDDIT_API_URL = 'https://www.reddit.com/r/{subreddit}/search.json'


# Function to get YouTube data
def get_youtube_data(product):
    search_params = {
        'part': 'snippet',
        'q': product,
        'key': YOUTUBE_API_KEY,
        'type': 'video',
        'maxResults': 5
    }
    search_response = requests.get(YOUTUBE_SEARCH_API_URL, params=search_params)
    search_results = search_response.json().get('items', [])

    youtube_data = []
    youtube_views = []
    video_ids = []

    for item in search_results:
        video_id = item['id']['videoId']
        video_ids.append(video_id)
        title = item['snippet']['title']
        url = f"https://www.youtube.com/watch?v={video_id}"
        youtube_data.append({'title': title, 'url': url})

    if video_ids:
        stats_params = {
            'part': 'statistics',
            'id': ','.join(video_ids),
            'key': YOUTUBE_API_KEY
        }
        stats_response = requests.get(YOUTUBE_VIDEOS_API_URL, params=stats_params)
        stats_results = stats_response.json().get('items', [])

        for i, stats in enumerate(stats_results):
            views = int(stats['statistics'].get('viewCount', 0))
            youtube_data[i]['views'] = views
            youtube_views.append(views)
    else:
        youtube_views = [0] * len(youtube_data)
        for data in youtube_data:
            data['views'] = 0

    return youtube_data, youtube_views

# Function to get Reddit data
def get_reddit_data(product):
    headers = {'User-Agent': REDDIT_USER_AGENT}
    params = {'q': product, 'limit': 5, 'sort': 'relevance', 'restrict_sr': False}
    response = requests.get(REDDIT_API_URL.format(subreddit='all'), headers=headers, params=params)
    reddit_data = []
    reddit_scores = []

    if response.status_code == 200:
        posts = response.json().get('data', {}).get('children', [])

        for post in posts:
            data = post['data']
            title = data['title']
            url = f"https://www.reddit.com{data['permalink']}"
            score = data['score']
            comments = data['num_comments']
            reddit_data.append({'title': title, 'url': url, 'score': score, 'comments': comments})
            reddit_scores.append(score)
    else:
        print(f"Error fetching Reddit data: {response.status_code}")
        reddit_data = []
        reddit_scores = []

    return reddit_data, reddit_scores


product = "watches"

youtube_data, youtube_views = get_youtube_data(product)
reddit_data, reddit_scores = get_reddit_data(product)

print(youtube_views)