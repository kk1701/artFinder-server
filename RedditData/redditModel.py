from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from textblob import TextBlob
from wordcloud import WordCloud

import os
import re
import pandas as pd
import matplotlib.pyplot as plt

# file_path = os.path.abspath("RedditData/reddit_data.csv")
# reddit_data = pd.read_csv(file_path)

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    # Remove URLs, special characters, and keep emojis
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^A-Za-z0-9\s\U0001F600-\U0001F64F]', '', text)
    return text

def get_sentiment(text):
    if not text:
        return 0
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def generate_reddit_wordcloud(all_comments):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_comments)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Comments', fontsize=15)
    plt.savefig('RedditData/reddit_wordcloud.png')
    # plt.show()
    plt.close()

def generate_reddit_bargraph(data):
    if 'score' in data.columns and 'title' in data.columns:
        plt.figure(figsize=(10, 6))
        plt.bar(data['title'], data['score'], color='skyblue')
        plt.xlabel('title', fontsize=12)
        plt.ylabel('score', fontsize=12)
        plt.title('Score vs Title from reddit', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.tight_layout()
        plt.savefig('RedditData/reddit_bargraph.png')
        # plt.show()
        plt.close()
    else:
        print("Error: The required columns 'Score' and 'Title' are not present in the dataset.")

def reddit_model(reddit_data):
    # Handle missing values
    reddit_data.fillna('', inplace=True)

    # Create binary label: 1 if score > median, else 0
    median_score = reddit_data['score'].median()
    reddit_data['label'] = (reddit_data['score'] > median_score).astype(int)

    # Feature engineering
    reddit_data['comment_length'] = reddit_data['comment'].apply(lambda x: len(str(x).split()))
    reddit_data['title_length'] = reddit_data['title'].apply(lambda x: len(str(x).split()))

    features = reddit_data[['upvotes', 'downvotes', 'num_comments', 'comment_length', 'title_length']]
    labels = reddit_data['label']

    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, labels, test_size=0.2, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    # print(classification_report(y_test, y_pred))
    
    # PRE-PROCESSING COMMENTS
    reddit_data['Cleaned Comments'] = reddit_data['comment'].apply(preprocess_text)
    
    # APPLYING SENTIMENT ANALYSIS
    reddit_data['Sentiment'] = reddit_data['Cleaned Comments'].apply(get_sentiment)
    
    all_comments = ' '.join(reddit_data['Cleaned Comments'])
    
    # GENERATE WORDCLOUD
    generate_reddit_wordcloud(all_comments)
    
    # GENERATE BAR GRAPH
    generate_reddit_bargraph(reddit_data)
