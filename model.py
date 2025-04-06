from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from dotenv import load_dotenv

import pandas as pd
import numpy as np
import requests
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
        'maxResults': 10
    }
    search_response = requests.get(YOUTUBE_SEARCH_API_URL, params=search_params)
    search_results = search_response.json().get('items', [])

    youtube_data = []
    youtube_urls = []
    youtube_views = []
    youtube_titles = []
    video_ids = []

    for item in search_results:
        video_id = item['id']['videoId']
        video_ids.append(video_id)
        title = item['snippet']['title']
        url = f"https://www.youtube.com/watch?v={video_id}"
        youtube_data.append({'title': title, 'url': url})
        youtube_titles.append(title)
        youtube_urls.append(url)

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

    return youtube_urls, youtube_titles, youtube_views

# Function to get Reddit data
def get_reddit_data(product):
    headers = {'User-Agent': REDDIT_USER_AGENT}
    params = {'q': product, 'limit': 10, 'sort': 'relevance', 'restrict_sr': False}
    response = requests.get(REDDIT_API_URL.format(subreddit='all'), headers=headers, params=params)
    reddit_data = []
    reddit_urls = []
    reddit_scores = []
    reddit_titles = []

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
            reddit_titles.append(title)
            reddit_urls.append(url)
    else:
        print(f"Error fetching Reddit data: {response.status_code}")
        reddit_data = []
        reddit_scores = []

    return reddit_urls, reddit_titles, reddit_scores


# Function to get keywords and their impacts.
def get_keyword_impact(titles, views, ngram_range=(1, 2), stop_words="english"):
    """
    Analyzes the impact of keywords in video titles on view counts.
    
    Args:
        titles (list): List of video titles (strings).
        views (list): List of view counts (integers).
        ngram_range (tuple): Range of n-grams to consider (default: (1, 2)).
        stop_words (str/list): Stop words to ignore (default: "english").
    
    Returns:
        pd.DataFrame: Keywords and their impact scores, sorted by impact (descending).
    """
    df = pd.DataFrame({"title": titles, "views": views})
    
    # Vectorize titles using TF-IDF
    tfidf = TfidfVectorizer(stop_words=stop_words, ngram_range=ngram_range)
    X = tfidf.fit_transform(df["title"])
    y = df["views"]
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Extract keywords and coefficients
    keywords = tfidf.get_feature_names_out()
    coefs = model.coef_
    
    scaler = MinMaxScaler(feature_range=(1, 10))
    normalized_impact = scaler.fit_transform(coefs.reshape(-1, 1)).flatten()
    
    keyword_impact = pd.DataFrame({
        "keyword": keywords,
        "impact": coefs,
        "normalized_impact": np.round(normalized_impact, 2)
    }).sort_values("normalized_impact", ascending=False)
    
    return keyword_impact[["keyword", "normalized_impact"]].reset_index(drop=True)
