# MissAV Vibe System Goals & Scope

## 🎯 System Objectives
The **MissAV Vibe Streaming & Monitoring System** is an ad-free video streaming proxy and real-time Vibe Coding agent monitoring platform built for local developer experimentation and high-performance media delivery testing.

### Key Capabilities
1. **Ad-Free Stream Proxying**: Strip away ad overlay redirects and bypass anti-leech cross-origin policies by proxying m3u8 playlists and TS video segments via a Go reverse proxy with header spoofing (`Referer: https://missav.com/`).
2. **Real-time Vibe Agent Hook**: A unified WebSocket gateway in Go that broadcasts Python crawler agent lifecycle events, HTML parsing metrics, and ranking updates directly to an interactive developer UI terminal.
3. **Immersive Developer UI**: Dark glassmorphism frontend powered by Tailwind CSS and HLS.js, featuring a live ranking sidebar, smooth video player, and real-time streaming Vibe Terminal.
4. **State Machine Control (`control-state/`)**: Explicit state tracking and task management files enabling transparent inspection of agent goals, decisions, and system health.

## ⚡ Performance Targets
- **Proxy Latency**: Stream chunk forwarding delay < 50ms.
- **WebSocket Throughput**: Live log event broadcast latency < 20ms to all active UI clients.
- **Zero Ad Noise**: 100% clean video player environment free of popup scripts or tracking tags.
