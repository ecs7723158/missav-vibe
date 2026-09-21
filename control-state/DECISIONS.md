# Architecture Decision Records (ADR)

## ADR-001: Header Spoofing Strategy for Stream Reverse Proxy
- **Context**: MissAV and related CDN hosts restrict direct embedding and cross-origin video segment requests using `Referer` and `User-Agent` headers checks.
- **Decision**: Implement a Go-based streaming proxy using `net/http` and `Gin`. For every request sent to `/proxy/stream?url=...`, the proxy attaches:
  - `Referer: https://missav.com/`
  - `User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`
  - `Access-Control-Allow-Origin: *` CORS header attached to responses.
- **Consequences**: Enables frontend HLS players (like HLS.js) to play restricted m3u8 streams smoothly without CORS or 403 Forbidden errors.

## ADR-002: Dual-Service Decoupled Architecture (Go + Python)
- **Context**: High-concurrency stream chunk proxying requires low resource overhead, while web crawling and AI/Agent data processing benefit from Python's rich ecosystem.
- **Decision**: Use Go for high-throughput HTTP proxying and WebSocket broadcasting (Port 8080), and Python FastAPI for data scraping, ranking calculations, and agent loops (Port 8000).
- **Consequences**: Maximizes execution speed while keeping Python agent logic modular and easy to extend.

## ADR-003: Real-Time Event Bus via HTTP Hook to WebSocket Hub
- **Context**: Python agent logs need to be displayed instantly on the frontend UI without establishing complex multi-way WebSockets in Python.
- **Decision**: Python sends HTTP POST payloads to Go's `/api/agent-hook`. Go's in-memory WebSocket Hub immediately broadcasts these JSON messages to all `/ws/client` connections.
- **Consequences**: Ultra-low complexity, reliable decoupled log streaming.
