import asyncio
import random
import time
from typing import List, Dict, Any
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel

app = FastAPI(
    title="MissAV Vibe Crawler & Agent Brain",
    description="Mock crawler, virtual ranking calculator, and background status broadcaster for MissAV Vibe Platform.",
    version="1.0.0"
)

# Enable CORS for frontend and cross-service calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GO_HOOK_URL = "http://localhost:8080/api/agent-hook"

class VideoItem(BaseModel):
    id: str
    code: str
    title: str
    cover_url: str
    duration: str
    views: int
    rating: float
    rank: int
    stream_url: str
    tags: List[str]
    actress: str

# Sample Mock Catalog (simulating parsed MissAV data)
MOCK_VIDEOS = [
    {
        "id": "msv-001",
        "code": "IPX-888",
        "title": "【4K極清】超人氣專屬女優 沉浸式浪漫企劃 4K原画無修正流出",
        "cover_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800&auto=format&fit=crop&q=80",
        "duration": "120:45",
        "views": 482910,
        "rating": 9.8,
        "stream_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
        "tags": ["4K", "獨家", "高畫質", "排行榜TOP1"],
        "actress": "相澤南"
    },
    {
        "id": "msv-002",
        "code": "SSIS-666",
        "title": "【頂級視聽】同棲生活24小時 密著寫真感串流優化版",
        "cover_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=800&auto=format&fit=crop&q=80",
        "duration": "115:30",
        "views": 391200,
        "rating": 9.6,
        "stream_url": "https://playertest.longtailvideo.com/adaptive/bipbop/gear4/prog_index.m3u8",
        "tags": ["同棲", "寫真", "無廣告", "熱門"],
        "actress": "河北彩花"
    },
    {
        "id": "msv-003",
        "code": "MIDE-999",
        "title": "【Vibe精選】辦公室秘密企劃 極簡串流碼率優化版",
        "cover_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=800&auto=format&fit=crop&q=80",
        "duration": "140:10",
        "views": 310550,
        "rating": 9.5,
        "stream_url": "https://demo.unified-streaming.com/k8s/features/stable/video/mp4/clear/bbb_sunflower_1080p_30fps_normal.mp4/.m3u8",
        "tags": ["OL", "職人", "碼率增強"],
        "actress": "三上悠亞"
    },
    {
        "id": "msv-004",
        "code": "SOD-301",
        "title": "【極客視訊】深夜限定賽博龐克風格 影音同步率測試紀錄",
        "cover_url": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=800&auto=format&fit=crop&q=80",
        "duration": "98:20",
        "views": 278900,
        "rating": 9.4,
        "stream_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
        "tags": ["Cyberpunk", "畫質修復", "賽博"],
        "actress": "深田詠美"
    },
    {
        "id": "msv-005",
        "code": "SONE-105",
        "title": "【夏季特輯】海邊度假全紀錄 無加載延遲去廣告串流",
        "cover_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80",
        "duration": "135:00",
        "views": 210400,
        "rating": 9.3,
        "stream_url": "https://playertest.longtailvideo.com/adaptive/bipbop/gear4/prog_index.m3u8",
        "tags": ["度假", "夏季", "HLS解密"],
        "actress": "新有菜"
    }
]

# In-memory storage for virtual rankings matrix
virtual_rankings: List[Dict[str, Any]] = []
agent_state = {
    "status": "INITIALIZING",
    "loop_count": 0,
    "last_broadcast": None,
    "parsed_items": 0
}

def recalculate_rankings():
    """Calculates dynamic virtual rankings based on mock views, rating & dynamic heat score."""
    global virtual_rankings
    items = []
    for idx, v in enumerate(MOCK_VIDEOS):
        item = v.copy()
        # Add random simulated dynamic variation to views and ratings
        item["views"] = item["views"] + random.randint(10, 500)
        item["rating"] = min(10.0, round(item["rating"] + random.uniform(-0.05, 0.05), 1))
        # Compute Vibe Heat Score
        heat_score = (item["views"] / 1000) * 0.6 + (item["rating"] * 10) * 0.4
        item["heat_score"] = round(heat_score, 2)
        items.append(item)
    
    # Sort by heat score descending
    items.sort(key=lambda x: x["heat_score"], reverse=True)
    for rank, item in enumerate(items, start=1):
        item["rank"] = rank
    
    virtual_rankings = items
    agent_state["parsed_items"] = len(items)

