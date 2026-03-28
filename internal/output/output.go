package output

import (
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strings"
	"unicode"

	"github.com/fatih/color"
)

// Status color categories.
var greenStatuses = map[string]bool{
	"running":   true,
	"active":    true,
	"online":    true,
	"enabled":   true,
	"open":      true,
	"paid":      true,
	"completed": true,
	"success":   true,
}

var redStatuses = map[string]bool{
	"stopped":   true,
	"inactive":  true,
	"offline":   true,
	"disabled":  true,
	"deleted":   true,
	"failed":    true,
	"error":     true,
	"closed":    true,
	"expired":   true,
	"suspended": true,
}

var yellowStatuses = map[string]bool{
	"pending":      true,
	"creating":     true,
	"starting":     true,
	"stopping":     true,
	"rebooting":    true,
	"resizing":     true,
	"reinstalling": true,
	"processing":   true,
}

// ColorizeStatus returns the status string wrapped in the appropriate color.
func ColorizeStatus(val string) string {
	lower := strings.ToLower(val)
	if greenStatuses[lower] {
		return color.GreenString(val)
	}
	if redStatuses[lower] {
		return color.RedString(val)
	}
	if yellowStatuses[lower] {
		return color.YellowString(val)
	}
	return val
}

// isStatusField returns true if the key looks like a status-related field.
func isStatusField(key string) bool {
	lower := strings.ToLower(key)
	return lower == "status" || lower == "state" || strings.HasSuffix(lower, "_status") || strings.HasSuffix(lower, "_state")
}

// camelToTitle converts a camelCase or snake_case key to Title Case label.
// Examples: "firstName" -> "First Name", "base_url" -> "Base Url",
// "serverID" -> "Server ID", "cpuUsage" -> "Cpu Usage".
func camelToTitle(s string) string {
	// First handle snake_case: replace underscores with spaces.
	s = strings.ReplaceAll(s, "_", " ")

	if !strings.Contains(s, " ") {
		// Handle camelCase: insert space before each uppercase letter
		// that follows a lowercase letter.
		var result []rune
		runes := []rune(s)
		for i, r := range runes {
			if i > 0 && unicode.IsUpper(r) {
				prev := runes[i-1]
				if unicode.IsLower(prev) {
					result = append(result, ' ')
				} else if unicode.IsUpper(prev) && i+1 < len(runes) && unicode.IsLower(runes[i+1]) {
					// Handle sequences like "serverID" -> keep "ID" together,
					// but "IDName" -> "ID Name".
					result = append(result, ' ')
				}
			}
			result = append(result, r)
		}
		s = string(result)
	}

	// Title-case each word.
	words := strings.Fields(s)
	for i, w := range words {
		if len(w) > 0 {
			// Check if the word is all uppercase and length > 1 (likely an acronym).
			allUpper := true
			for _, r := range w {
				if !unicode.IsUpper(r) && !unicode.IsDigit(r) {
					allUpper = false
					break
				}
			}
			if allUpper && len(w) > 1 {
				words[i] = w // Keep acronyms as-is (e.g., "ID", "CPU").
			} else {
				words[i] = strings.ToUpper(w[:1]) + strings.ToLower(w[1:])
			}
		}
	}
	return strings.Join(words, " ")
}

// PrintJSON outputs data as pretty-printed JSON.
func PrintJSON(data interface{}) {
	out, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error formatting JSON: %v\n", err)
		return
	}
	fmt.Println(string(out))
}

// PrintTable renders data as a formatted ASCII table.
func PrintTable(rows [][]string, headers []string) {
	if len(headers) == 0 {
		return
	}

	// Calculate column widths
	widths := make([]int, len(headers))
	for i, h := range headers {
		widths[i] = len(h)
	}
	for _, row := range rows {
		for i, cell := range row {
			if i < len(widths) && len(cell) > widths[i] {
				widths[i] = len(cell)
			}
		}
	}

	// Build separator
	sepParts := make([]string, len(widths))
	for i, w := range widths {
		sepParts[i] = strings.Repeat("-", w+2)
	}

	// Print header
	headerColor := color.New(color.Bold)
	for i, h := range headers {
		if i > 0 {
			fmt.Print("  ")
		}
		headerColor.Printf("%-*s", widths[i], h)
	}
	fmt.Println()

	// Print separator
	for i, s := range sepParts {
		if i > 0 {
			fmt.Print("  ")
		}
		fmt.Print(s)
	}
	fmt.Println()

	// Print rows with status coloring
	statusCols := make(map[int]bool)
	for i, h := range headers {
		lower := strings.ToLower(h)
		if lower == "status" || lower == "state" {
			statusCols[i] = true
		}
	}

	for _, row := range rows {
		for i := 0; i < len(headers); i++ {
			if i > 0 {
				fmt.Print("  ")
			}
			cell := ""
			if i < len(row) {
				cell = row[i]
			}
			if statusCols[i] {
				// Pad then colorize
				padded := fmt.Sprintf("%-*s", widths[i], cell)
				fmt.Print(ColorizeStatus(padded))
			} else {
				fmt.Printf("%-*s", widths[i], cell)
			}
		}
		fmt.Println()
	}
}

