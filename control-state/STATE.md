# System State & Runtime Dashboard

## 🚦 System Status Matrix
| Component | Port | Status | Protocol | Endpoint |
|---|---|---|---|---|
| **Go Proxy Gateway** | `:8080` | `READY` | HTTP / WS | `http://localhost:8080/proxy/stream` |
| **WebSocket Hub** | `:8080` | `LISTENING` | WS | `ws://localhost:8080/ws/client` |
| **Agent Hook Ingestion** | `:8080` | `ACTIVE` | HTTP POST | `http://localhost:8080/api/agent-hook` |
| **Python Crawler Engine**| `:8000` | `READY` | HTTP / Async | `http://localhost:8000/api/rankings` |
| **Frontend Vibe UI** | `:5500` / Local | `READY` | Web / HLS | `index.html` |

## 🔄 Active Agent Context
- **Current Mode**: `MOCK_CRAWLER_SIMULATION`
- **Agent Hook Loop**: `RUNNING` (Interval: 3.5s status push to Go Backend)
- **Active WebSocket Clients**: Managed dynamically by Go Hub
- **Active Stream Proxy Session**: Standby
