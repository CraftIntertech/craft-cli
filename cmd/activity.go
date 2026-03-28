package cmd

import (
	"fmt"
	"strconv"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var activityCmd = &cobra.Command{
	Use:   "activity",
	Short: "View account activity log",
	Run: func(cmd *cobra.Command, args []string) {
		page, _ := cmd.Flags().GetInt("page")
		limit, _ := cmd.Flags().GetInt("limit")

		params := map[string]string{
			"page":  strconv.Itoa(page),
			"limit": strconv.Itoa(limit),
		}

		result := client.Get("/activity", params, true)

		// Extract the activity list from the response.
		var items []interface{}
		if data, ok := result["data"].([]interface{}); ok {
			items = data
		} else {
			// Fallback: the response itself may be the list wrapper.
			items = nil
		}

		headers := []string{"Action", "Description", "IP", "Date"}
		var rows [][]string

		for _, item := range items {
			entry, ok := item.(map[string]interface{})
			if !ok {
				continue
			}
			action := fmt.Sprintf("%v", entry["action"])
			description := fmt.Sprintf("%v", entry["description"])
			ip := fmt.Sprintf("%v", entry["ip"])
			date := fmt.Sprintf("%v", entry["date"])
			rows = append(rows, []string{action, description, ip, date})
		}

		output.PrintTable(rows, headers)

		// Show pagination info if available.
		output.PrintPageInfo(result, page, limit)
	},
}

func init() {
	activityCmd.Flags().Int("page", 1, "Page number")
	activityCmd.Flags().Int("limit", 20, "Items per page")
	rootCmd.AddCommand(activityCmd)
}
