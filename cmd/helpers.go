package cmd

import (
	"fmt"
	"os"
	"strings"

	"github.com/AlecAivazis/survey/v2"
	"github.com/CraftIntertech/craft-cli/internal/client"
)

// extractList extracts a list from an API response, checking common patterns.
func extractList(data map[string]interface{}, keys ...string) []map[string]interface{} {
	inner := data
	if d, ok := data["data"]; ok {
		switch v := d.(type) {
		case map[string]interface{}:
			inner = v
		case []interface{}:
			return toMapSlice(v)
		}
	}

	for _, key := range keys {
		if val, ok := inner[key]; ok {
			if arr, ok := val.([]interface{}); ok {
				return toMapSlice(arr)
			}
		}
	}

	for _, key := range []string{"items", "data"} {
		if val, ok := inner[key]; ok {
			if arr, ok := val.([]interface{}); ok {
				return toMapSlice(arr)
			}
		}
	}

	return nil
}

// extractObj extracts a single object from an API response.
func extractObj(data map[string]interface{}) map[string]interface{} {
	if d, ok := data["data"]; ok {
		if m, ok := d.(map[string]interface{}); ok {
			return m
		}
	}
	return data
}

// toMapSlice converts []interface{} to []map[string]interface{}.
func toMapSlice(arr []interface{}) []map[string]interface{} {
	var result []map[string]interface{}
	for _, item := range arr {
		if m, ok := item.(map[string]interface{}); ok {
			result = append(result, m)
		}
	}
	return result
}

// getString safely gets a string from a map.
func getString(m map[string]interface{}, key string) string {
	if val, ok := m[key]; ok {
		return fmt.Sprintf("%v", val)
	}
	return ""
}

// SelectVM fetches user VMs and lets the user pick one interactively.
func SelectVM(label string) string {
	if label == "" {
		label = "Select VM"
	}

	data := client.Get("/vms", map[string]string{"page": "1", "limit": "50"}, true)
	vms := extractList(data, "vms", "items")
	if len(vms) == 0 {
		fmt.Fprintln(os.Stderr, "Error: No VMs found.")
		os.Exit(1)
	}

	options := make([]string, len(vms))
	idMap := make(map[string]string)
	for i, vm := range vms {
		name := getString(vm, "name")
		status := getString(vm, "status")
		ip := getString(vm, "ip")
		if ip == "" {
			ip = getString(vm, "ipAddress")
		}
		display := fmt.Sprintf("%s (%s)", name, status)
		if ip != "" {
			display += " — " + ip
		}
		options[i] = display
		idMap[display] = getString(vm, "id")
	}

	var selected string
	prompt := &survey.Select{
		Message: label,
		Options: options,
	}
	if err := survey.AskOne(prompt, &selected); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return idMap[selected]
}

// SelectNode fetches nodes and lets the user pick one interactively.
func SelectNode(label string) string {
	if label == "" {
		label = "Select node"
	}

	data := client.Get("/nodes", nil, true)
	nodes := extractList(data, "nodes")
	if len(nodes) == 0 {
		fmt.Fprintln(os.Stderr, "Error: No nodes available.")
		os.Exit(1)
	}

	options := make([]string, len(nodes))
	idMap := make(map[string]string)
	for i, n := range nodes {
		name := getString(n, "name")
		if name == "" {
			name = getString(n, "hostname")
		}
		location := getString(n, "location")
		country := getString(n, "country")
		var parts []string
		if location != "" {
			parts = append(parts, location)
		}
		if country != "" {
			parts = append(parts, country)
		}
		display := name
		if len(parts) > 0 {
			display += " (" + strings.Join(parts, ", ") + ")"
		}
		options[i] = display
		idMap[display] = getString(n, "id")
	}

	var selected string
	prompt := &survey.Select{
		Message: label,
		Options: options,
	}
	if err := survey.AskOne(prompt, &selected); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return idMap[selected]
}

// SelectBillingType lets the user pick a billing cycle interactively.
func SelectBillingType(label string) string {
	if label == "" {
		label = "Billing type"
	}

	options := []string{"Daily", "Weekly", "Monthly", "Yearly"}
	valueMap := map[string]string{
		"Daily": "daily", "Weekly": "weekly", "Monthly": "monthly", "Yearly": "yearly",
	}

	var selected string
	prompt := &survey.Select{
		Message: label,
		Options: options,
		Default: "Monthly",
	}
	if err := survey.AskOne(prompt, &selected); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return valueMap[selected]
}

