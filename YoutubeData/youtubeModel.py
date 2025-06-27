from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from sklearn.impute import SimpleImputer
from textblob import TextBlob
from wordcloud import WordCloud

import re
import matplotlib.pyplot as plt

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

def generate_youtube_wordcloud(all_comments):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_comments)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Comments', fontsize=15)
    plt.savefig('YoutubeData/youtube_wordcloud.png')
    # plt.show()
    plt.close()

def generate_youtube_bargraphs(data):
    data['Score 1'] = data['Likes']
    data['Score 2'] = data['Likes'] / (data['comment_count'] + 1e-10)
    data['Score 3'] = data['Views']
    data['Score 4'] = data['Views'] / (data['Likes'] + 1e-10)

    plt.figure(figsize=(15, 20))
    
    scores_info = [
        ('Likes', 'Score 1'),
        ('Likes / Comments Count', 'Score 2'),
        ('Views', 'Score 3'),
        ('Views / Likes', 'Score 4')
    ]
    
    # Plot each score
    for i, (title, column) in enumerate(scores_info, 1):
        plt.subplot(2, 2, i)
        plt.bar(data['Video ID'], data[column], width=0.3, color='skyblue')
        plt.title(title)
        plt.xlabel('Video ID')
        plt.ylabel(title)
        plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig('YoutubeData/youtube_bargraphs.png')
    # plt.show()
    plt.close()
    
    
def youtube_model(data):
    data['comment_count'] = data['Comments'].fillna("").apply(lambda x: len(str(x).split(" | ")))

    data['score'] = data['comment_count'] / data['Likes']

    data['label'] = (data['score'] > 1).astype(int)

    features = data[['Views', 'Likes', 'Dislikes', 'comment_count']]
    label = data['label']

    # Impute missing values using the mean
    imputer = SimpleImputer(strategy='mean')
    features_imputed = imputer.fit_transform(features)

    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features_imputed)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, label, test_size=0.2, random_state=42)

    model = LogisticRegression()
    # model.fit(X_train, y_train)

    # y_pred = model.predict(X_test)
    # print(classification_report(y_test, y_pred))
    
    
    # PRE-PROCESSING COMMENTS
    data['Cleaned Comments'] = data['Comments'].apply(preprocess_text)
    
    # APPLYING SENTIMENT ANALYSIS
    data['Sentiment'] = data['Cleaned Comments'].apply(get_sentiment)
    
    all_comments = ' '.join(data['Cleaned Comments'])
    
    # GENERATE WORDCLOUD
    generate_youtube_wordcloud(all_comments)
    
    # GENERATE BAR GRAPHS
    generate_youtube_bargraphs(data)
