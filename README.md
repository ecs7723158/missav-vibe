# MissAV 去廣告串流優化平台與 Vibe Coding 監控系統

> **MissAV Vibe Streaming Optimization Platform & Agent Monitoring System**
> 本專案為結合 **Go 高效反向代理**、**Python FastAPI 爬蟲 Agent 腦部**與 **Tailwind CSS + HLS.js 極客視覺化前端** 的全端影音優化與即時 Vibe Terminal 監控系統。

---

## 🏗️ 系統總覽架構圖 (Architecture)

```mermaid
flowchart TD
    subgraph Frontend ["視覺化前端 (frontend/index.html)"]
        UI["Tailwind CSS + HLS.js 沉浸播放器"]
        TERM["Vibe Terminal (WebSocket 客戶端)"]
        SIDE["虛擬排行榜 (Virtual Rankings Matrix)"]
    </div>

    subgraph GoBackend ["Go 服務閘道 (backend-go - Port 8080)"]
        PROXY["/proxy/stream<br/>(Header Spoofing & m3u8/TS 流轉發)"]
        WSHUB["/ws/client<br/>(Gorilla WebSocket Broadcaster)"]
        HOOK["/api/agent-hook<br/>(Agent Status Ingestion)"]
    end

    subgraph PyCrawler ["Python 爬蟲腦部 (crawler-python - Port 8000)"]
        API["FastAPI App (/api/rankings)"]
        PARSER["Mock MissAV 頁面解析 & 熱度矩陣計算"]
        LOOP["Async Agent Broadcaster Loop"]
    end

    SIDE -->|HTTP GET /api/rankings| API
    UI -->|Proxy Request url=m3u8| PROXY
    PROXY -->|Referer: missav.com| TargetCDN["MissAV / Target CDN"]
    LOOP -->|HTTP POST Agent Logs| HOOK
    HOOK --> WSHUB
    WSHUB -->|WS Live Stream| TERM
```

---

## 📁 專案目錄結構

```
missav-vibe/
├── frontend/                  # 視覺化網頁與 Terminal 面板
│   └── index.html             # Tailwind CSS Dark Cyberpunk + HLS.js + WS Client
├── backend-go/                # Go 影音串流 Proxy 與 WebSocket 閘道 (Port 8080)
│   ├── main.go                # Gin 反向代理 + Gorilla WebSocket Hub
│   └── go.mod                 # Go 依賴設定
├── crawler-python/            # Python 爬蟲與 Agent 腦部 (Port 8000)
│   ├── main.py                # FastAPI 爬蟲、熱度排行榜計算機與 Agent 廣播 Loop
│   └── requirements.txt       # Python 依賴清單
├── control-state/             # Agent 任務與系統狀態機 (Transparent Audit)
│   ├── GOAL.md                # 系統目標與效能指標
│   ├── STATE.md               # 運行節點狀態矩陣
│   ├── TASKS.md               # 任務追蹤清單
│   └── DECISIONS.md           # 系統架構決策紀錄 (ADR)
└── README.md                  # 本系統說明文件與啟動手冊
```

---

## 🚀 快速啟動指南 (Quick Start)

### 步驟 1：啟動 Go 反向代理與 WebSocket 閘道 (Port 8080)
```bash
cd backend-go
go run main.go
```
*正常啟動後將在 `http://localhost:8080` 監聽代理與 WebSocket 請求。*

---

### 步驟 2：啟動 Python 爬蟲與 Agent 腦部 (Port 8000)
```bash
cd crawler-python
# 安裝依賴 (建議在 venv 環境下執行)
pip install -r requirements.txt

# 啟動 FastAPI 服務
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*正常啟動後 Python Agent 將自動開啟背景迴圈，每隔 3.5 秒向 Go `/api/agent-hook` 推送爬蟲與熱度計算日誌。*

---

### 步驟 3：開啟前端面板 (Frontend UI)
您可以用以下任一方式開啟前端介面：
1. **直接點擊開啟**：雙擊 `frontend/index.html` 在瀏覽器中開啟。
2. **使用 Python HTTP 伺服器 (推薦)**：
   ```bash
   cd frontend
   python3 -m http.server 5500
   ```
   開啟瀏覽器造訪 `http://localhost:5500`。

---

## 🎮 操作功能說明

1. **左側「Virtual Ranking Matrix」**：
   - 即時載入 Python 爬蟲產出的影片熱度排行榜，包含封面圖、女優、評分與點閱數。
   - 點擊任一影片卡片即可將 m3u8 串流載入中央播放器。
2. **中央「HLS Immersive Player」**：
   - 預設經由 Go Proxy (`http://localhost:8080/proxy/stream?url=...`) 進行 Header 偽造與 m3u8 解密播放。
   - 支援貼上任意自訂 `.m3u8` 網址點擊 **Proxy Play** 進行去廣告與破除跨域播放。
3. **右側/底部「Vibe Agent Terminal」**：
   - 透過 WebSocket `ws://localhost:8080/ws/client` 即時連線。
   - 即時顯示 Python 爬蟲 Agent 抓取 DOM、解析標籤、計算熱度與驗證串流標頭的完整 Log。
   - 支援 `ALL / INFO / SUCCESS / CRAWLER` 分類過濾、自動滾動與日誌清空。

---

## ⚖️ 免責聲明 (Legal Disclaimer)

> **IMPORTANT**
> 本專案 (`missav-vibe`) 僅供**本地技術研究、網路協定測試、Go/Python 全端架構開發與 Vibe Coding 實驗測試**使用。
> 1. 本專案程式碼中之爬蟲邏輯與數據資料庫皆採 Mock 模擬數據測試。
> 2. 請勿將本代理伺服器或爬蟲程式用於非法下載、商業轉售或侵犯著作權之行為。
> 3. 使用者需自行承擔因不正當使用所引發之相關法律責任。
