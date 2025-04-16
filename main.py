from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from schemas import ProductRequested, YoutubeTableResponse, RedditTableResponse, YoutubeModelResponse, RedditModelResponse
from YoutubeData.youtubeData import collect_youtube_data
from RedditData.redditData import collect_reddit_data
from YoutubeData.youtubeModel import youtube_model
from RedditData.redditModel import reddit_model

import os
import base64
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submitForm")
async def submitForm(request: ProductRequested):
    product = request.product_name
    query = product + " reviews"
    
    collect_youtube_data(query)
    
    collect_reddit_data(query)
    
    return {
        "message": "recieved product name."
    }
      
@app.get("/youtubeTableData", response_model=YoutubeTableResponse)
async def youtubeTableData():

    youtube_data = pd.read_csv("./YoutubeData/youtube_data.csv")

    youtube_titles = youtube_data["Title"]
    youtube_urls = youtube_data["URL"]
    youtube_views = youtube_data["Views"]
    
    return {
        "youtube_titles": youtube_titles[:10],
        "youtube_urls": youtube_urls[:10],
        "youtube_views": youtube_views[:10]
    }
      
@app.get("/redditTableData", response_model=RedditTableResponse)
async def redditTableData():
    
    reddit_data = pd.read_csv("./RedditData/reddit_data.csv")

    reddit_titles = reddit_data['title']
    reddit_urls = reddit_data['url']
    reddit_scores = reddit_data['score']
    
    return {
        "reddit_titles": reddit_titles[:10],
        "reddit_urls": reddit_urls[:10],
        "reddit_scores": reddit_scores[:10]
    }

@app.get("/getYoutubeWordcloud")
async def getYoutubeWordcloud():
    
    youtube_data = pd.read_csv("./YoutubeData/youtube_data.csv")
    youtube_model(youtube_data)
    
    file_path = f"YoutubeData/youtube_wordcloud.png"
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        return {"image": f"data:image/png;base64,{base64_image}"}
    
    return {"error": "Youtube wordcloud not found"}

@app.get("/getYoutubeBarGraphs")
async def getYoutubeBarGraphs():

    file_path = f"YoutubeData/youtube_bargraphs.png"
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        return {"image": f"data:image/png;base64,{base64_image}"}
    
    return {"error": "Youtube bar graphs not found"}

@app.get("/getRedditWordCloud")
async def getRedditWordCloud():
    
    reddit_data = pd.read_csv("./RedditData/reddit_data.csv")
    reddit_model(reddit_data)
    
    file_path = f"RedditData/reddit_wordcloud.png"
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        return {"image": f"data:image/png;base64,{base64_image}"}
    
    return {"error": "Reddit wordcloud not found"}

@app.get("/getRedditBarGraph")
async def getRedditWordCloud():

    file_path = f"RedditData/reddit_bargraph.png"
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode("utf-8")
        return {"image": f"data:image/png;base64,{base64_image}"}
    
    return {"error": "Reddit bar graph not found"}