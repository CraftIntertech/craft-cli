package cmd

import (
	"fmt"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var nodeListCmd = &cobra.Command{
	Use:   "list",
	Short: "List all nodes",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/nodes", nil, true)
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

var nodeHardwareCmd = &cobra.Command{
	Use:   "hardware [NODE_ID]",
	Short: "Show hardware details for a node",
	Run: func(cmd *cobra.Command, args []string) {
		nodeID := ""
		if len(args) > 0 {
			nodeID = args[0]
		}
		if nodeID == "" {
			nodeID = SelectNode("Select node for hardware info")
		}

		result := client.Get(fmt.Sprintf("/nodes/%s/hardware", nodeID), nil, true)
		output.PrintItem(extractObj(result))
	},
}

func init() {
	NodeCmd.AddCommand(nodeListCmd)
	NodeCmd.AddCommand(nodeHardwareCmd)
}