# Initial ranking calculation
recalculate_rankings()

async def send_agent_log(level: str, message: str, data: Any = None):
    """Sends log payload to Go Backend API Hook for WebSocket broadasting."""
    payload = {
        "source": "CRAWLER_AGENT",
        "level": level,
        "message": message,
        "timestamp": time.strftime("%H:%M:%S") + f".{int(time.time()*1000)%1000:03d}",
        "data": data
    }
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.post(GO_HOOK_URL, json=payload)
            if resp.status_code == 200:
                agent_state["last_broadcast"] = payload["timestamp"]
    except Exception as e:
        # Go backend might be starting up
        pass

async def agent_loop():
    """Background task loop simulating continuous crawling and metric evaluation."""
    await asyncio.sleep(2.0)
    print("🤖 Agent Background Loop Started...")
    
    loop_messages = [
        ("INFO", "🔍 [FETCH] Initiating HTTPS GET to MissAV homepage DOM..."),
        ("INFO", "⚡ [PARSER] Parsing HTML node cards with BeautifulSoup4. Stripping ad scripts..."),
        ("SUCCESS", "✅ [EXTRACT] Extracted 5 primary video metadata cards without ad payloads."),
        ("INFO", "📊 [METRICS] Re-calculating Vibe Heat Score matrix (Views * 0.6 + Rating * 0.4)..."),
        ("SUCCESS", "🔥 [RANK_UPDATE] Virtual Ranking Matrix refreshed. Top 1 item updated."),
        ("INFO", "🛡️ [PROXY_CHECK] Verifying m3u8 playlist headers via Go Proxy (8080)..."),
        ("SUCCESS", "✨ [STANDBY] Agent loop resting. System fully optimal.")
    ]

    msg_idx = 0
    while True:
        try:
            agent_state["loop_count"] += 1
            agent_state["status"] = "RUNNING"
            
            # Recalculate virtual rankings periodically
            recalculate_rankings()

            level, msg = loop_messages[msg_idx % len(loop_messages)]
            
            # Add dynamic context data for rank updates
            extra_data = None
            if "RANK_UPDATE" in msg and virtual_rankings:
                extra_data = {
                    "top_video": virtual_rankings[0]["code"],
                    "title": virtual_rankings[0]["title"][:20] + "...",
                    "heat_score": virtual_rankings[0]["heat_score"]
                }

            await send_agent_log(level, msg, extra_data)
            msg_idx += 1

        except Exception as err:
            print(f"Agent loop error: {err}")

        await asyncio.sleep(3.5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(agent_loop())

@app.get("/api/rankings", response_model=List[Dict[str, Any]])
def get_rankings():
    """Get the calculated virtual rankings matrix."""
    return virtual_rankings

@app.get("/api/status")
def get_status():
    """Get crawler agent runtime state."""
    return {
        "service": "crawler-python",
        "port": 8000,
        "agent_state": agent_state,
        "total_ranked_videos": len(virtual_rankings)
    }

@app.post("/api/crawl/trigger")
async def trigger_crawl(background_tasks: BackgroundTasks):
    """Manually trigger an instant crawling session."""
    await send_agent_log("INFO", "🚀 [MANUAL_TRIGGER] User requested instant crawling and parsing sequence!")
    recalculate_rankings()
    await send_agent_log("SUCCESS", "✅ [MANUAL_TRIGGER] Re-parsed MissAV nodes and updated rankings matrix.")
    return {"status": "triggered", "video_count": len(virtual_rankings)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
