from dotenv import load_dotenv

import pandas as pd
import praw
import os

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent="u/New-Connection5278")

# print("Reddit API set up successfully!")


def collect_reddit_data(query, max_results=50):
    subreddit = reddit.subreddit("all")
    posts = []
    for submission in subreddit.search(query, limit=max_results):
        post_data = {
            'title': submission.title,
            'url': submission.url,
            'score': submission.score,
            'num_comments': submission.num_comments,
            'upvotes': submission.ups,
            'downvotes': submission.downs,
            'created_utc': submission.created_utc,
            'comments': []
        }


        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list()[:20]:
            post_data['comments'].append(comment.body)

        posts.append(post_data)
    
    save_redditdata_to_csv(posts)

    return posts

def save_redditdata_to_csv(reddit_data, filename="RedditData/reddit_data.csv"):
    # Flattening the data for CSV conversion
    flattened_data = []
    for post in reddit_data:
        for comment in post['comments']:
            flattened_data.append({
                'title': post['title'],
                'url': post['url'],
                'score': post['score'],
                'upvotes': post['upvotes'],
                'downvotes': post['downvotes'],
                'num_comments': post['num_comments'],
                'created_utc': post['created_utc'],
                'comment': comment
            })
    df = pd.DataFrame(flattened_data)
    df.to_csv(filename, index=False)


# query = "productivity software reviews"
# reddit_data = collect_reddit_data(query)
# save_redditdata_to_csv(reddit_data)