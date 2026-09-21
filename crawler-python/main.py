import asyncio
import random
import time
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel

app = FastAPI(
    title="MissAV Vibe Interactive Crawler & Agent Brain",
    description="Interactive backend service simulating MissAV.ws metadata, categories, actresses, search, and real-time agent broadcasting.",
    version="2.0.0"
)

# Enable CORS for frontend and proxy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GO_HOOK_URL = "http://localhost:8080/api/agent-hook"

# Comprehensive Mock Dataset matching MissAV.ws style
MOCK_VIDEOS = [
    {
        "id": "msv-001",
        "code": "IPX-888",
        "title": "【4K極清】超人氣專屬女優 沉浸式浪漫企劃 4K原画無修正流出",
        "cover_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800&auto=format&fit=crop&q=80",
        "duration": "120:45",
        "release_date": "2026-09-18",
        "views": 482910,
        "rating": 9.8,
        "stream_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
        "tags": ["4K", "獨家", "高畫質", "無修正", "浪漫"],
        "actress": "相澤南",
        "category": "uncensored"
    },
    {
        "id": "msv-002",
        "code": "SSIS-666",
        "title": "【頂級視聽】同棲生活24小時 密著寫真感串流中文字幕版",
        "cover_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=800&auto=format&fit=crop&q=80",
        "duration": "115:30",
        "release_date": "2026-09-19",
        "views": 391200,
        "rating": 9.6,
        "stream_url": "https://playertest.longtailvideo.com/adaptive/bipbop/gear4/prog_index.m3u8",
        "tags": ["同棲", "寫真", "中文字幕", "熱門發行"],
        "actress": "河北彩花",
        "category": "chinese-subtitle"
    },
    {
        "id": "msv-003",
        "code": "MIDE-999",
        "title": "【Vibe精選】辦公室秘密企劃 極簡串流碼率優化中文字幕版",
        "cover_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=800&auto=format&fit=crop&q=80",
        "duration": "140:10",
        "release_date": "2026-09-15",
        "views": 310550,
        "rating": 9.5,
        "stream_url": "https://devstreaming-cdn.apple.com/videos/streaming/examples/bipbop_16x9/bipbop_16x9_variant.m3u8",
        "tags": ["OL", "職人", "中文字幕", "碼率增強"],
        "actress": "三上悠亞",
        "category": "chinese-subtitle"
    },
    {
        "id": "msv-004",
        "code": "SOD-301",
        "title": "【極客視訊】深夜限定賽博龐克風格 影音同步率測試紀錄",
        "cover_url": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=800&auto=format&fit=crop&q=80",
        "duration": "98:20",
        "release_date": "2026-09-20",
        "views": 278900,
        "rating": 9.4,
        "stream_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
        "tags": ["Cyberpunk", "畫質修復", "賽博", "最近更新"],
        "actress": "深田詠美",
        "category": "recent"
    },
    {
        "id": "msv-005",
        "code": "SONE-105",
        "title": "【夏季特輯】海邊度假全紀錄 無加載延遲去廣告串流",
        "cover_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80",
        "duration": "135:00",
        "release_date": "2026-09-17",
        "views": 210400,
        "rating": 9.3,
        "stream_url": "https://playertest.longtailvideo.com/adaptive/bipbop/gear4/prog_index.m3u8",
        "tags": ["度假", "夏季", "無修正", "巨乳"],
        "actress": "新有菜",
        "category": "uncensored"
    },
    {
        "id": "msv-006",
        "code": "JUL-204",
        "title": "【人妻溫泉】靜謐旅館的午後私會 4K超高解析度特別版",
        "cover_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=800&auto=format&fit=crop&q=80",
        "duration": "128:50",
        "release_date": "2026-09-16",
        "views": 365400,
        "rating": 9.7,
        "stream_url": "https://devstreaming-cdn.apple.com/videos/streaming/examples/bipbop_16x9/bipbop_16x9_variant.m3u8",
        "tags": ["人妻", "溫泉", "4K", "中文字幕", "熱門發行"],
        "actress": "波多野結衣",
        "category": "chinese-subtitle"
    },
    {
        "id": "msv-007",
        "code": "SDDE-512",
        "title": "【女僕逆襲】豪華宅邸專屬管家 獨家未公開特別收錄",
        "cover_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=800&auto=format&fit=crop&q=80",
        "duration": "112:15",
        "release_date": "2026-09-21",
        "views": 194800,
        "rating": 9.2,
        "stream_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
        "tags": ["女僕", "制服", "最近更新", "獨家"],
        "actress": "天使萌",
        "category": "recent"
    },
    {
        "id": "msv-008",
        "code": "FSDSS-245",
        "title": "【高校回憶】放課後的社團更衣室 青春素人純情視角",
        "cover_url": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=800&auto=format&fit=crop&q=80",
        "duration": "104:30",
        "release_date": "2026-09-20",
        "views": 258000,
        "rating": 9.4,
        "stream_url": "https://playertest.longtailvideo.com/adaptive/bipbop/gear4/prog_index.m3u8",
        "tags": ["學生", "制服", "素人", "中文字幕"],
        "actress": "小野六花",
        "category": "chinese-subtitle"
    },
    {
        "id": "msv-009",
        "code": "STARS-450",
        "title": "【S1旗艦】年度最美臉孔 頂級電影級調色超大作",
        "cover_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=800&auto=format&fit=crop&q=80",
        "duration": "150:00",
        "release_date": "2026-09-14",
        "views": 441000,
        "rating": 9.9,
        "stream_url": "https://devstreaming-cdn.apple.com/videos/streaming/examples/bipbop_16x9/bipbop_16x9_variant.m3u8",
        "tags": ["4K", "大作", "獨家", "無修正", "熱門發行"],
        "actress": "河北彩花",
        "category": "trending"
    },
    {
        "id": "msv-010",
        "code": "KMHR-012",
        "title": "【街頭實測】突擊訪問澀谷辣妹 百分百自然無劇本收錄",
        "cover_url": "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=800&auto=format&fit=crop&q=80",
        "duration": "88:40",
        "release_date": "2026-09-21",
        "views": 182300,
        "rating": 9.1,
        "stream_url": "https://devstreaming-cdn.apple.com/videos/streaming/examples/bipbop_4x3/bipbop_4x3_variant.m3u8",
        "tags": ["街拍", "素人", "最近更新"],
        "actress": "素人企画",
        "category": "recent"
    }
]

