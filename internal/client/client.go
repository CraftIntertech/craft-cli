package client

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/CraftIntertech/craft-cli/internal/config"
)

const defaultTimeout = 30

// statusHints provides fallback error messages based on HTTP status code.
var statusHints = map[int]string{
	400: "Bad request. Please check your input.",
	401: "Authentication failed. Please log in again with 'craft auth login'.",
	403: "Permission denied. You don't have access to this resource.",
	404: "Resource not found.",
	409: "Conflict. The resource may already exist or is in a conflicting state.",
	422: "Validation error. Please check your input.",
	429: "Too many requests. Please wait a moment and try again.",
	500: "Internal server error. Please try again later.",
	502: "Bad gateway. The server is temporarily unavailable.",
	503: "Service unavailable. Please try again later.",
	504: "Gateway timeout. The server took too long to respond.",
}

// extractErrorMessage attempts to pull a human-readable error message from
// an API error response body. It checks several common JSON field patterns.
func extractErrorMessage(body []byte, statusCode int) string {
	var data map[string]interface{}
	if err := json.Unmarshal(body, &data); err != nil {
		if hint, ok := statusHints[statusCode]; ok {
			return hint
		}
		return fmt.Sprintf("Request failed with status %d", statusCode)
	}

	// Check top-level string fields.
	for _, key := range []string{"message", "error", "detail", "msg"} {
		if val, ok := data[key]; ok {
			if s, ok := val.(string); ok && s != "" {
				return s
			}
		}
	}

	// Check nested error.message.
	if errObj, ok := data["error"]; ok {
		if errMap, ok := errObj.(map[string]interface{}); ok {
			if msg, ok := errMap["message"]; ok {
				if s, ok := msg.(string); ok && s != "" {
					return s
				}
			}
		}
	}

	// Check "errors" field — could be an array or a dict.
	if errorsVal, ok := data["errors"]; ok {
		switch v := errorsVal.(type) {
		case []interface{}:
			var parts []string
			for _, item := range v {
				switch e := item.(type) {
				case string:
					parts = append(parts, e)
				case map[string]interface{}:
					if msg, ok := e["message"]; ok {
						parts = append(parts, fmt.Sprintf("%v", msg))
					} else if msg, ok := e["msg"]; ok {
						parts = append(parts, fmt.Sprintf("%v", msg))
					} else {
						b, _ := json.Marshal(e)
						parts = append(parts, string(b))
					}
				default:
					parts = append(parts, fmt.Sprintf("%v", e))
				}
			}
			if len(parts) > 0 {
				return strings.Join(parts, "; ")
			}
		case map[string]interface{}:
			var parts []string
			for field, msgs := range v {
				switch m := msgs.(type) {
				case []interface{}:
					for _, msg := range m {
						parts = append(parts, fmt.Sprintf("%s: %v", field, msg))
					}
				default:
					parts = append(parts, fmt.Sprintf("%s: %v", field, m))
				}
			}
			if len(parts) > 0 {
				return strings.Join(parts, "; ")
			}
		}
	}

	if hint, ok := statusHints[statusCode]; ok {
		return hint
	}
	return fmt.Sprintf("Request failed with status %d", statusCode)
}

// APIRequest performs an HTTP request to the API and returns the parsed JSON
// response. If authRequired is true the current access token is included as a
// Bearer token. timeout is in seconds; 0 means use the default (30s).
func APIRequest(method, path string, body interface{}, params map[string]string, authRequired bool, timeout int) (map[string]interface{}, error) {
	baseURL := config.GetBaseURL()
	url := strings.TrimRight(baseURL, "/") + "/" + strings.TrimLeft(path, "/")

	if timeout <= 0 {
		timeout = defaultTimeout
	}

	var bodyReader io.Reader
	if body != nil {
		jsonBytes, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal request body: %w", err)
		}
		bodyReader = bytes.NewReader(jsonBytes)
	}

	req, err := http.NewRequest(method, url, bodyReader)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	if authRequired {
		token := config.GetToken()
		if token == "" {
			return nil, fmt.Errorf("not authenticated. Please log in with 'craft auth login'")
		}
		req.Header.Set("Authorization", "Bearer "+token)
	}

	if len(params) > 0 {
		q := req.URL.Query()
		for k, v := range params {
			q.Set(k, v)
		}
		req.URL.RawQuery = q.Encode()
	}

	httpClient := &http.Client{
		Timeout: time.Duration(timeout) * time.Second,
	}

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		if len(respBody) == 0 {
			return map[string]interface{}{}, nil
		}
		var result map[string]interface{}
		if err := json.Unmarshal(respBody, &result); err != nil {
			return nil, fmt.Errorf("failed to parse response JSON: %w", err)
		}
		return result, nil
	}

	msg := extractErrorMessage(respBody, resp.StatusCode)
	return nil, fmt.Errorf("%s", msg)
}

// Get performs a GET request. On error it prints the message to stderr and exits.
func Get(path string, params map[string]string, auth bool) map[string]interface{} {
	result, err := APIRequest("GET", path, nil, params, auth, 0)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return result
}

// Post performs a POST request. On error it prints the message to stderr and exits.
func Post(path string, data map[string]interface{}, auth bool, timeout int) map[string]interface{} {
	result, err := APIRequest("POST", path, data, nil, auth, timeout)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return result
}

// Put performs a PUT request. On error it prints the message to stderr and exits.
func Put(path string, data map[string]interface{}, auth bool) map[string]interface{} {
	result, err := APIRequest("PUT", path, data, nil, auth, 0)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return result
}

// Patch performs a PATCH request. On error it prints the message to stderr and exits.
func Patch(path string, data map[string]interface{}, auth bool) map[string]interface{} {
	result, err := APIRequest("PATCH", path, data, nil, auth, 0)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return result
}

// Delete performs a DELETE request. On error it prints the message to stderr and exits.
func Delete(path string, auth bool) map[string]interface{} {
	result, err := APIRequest("DELETE", path, nil, nil, auth, 0)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return result
}
