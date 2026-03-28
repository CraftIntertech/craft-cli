package cmd

import (
	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var systemStatusCmd = &cobra.Command{
	Use:   "status",
	Short: "Show system status",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/system/status", nil, false)
		output.PrintItem(extractObj(result))
	},
}

var systemPlansCmd = &cobra.Command{
	Use:   "plans",
	Short: "List system plans",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/system/plans", nil, false)
		plans := extractList(result, "plans")

		var rows [][]string
		for _, p := range plans {
			rows = append(rows, []string{
				getString(p, "id"),
				getString(p, "name"),
				getString(p, "type"),
				getString(p, "price"),
			})
		}

		output.PrintTable(rows, []string{"ID", "Name", "Type", "Price"})
	},
}

var systemNodesCmd = &cobra.Command{
	Use:   "nodes",
	Short: "List system nodes",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/system/nodes", nil, false)
		nodes := extractList(result, "nodes")

		var rows [][]string
		for _, n := range nodes {
			rows = append(rows, []string{
				getString(n, "id"),
				getString(n, "name"),
				getString(n, "location"),
				getString(n, "country"),
				getString(n, "status"),
			})
		}

		output.PrintTable(rows, []string{"ID", "Name", "Location", "Country", "Status"})
	},
}

func init() {
	SystemCmd.AddCommand(systemStatusCmd)
	SystemCmd.AddCommand(systemPlansCmd)
	SystemCmd.AddCommand(systemNodesCmd)
}