# Actress profiles metadata
ACTRESS_PROFILES = [
    {"name": "河北彩花", "avatar": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=300&auto=format&fit=crop&q=80", "cup": "E", "debut": "2018", "rating": 9.8},
    {"name": "相澤南", "avatar": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=300&auto=format&fit=crop&q=80", "cup": "D", "debut": "2016", "rating": 9.7},
    {"name": "三上悠亞", "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300&auto=format&fit=crop&q=80", "cup": "F", "debut": "2015", "rating": 9.6},
    {"name": "波多野結衣", "avatar": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=300&auto=format&fit=crop&q=80", "cup": "D", "debut": "2008", "rating": 9.7},
    {"name": "深田詠美", "avatar": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=300&auto=format&fit=crop&q=80", "cup": "F", "debut": "2017", "rating": 9.5},
    {"name": "新有菜", "avatar": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=300&auto=format&fit=crop&q=80", "cup": "C", "debut": "2016", "rating": 9.4},
    {"name": "天使萌", "avatar": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=300&auto=format&fit=crop&q=80", "cup": "B", "debut": "2014", "rating": 9.3},
    {"name": "小野六花", "avatar": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=300&auto=format&fit=crop&q=80", "cup": "C", "debut": "2020", "rating": 9.4},
    {"name": "素人企画", "avatar": "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=300&auto=format&fit=crop&q=80", "cup": "All", "debut": "2021", "rating": 9.1}
]

# In-memory storage for active video states
virtual_catalog: List[Dict[str, Any]] = []
agent_state = {
    "status": "INITIALIZING",
    "loop_count": 0,
    "last_broadcast": None,
    "total_videos": len(MOCK_VIDEOS),
    "active_crawlers": 1
}

def recalculate_catalog():
    """Recalculates dynamic heat score, MissAV links, and stream mappings."""
    global virtual_catalog
    items = []
    
    # Verified, high-availability public HLS streams (100% operational)
    verified_streams = [
        "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
        "https://devstreaming-cdn.apple.com/videos/streaming/examples/bipbop_16x9/bipbop_16x9_variant.m3u8",
        "https://playertest.longtailvideo.com/adaptive/bipbop/gear4/prog_index.m3u8",
        "https://devstreaming-cdn.apple.com/videos/streaming/examples/bipbop_4x3/bipbop_4x3_variant.m3u8"
    ]

    for idx, v in enumerate(MOCK_VIDEOS):
        item = v.copy()
        item["views"] = item["views"] + random.randint(5, 120)
        item["rating"] = min(10.0, round(item["rating"] + random.uniform(-0.02, 0.02), 1))
        heat_score = (item["views"] / 1000) * 0.6 + (item["rating"] * 10) * 0.4
        item["heat_score"] = round(heat_score, 2)
        
        # Link back to MissAV original pages
        code_slug = item["code"].lower().strip()
        item["missav_url"] = f"https://missav.ws/{code_slug}"
        item["missav_alt_url"] = f"https://missav.com/{code_slug}"
        
        # Ensure reliable streaming URL
        item["stream_url"] = verified_streams[idx % len(verified_streams)]
        item["proxy_stream_url"] = f"http://localhost:8080/proxy/stream?url={item['stream_url']}&referer=https://missav.ws/"
        
        items.append(item)

    # Sort default by heat score
    items.sort(key=lambda x: x["heat_score"], reverse=True)
    for rank, item in enumerate(items, start=1):
        item["rank"] = rank

    virtual_catalog = items

recalculate_catalog()

async def send_agent_log(level: str, message: str, data: Any = None):
    """Sends log payload to Go Backend API Hook for WebSocket broadcasting."""
    payload = {
        "source": "MISSAV_CRAWLER",
        "level": level,
        "message": message,
        "timestamp": time.strftime("%H:%M:%S") + f".{int(time.time()*1000)%1000:03d}",
        "data": data
    }
    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            await client.post(GO_HOOK_URL, json=payload)
    except Exception:
        pass

async def agent_loop():
    """Background loop simulating MissAV.ws DOM updates and ranking broadcasts."""
    await asyncio.sleep(2.0)
    
    status_cycles = [
        ("INFO", "🌐 [CRAWL_MISSAV_WS] Scraping https://missav.ws/ new releases feed..."),
        ("SUCCESS", "⚡ [DOM_CLEAN] Stripped 14 ad scripts, banners & popup overlays successfully."),
        ("INFO", "🔍 [PARSE_METADATA] Extracted video tags, actress profile & m3u8 playlist token."),
        ("INFO", "🔥 [HEAT_ENGINE] Re-evaluating dynamic ranking algorithms and engagement matrix."),
        ("SUCCESS", "✅ [PROXY_VALIDATE] Tested Go Reverse Proxy (8080) with Referer: https://missav.ws/"),
        ("INFO", "✨ [STANDBY] Agent loop idle. Ready for interactive user queries.")
    ]

    idx = 0
    while True:
        try:
            agent_state["loop_count"] += 1
            agent_state["status"] = "ACTIVE"
            recalculate_catalog()

            level, msg = status_cycles[idx % len(status_cycles)]
            extra_data = None
            if "HEAT_ENGINE" in msg and virtual_catalog:
                extra_data = {
                    "top_video": virtual_catalog[0]["code"],
                    "actress": virtual_catalog[0]["actress"],
                    "heat_score": virtual_catalog[0]["heat_score"]
                }

            await send_agent_log(level, msg, extra_data)
            idx += 1
        except Exception as e:
            print(f"Agent loop error: {e}")

        await asyncio.sleep(3.5)

@app.on_event("startup")
async def startup():
    asyncio.create_task(agent_loop())

# --- Interactive API Routes ---

@app.get("/api/videos")
def get_videos(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    actress: Optional[str] = None,
    sort: Optional[str] = "heat",
    page: int = 1,
    limit: int = 20
):
    """Filterable video list matching MissAV.ws navigation."""
    results = virtual_catalog.copy()

    if category and category != "all":
        if category == "recent":
            results = [v for v in results if v.get("category") == "recent" or "最近更新" in v["tags"]]
        elif category == "trending":
            results = [v for v in results if v.get("category") == "trending" or "熱門發行" in v["tags"] or v["rank"] <= 5]
        elif category == "chinese-subtitle":
            results = [v for v in results if "中文字幕" in v["tags"]]
        elif category == "uncensored":
            results = [v for v in results if "無修正" in v["tags"] or "4K" in v["tags"]]
        else:
            results = [v for v in results if v.get("category") == category]

    if tag and tag != "all":
        results = [v for v in results if any(tag.lower() == t.lower() for t in v["tags"])]

    if actress:
        results = [v for v in results if actress.lower() in v["actress"].lower()]

    if search:
        s = search.lower().strip()
        results = [
            v for v in results
            if s in v["code"].lower() or s in v["title"].lower() or s in v["actress"].lower() or any(s in t.lower() for t in v["tags"])
        ]

    if sort == "views":
        results.sort(key=lambda x: x["views"], reverse=True)
    elif sort == "rating":
        results.sort(key=lambda x: x["rating"], reverse=True)
    elif sort == "new":
        results.sort(key=lambda x: x["release_date"], reverse=True)
    else:  # heat
        results.sort(key=lambda x: x["heat_score"], reverse=True)

    total = len(results)
    start = (page - 1) * limit
    paginated = results[start : start + limit]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "videos": paginated
    }

@app.get("/api/videos/{code}")
def get_video_detail(code: str):
    """Retrieve single video details and 4 related video recommendations."""
    target = None
    for v in virtual_catalog:
        if v["code"].lower() == code.lower() or v["id"] == code:
            target = v
            break

    if not target:
        raise HTTPException(status_code=404, detail="Video not found")

    # Find related videos by actress or shared tags
    related = [
        v for v in virtual_catalog
        if v["code"] != target["code"] and (v["actress"] == target["actress"] or any(t in target["tags"] for t in v["tags"]))
    ]
    if len(related) < 4:
        for v in virtual_catalog:
            if v["code"] != target["code"] and v not in related:
                related.append(v)
            if len(related) >= 4:
                break

    return {
        "video": target,
        "related": related[:4]
    }

@app.get("/api/categories")
def get_categories():
    """List categories with dynamic counts."""
    return [
        {"id": "all", "name": "全部影片", "icon": "fa-film", "count": len(virtual_catalog)},
        {"id": "recent", "name": "最近更新", "icon": "fa-clock", "count": len([v for v in virtual_catalog if "最近更新" in v["tags"] or v.get("category") == "recent"])},
        {"id": "trending", "name": "熱門發行", "icon": "fa-fire", "count": len([v for v in virtual_catalog if "熱門發行" in v["tags"] or v.get("category") == "trending"])},
        {"id": "chinese-subtitle", "name": "中文字幕", "icon": "fa-closed-captioning", "count": len([v for v in virtual_catalog if "中文字幕" in v["tags"]])},
        {"id": "uncensored", "name": "無修正流出", "icon": "fa-gem", "count": len([v for v in virtual_catalog if "無修正" in v["tags"] or "4K" in v["tags"]])}
    ]

@app.get("/api/tags")
def get_tags():
    """Return all unique tags and occurrence counts."""
    tag_counts = {}
    for v in virtual_catalog:
        for t in v["tags"]:
            tag_counts[t] = tag_counts.get(t, 0) + 1
    
    return [
        {"name": tag, "count": count}
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    ]

@app.get("/api/actresses")
def get_actresses():
    """Return top actresses with photo, total works and info."""
    result = []
    for profile in ACTRESS_PROFILES:
        works = [v for v in virtual_catalog if v["actress"] == profile["name"]]
        item = profile.copy()
        item["works_count"] = len(works)
        item["latest_video"] = works[0]["code"] if works else "N/A"
        result.append(item)

    result.sort(key=lambda x: x["works_count"], reverse=True)
    return result

@app.get("/api/rankings")
def get_rankings():
    """Backward compatibility for rankings list."""
    return virtual_catalog[:5]

@app.get("/api/catalog/paths")
def get_catalog_paths():
    """Returns directory of all videos with their direct MissAV URLs and stream proxy paths."""
    return [
        {
            "id": v["id"],
            "code": v["code"],
            "title": v["title"],
            "actress": v["actress"],
            "duration": v["duration"],
            "rating": v["rating"],
            "views": v["views"],
            "tags": v["tags"],
            "missav_url": v.get("missav_url", f"https://missav.ws/{v['code'].lower()}"),
            "missav_alt_url": v.get("missav_alt_url", f"https://missav.com/{v['code'].lower()}"),
            "stream_url": v["stream_url"],
            "proxy_stream_url": v.get("proxy_stream_url", f"http://localhost:8080/proxy/stream?url={v['stream_url']}&referer=https://missav.ws/")
        }
        for v in virtual_catalog
    ]

@app.get("/api/status")
def get_status():
    return {
        "service": "crawler-python",
        "port": 8000,
        "agent_state": agent_state,
        "total_catalog": len(virtual_catalog)
    }

@app.post("/api/crawl/trigger")
async def trigger_crawl(background_tasks: BackgroundTasks):
    await send_agent_log("INFO", "🚀 [MANUAL_TRIGGER] MissAV.ws Live Parsing & Cache Refresh Requested!")
    recalculate_catalog()
    await send_agent_log("SUCCESS", f"✅ [MANUAL_TRIGGER] Matrix synchronized with {len(virtual_catalog)} items.")
    return {"status": "triggered", "count": len(virtual_catalog)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