// SelectTicket fetches tickets and lets the user pick one interactively.
func SelectTicket(label string) string {
	if label == "" {
		label = "Select ticket"
	}

	data := client.Get("/tickets", nil, true)
	tickets := extractList(data, "tickets")
	if len(tickets) == 0 {
		fmt.Fprintln(os.Stderr, "Error: No tickets found.")
		os.Exit(1)
	}

	options := make([]string, len(tickets))
	idMap := make(map[string]string)
	for i, t := range tickets {
		tid := getString(t, "id")
		subject := getString(t, "subject")
		status := getString(t, "status")
		short := tid
		if len(tid) > 8 {
			short = tid[:8] + "..."
		}
		display := fmt.Sprintf("[%s] %s (%s)", status, subject, short)
		options[i] = display
		idMap[display] = tid
	}

	var selected string
	prompt := &survey.Select{
		Message: label,
		Options: options,
	}
	if err := survey.AskOne(prompt, &selected); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return idMap[selected]
}

// Confirm asks the user for a yes/no confirmation.
func Confirm(message string) bool {
	var result bool
	prompt := &survey.Confirm{
		Message: message,
		Default: false,
	}
	if err := survey.AskOne(prompt, &result); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return result
}

// PromptText prompts the user for text input.
func PromptText(message string) string {
	var result string
	prompt := &survey.Input{
		Message: message,
	}
	if err := survey.AskOne(prompt, &result); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return result
}

// PromptPassword prompts the user for secret input.
func PromptPassword(message string) string {
	var result string
	prompt := &survey.Password{
		Message: message,
	}
	if err := survey.AskOne(prompt, &result); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return result
}

// SelectHosting fetches the hosting list and lets the user pick one interactively.
func SelectHosting(label string) string {
	if label == "" {
		label = "Select hosting"
	}

	data := client.Get("/hosting", nil, true)
	items := extractList(data, "hosting", "items")
	if len(items) == 0 {
		fmt.Fprintln(os.Stderr, "Error: No hosting accounts found.")
		os.Exit(1)
	}

	options := make([]string, len(items))
	idMap := make(map[string]string)
	for i, h := range items {
		name := getString(h, "name")
		domain := getString(h, "domain")
		status := getString(h, "status")
		display := fmt.Sprintf("%s (%s) [%s]", name, domain, status)
		options[i] = display
		idMap[display] = getString(h, "id")
	}

	var selected string
	prompt := &survey.Select{
		Message: label,
		Options: options,
	}
	if err := survey.AskOne(prompt, &selected); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return idMap[selected]
}

// SelectOSTemplate fetches OS templates and lets the user pick one interactively.
func SelectOSTemplate(label string) string {
	if label == "" {
		label = "Select OS template"
	}

	data := client.Get("/os-templates", nil, true)
	items := extractList(data, "os_templates", "templates")
	if len(items) == 0 {
		fmt.Fprintln(os.Stderr, "Error: No OS templates found.")
		os.Exit(1)
	}

	options := make([]string, len(items))
	idMap := make(map[string]string)
	for i, t := range items {
		name := getString(t, "name")
		options[i] = name
		idMap[name] = getString(t, "id")
	}

	var selected string
	prompt := &survey.Select{
		Message: label,
		Options: options,
	}
	if err := survey.AskOne(prompt, &selected); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return idMap[selected]
}

// SelectPlan fetches plans for a given node and lets the user pick one interactively.
func SelectPlan(nodeID, label string) string {
	if label == "" {
		label = "Select plan"
	}

	params := map[string]string{"nodeId": nodeID}
	data := client.Get("/plans", params, true)
	items := extractList(data, "plans")
	if len(items) == 0 {
		fmt.Fprintln(os.Stderr, "Error: No plans found for this node.")
		os.Exit(1)
	}

	options := make([]string, len(items))
	idMap := make(map[string]string)
	for i, p := range items {
		name := getString(p, "name")
		options[i] = name
		idMap[name] = getString(p, "id")
	}

	var selected string
	prompt := &survey.Select{
		Message: label,
		Options: options,
	}
	if err := survey.AskOne(prompt, &selected); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	return idMap[selected]
}

// SelectSSHKeys fetches SSH keys and lets the user pick multiple interactively.
// Returns comma-separated IDs of selected keys.
func SelectSSHKeys() string {
	data := client.Get("/ssh-keys", nil, true)
	items := extractList(data, "ssh_keys", "keys")
	if len(items) == 0 {
		fmt.Fprintln(os.Stderr, "No SSH keys found.")
		return ""
	}

	options := make([]string, len(items))
	idMap := make(map[string]string)
	for i, k := range items {
		name := getString(k, "name")
		options[i] = name
		idMap[name] = getString(k, "id")
	}

	var selected []string
	prompt := &survey.MultiSelect{
		Message: "Select SSH keys:",
		Options: options,
	}
	if err := survey.AskOne(prompt, &selected); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	ids := make([]string, len(selected))
	for i, s := range selected {
		ids[i] = idMap[s]
	}

	return strings.Join(ids, ",")
}
