from pydantic import BaseModel

class ProductRequested(BaseModel):
    product_name: str
    
class YoutubeTableResponse(BaseModel):
    youtube_titles: list[str]
    youtube_urls: list[str]
    youtube_views: list[int]

class RedditTableResponse(BaseModel):
    reddit_titles: list[str]
    reddit_urls: list[str]
    reddit_scores: list[int]
    
class YoutubeModelResponse(BaseModel):
    youtube_description_score: int
    
class RedditModelResponse(BaseModel):
    reddit_description_score: int
    
