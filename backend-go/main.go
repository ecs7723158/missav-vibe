package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
)

// WSHub manages active WebSocket client connections and broadcasts messages.
type WSHub struct {
	clients    map[*websocket.Conn]bool
	broadcast  chan []byte
	register   chan *websocket.Conn
	unregister chan *websocket.Conn
	mu         sync.Mutex
}

func newWSHub() *WSHub {
	return &WSHub{
		clients:    make(map[*websocket.Conn]bool),
		broadcast:  make(chan []byte, 256),
		register:   make(chan *websocket.Conn),
		unregister: make(chan *websocket.Conn),
	}
}

func (h *WSHub) run() {
	for {
		select {
		case conn := <-h.register:
			h.mu.Lock()
			h.clients[conn] = true
			h.mu.Unlock()
			log.Println("[WS Hub] New client connected. Total clients:", len(h.clients))
			// Send welcome message
			welcome, _ := json.Marshal(gin.H{
				"source":    "SYSTEM",
				"level":     "SUCCESS",
				"message":   "Connected to MissAV Vibe WebSocket Gateway",
				"timestamp": time.Now().Format("15:04:05.000"),
			})
			conn.WriteMessage(websocket.TextMessage, welcome)

		case conn := <-h.unregister:
			h.mu.Lock()
			if _, ok := h.clients[conn]; ok {
				delete(h.clients, conn)
				conn.Close()
				log.Println("[WS Hub] Client disconnected. Total clients:", len(h.clients))
			}
			h.mu.Unlock()

		case message := <-h.broadcast:
			h.mu.Lock()
			for conn := range h.clients {
				err := conn.WriteMessage(websocket.TextMessage, message)
				if err != nil {
					log.Println("[WS Hub] Write error, disconnecting client:", err)
					conn.Close()
					delete(h.clients, conn)
				}
			}
			h.mu.Unlock()
		}
	}
}

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow all origins for local vibe testing
	},
}

// AgentPayload defines incoming status broadcasts from Python agent or crawler
type AgentPayload struct {
	Source    string      `json:"source"`
	Level     string      `json:"level"`
	Message   string      `json:"message"`
	Timestamp string      `json:"timestamp,omitempty"`
	Data      interface{} `json:"data,omitempty"`
}

func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With, Range")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		c.Next()
	}
}

func main() {
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()
	r.Use(CORSMiddleware())

	hub := newWSHub()
	go hub.run()

	// 1. WebSocket Endpoint for Frontend
	r.GET("/ws/client", func(c *gin.Context) {
		conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
		if err != nil {
			log.Println("[WS] Upgrade error:", err)
			return
		}
		hub.register <- conn

		// Read pump to keep connection alive and detect close
		go func() {
			defer func() {
				hub.unregister <- conn
			}()
			for {
				_, _, err := conn.ReadMessage()
				if err != nil {
					break
				}
			}
		}()
	})

	// 2. Ingest Agent Hook Logs from Python Crawler/Agent
	r.POST("/api/agent-hook", func(c *gin.Context) {
		var payload AgentPayload
		if err := c.ShouldBindJSON(&payload); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid payload: " + err.Error()})
			return
		}

		if payload.Timestamp == "" {
			payload.Timestamp = time.Now().Format("15:04:05.000")
		}
		if payload.Source == "" {
			payload.Source = "AGENT"
		}
		if payload.Level == "" {
			payload.Level = "INFO"
		}

		msgBytes, err := json.Marshal(payload)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "JSON marshal failed"})
			return
		}

		// Broadcast to all connected WebSocket clients
		hub.broadcast <- msgBytes

		hub.mu.Lock()
		clientCount := len(hub.clients)
		hub.mu.Unlock()

		c.JSON(http.StatusOK, gin.H{
			"status":            "broadcasted",
			"connected_clients": clientCount,
		})
	})

	// 3. Stream Proxy Endpoint (/proxy/stream?url=...)
	r.GET("/proxy/stream", func(c *gin.Context) {
		targetURL := c.Query("url")
		if targetURL == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Missing 'url' query parameter"})
			return
		}

		req, err := http.NewRequestWithContext(c.Request.Context(), "GET", targetURL, nil)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create request: " + err.Error()})
			return
		}

		// Spoof headers to bypass MissAV anti-leech and referer checks
		req.Header.Set("Referer", "https://missav.com/")
		req.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
		req.Header.Set("Accept", "*/*")
		req.Header.Set("Accept-Language", "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7")

		// Pass through byte range requests for streaming TS video chunks
		if rangeHeader := c.GetHeader("Range"); rangeHeader != "" {
			req.Header.Set("Range", rangeHeader)
		}

		client := &http.Client{
			Timeout: 30 * time.Second,
		}

		resp, err := client.Do(req)
		if err != nil {
			c.JSON(http.StatusBadGateway, gin.H{"error": "Proxy request failed: " + err.Error()})
			return
		}
		defer resp.Body.Close()

		// Copy upstream response headers
		if contentType := resp.Header.Get("Content-Type"); contentType != "" {
			c.Writer.Header().Set("Content-Type", contentType)
		} else {
			c.Writer.Header().Set("Content-Type", "application/x-mpegURL")
		}

		if contentLength := resp.Header.Get("Content-Length"); contentLength != "" {
			c.Writer.Header().Set("Content-Length", contentLength)
		}
		if contentRange := resp.Header.Get("Content-Range"); contentRange != "" {
			c.Writer.Header().Set("Content-Range", contentRange)
		}
		if acceptRanges := resp.Header.Get("Accept-Ranges"); acceptRanges != "" {
			c.Writer.Header().Set("Accept-Ranges", acceptRanges)
		}

		// Enforce CORS for streaming
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "*")
		c.Writer.WriteHeader(resp.StatusCode)

		// Stream content directly to writer
		_, _ = io.Copy(c.Writer, resp.Body)
	})

	// Health Check Route
	r.GET("/health", func(c *gin.Context) {
		hub.mu.Lock()
		activeClients := len(hub.clients)
		hub.mu.Unlock()

		c.JSON(http.StatusOK, gin.H{
			"status":         "ok",
			"service":        "backend-go",
			"port":           8080,
			"active_clients": activeClients,
			"timestamp":      time.Now().Format(time.RFC3339),
		})
	})

	fmt.Println("🚀 Go Backend Proxy & WS Gateway running on http://localhost:8080")
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}
