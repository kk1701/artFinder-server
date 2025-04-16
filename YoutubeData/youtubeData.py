from googleapiclient.discovery import build
from dotenv import load_dotenv

import csv
import os

load_dotenv() 

api_key = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=api_key)
# print("YouTube API set up successfully!")

def collect_youtube_data(query, max_results=50):

    search_response = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=max_results,
        order="relevance"
    ).execute()

    video_data = []

    # Extract video details
    for item in search_response['items']:
        video_id = item['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_info = {
            'video_id': video_id,
            'video_url': video_url,
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'published_at': item['snippet']['publishedAt'],
            'channel_title': item['snippet']['channelTitle'],
            'likes': None,
            'dislikes': None,
            'views': None,
            'comments': []
        }


        try:
            stats_response = youtube.videos().list(
                part="statistics",
                id=video_id
            ).execute()

            stats = stats_response['items'][0]['statistics']
            video_info['views'] = int(stats.get('viewCount', 0))
            video_info['likes'] = int(stats.get('likeCount', 0))
            video_info['dislikes'] = int(stats.get('dislikeCount', 0)) if 'dislikeCount' in stats else None

        except Exception as e:
            print(f"Could not fetch stats for video {video_id}: {e}")

        # Fetch comments
        try:
            comments_response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=20,
                order="relevance"
            ).execute()

            for comment in comments_response['items']:
                comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                video_info['comments'].append(comment_text)

        except Exception as e:
            print(f"Could not fetch comments for video {video_id}: {e}")

        video_data.append(video_info)

    save_youtubedata_to_csv(video_data)

    return video_data

def save_youtubedata_to_csv(video_data, filename="YoutubeData/youtube_data.csv"):

    columns = ['Video ID', 'URL', 'Title', 'Description', 'Published At', 'Channel Title', 'Views', 'Likes', 'Dislikes', 'Comments']

    # Write data to CSV
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(columns)

        for video in video_data:
            writer.writerow([
                video['video_id'],
                video['video_url'],
                video['title'],
                video['description'],
                video['published_at'],
                video['channel_title'],
                video['views'],
                video['likes'],
                video['dislikes'],
                " | ".join(video['comments'])
            ])

# Testing function
# query = "productivity software reviews"
# collect_youtube_data(query)

# print(f"YouTube data has been saved to 'youtube_data.csv'.")