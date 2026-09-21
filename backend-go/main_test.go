package main

import (
	"net/url"
	"strings"
	"testing"
)

func TestURLResolution(t *testing.T) {
	baseURL, err := url.Parse("https://surrit.com/hls/test/playlist.m3u8")
	if err != nil {
		t.Fatalf("Failed to parse base URL: %v", err)
	}

	relativeURL := "720p/video.m3u8"
	rel, err := url.Parse(relativeURL)
	if err != nil {
		t.Fatalf("Failed to parse relative URL: %v", err)
	}

	resolved := baseURL.ResolveReference(rel).String()
	expected := "https://surrit.com/hls/test/720p/video.m3u8"
	if resolved != expected {
		t.Errorf("Expected %s, got %s", expected, resolved)
	}
}

func TestM3U8RewriteFormat(t *testing.T) {
	line := "https://example.com/segment1.ts"
	customReferer := "https://missav.ws/"
	
	proxied := "/proxy/stream?url=" + url.QueryEscape(line) + "&referer=" + url.QueryEscape(customReferer)
	if !strings.Contains(proxied, "/proxy/stream?url=") {
		t.Errorf("Proxied string missing base proxy route")
	}
	if !strings.Contains(proxied, "referer=https%3A%2F%2Fmissav.ws%2F") {
		t.Errorf("Custom referer not properly query escaped")
	}
}