// PrintSuccess prints a green success message.
func PrintSuccess(msg string) {
	color.Green("\u2713 %s", msg)
}

// PrintWarning prints a yellow warning message.
func PrintWarning(msg string) {
	color.Yellow("\u26a0 %s", msg)
}

// PrintError prints a red error message.
func PrintError(msg string) {
	color.Red("\u2717 %s", msg)
}

// PrintInfo prints a cyan info message.
func PrintInfo(msg string) {
	color.Cyan("\u2139 %s", msg)
}

// formatValue converts a value to a display string with appropriate coloring.
func formatValue(key string, val interface{}) string {
	if val == nil {
		dim := color.New(color.Faint)
		return dim.Sprint("-")
	}

	switch v := val.(type) {
	case bool:
		if v {
			return color.GreenString("Yes")
		}
		return color.RedString("No")
	case []interface{}:
		parts := make([]string, 0, len(v))
		for _, item := range v {
			parts = append(parts, fmt.Sprintf("%v", item))
		}
		return strings.Join(parts, ", ")
	case map[string]interface{}:
		b, err := json.Marshal(v)
		if err != nil {
			return fmt.Sprintf("%v", v)
		}
		return string(b)
	default:
		s := fmt.Sprintf("%v", v)
		if isStatusField(key) {
			return ColorizeStatus(s)
		}
		return s
	}
}

// PrintItem pretty-prints a single item as aligned key-value pairs.
// If the data contains a "data" key, it extracts that value first.
// Nested maps are flattened: child keys are added first, then parent keys
// override on conflict.
func PrintItem(data interface{}) {
	var m map[string]interface{}

	switch v := data.(type) {
	case map[string]interface{}:
		m = v
	default:
		// Fall back to JSON encoding and re-parsing.
		b, err := json.Marshal(data)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error formatting output: %v\n", err)
			return
		}
		if err := json.Unmarshal(b, &m); err != nil {
			// Not a map-like structure, just print as JSON.
			PrintJSON(data)
			return
		}
	}

	// Extract "data" key if present and it's a map.
	if dataVal, ok := m["data"]; ok {
		if dataMap, ok := dataVal.(map[string]interface{}); ok {
			m = dataMap
		}
	}

	// Flatten nested maps: child keys first, then parent keys override.
	flat := make(map[string]interface{})
	for _, v := range m {
		if nested, ok := v.(map[string]interface{}); ok {
			// Add child keys first.
			for ck, cv := range nested {
				flat[ck] = cv
			}
		}
	}
	// Now add parent keys (they override child keys on conflict).
	for k, v := range m {
		if _, ok := v.(map[string]interface{}); !ok {
			flat[k] = v
		}
	}

	// Collect and sort keys.
	keys := make([]string, 0, len(flat))
	for k := range flat {
		keys = append(keys, k)
	}
	sort.Strings(keys)

	// Find max label width for alignment.
	maxWidth := 0
	labels := make(map[string]string, len(keys))
	for _, k := range keys {
		label := camelToTitle(k)
		labels[k] = label
		if len(label) > maxWidth {
			maxWidth = len(label)
		}
	}

	// Print aligned key-value pairs.
	labelColor := color.New(color.FgCyan, color.Bold)
	for _, k := range keys {
		label := labels[k]
		valStr := formatValue(k, flat[k])
		labelColor.Printf("%-*s", maxWidth+2, label+":")
		fmt.Printf(" %s\n", valStr)
	}
}

// PrintPageInfo displays pagination information extracted from a response.
// It looks for "total", "total_count", or "count" in the data map and
// calculates the total number of pages.
func PrintPageInfo(data map[string]interface{}, page, limit int) {
	total := 0
	found := false

	for _, key := range []string{"total", "total_count", "count"} {
		if val, ok := data[key]; ok {
			switch v := val.(type) {
			case float64:
				total = int(v)
				found = true
			case int:
				total = v
				found = true
			}
			if found {
				break
			}
		}
	}

	if !found || total <= 0 {
		return
	}

	totalPages := (total + limit - 1) / limit
	dim := color.New(color.Faint)
	dim.Printf("\nPage %d of %d (total: %d items)\n", page, totalPages, total)
}
