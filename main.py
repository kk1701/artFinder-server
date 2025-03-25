from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from model import get_youtube_data, get_reddit_data, get_keyword_impact

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductRequested(BaseModel):
    product_name: str

class DataResponse(BaseModel):
    youtube_titles: list[str]
    youtube_urls: list[str]
    youtube_views: list[int]
    reddit_titles: list[str]
    reddit_urls: list[str]
    reddit_scores: list[int]
    youtube_keywords: list[str]
    youtube_keyword_impacts: list[float]
    reddit_keywords: list[str]
    reddit_keyword_impacts: list[float]
      
@app.post("/getData", response_model=DataResponse)
async def getYoutubeData(request: ProductRequested):
    
    product = request.product_name
    youtube_urls, youtube_titles, youtube_views = get_youtube_data(product)
    reddit_urls, reddit_titles, reddit_scores = get_reddit_data(product)
    
    youtube_df = get_keyword_impact(youtube_titles, youtube_views)
    youtube_keywords = youtube_df["keyword"].tolist()
    youtube_keyword_impacts = youtube_df["normalized_impact"].tolist()
    
    reddit_df = get_keyword_impact(reddit_titles, reddit_scores)
    reddit_keywords = reddit_df["keyword"].tolist()
    reddit_keyword_impacts = reddit_df["normalized_impact"].tolist()
    
    return {
        "youtube_titles": youtube_titles,
        "youtube_urls": youtube_urls,
        "youtube_views": youtube_views,
        "reddit_titles": reddit_titles,
        "reddit_urls": reddit_urls,
        "reddit_scores": reddit_scores,
        "youtube_keywords": youtube_keywords[:10],
        "youtube_keyword_impacts": youtube_keyword_impacts[:10],
        "reddit_keywords": reddit_keywords[:10],
        "reddit_keyword_impacts": reddit_keyword_impacts[:10]
    }
