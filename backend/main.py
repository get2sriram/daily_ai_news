from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from news_agent import NewsAgent
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI(title="Daily AI News API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for news by timeframe
_cached_news = {
    "today": {"data": [], "last_updated": None},
    "weekly": {"data": [], "last_updated": None},
    "monthly": {"data": [], "last_updated": None}
}

agent = NewsAgent()

@app.get("/")
async def root():
    return {
        "message": "Daily AI News API is running",
        "cached_timeframes": list(_cached_news.keys())
    }

@app.get("/api/news")
async def get_news(timeframe: str = "today"):
    """Returns AI news summary for a specific timeframe (today, weekly, monthly)."""
    if timeframe not in _cached_news:
        raise HTTPException(status_code=400, detail="Invalid timeframe. Use today, weekly, or monthly.")
    
    # If cache is empty for this timeframe, fetch it
    if not _cached_news[timeframe]["data"]:
        days_val = 1 if timeframe == "today" else (7 if timeframe == "weekly" else 30)
        _cached_news[timeframe]["data"] = agent.get_summary(days=days_val)
        _cached_news[timeframe]["last_updated"] = datetime.now().isoformat()
    
    return {
        "news": _cached_news[timeframe]["data"],
        "last_updated": _cached_news[timeframe]["last_updated"]
    }

@app.post("/api/refresh")
async def refresh_news(timeframe: str = "today"):
    """Manually triggers the agent to fetch the latest AI news for a timeframe."""
    if timeframe not in _cached_news:
        raise HTTPException(status_code=400, detail="Invalid timeframe.")
        
    try:
        days_val = 1 if timeframe == "today" else (7 if timeframe == "weekly" else 30)
        _cached_news[timeframe]["data"] = agent.get_summary(days=days_val)
        _cached_news[timeframe]["last_updated"] = datetime.now().isoformat()
        return {
            "status": "success",
            "message": f"{timeframe} news feed refreshed",
            "last_updated": _cached_news[timeframe]["last_updated"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sources")
async def get_source_stats():
    """Returns statistics about which sources were used across all timeframes."""
    stats = {}
    
    for timeframe in ["today", "weekly", "monthly"]:
        for item in _cached_news[timeframe]["data"]:
            source = item.get("source", "Unknown")
            if source not in stats:
                stats[source] = {"today": 0, "weekly": 0, "monthly": 0, "total": 0}
            stats[source][timeframe] += 1
            stats[source]["total"] += 1
            
    # Convert to list for easier frontend handling
    source_list = [
        {"name": name, **data} for name, data in stats.items()
    ]
    # Sort by total articles selected
    source_list.sort(key=lambda x: x["total"], reverse=True)
    
    return {"sources": source_list}

if __name__ == "__main__":
    import uvicorn
    # Use environment variable for port to allow flexibility
    port = int(os.getenv("PORT", 8000))
    # 'main:app' string is required for the reload feature to work
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
