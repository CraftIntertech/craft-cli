package cmd

import (
	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var planVMCmd = &cobra.Command{
	Use:   "vm",
	Short: "List available VM plans",
	Run: func(cmd *cobra.Command, args []string) {
		params := map[string]string{}
		if nodeID, _ := cmd.Flags().GetString("node-id"); nodeID != "" {
			params["nodeId"] = nodeID
		}

		result := client.Get("/plans", params, true)
		plans := extractList(result, "plans")

		var rows [][]string
		for _, p := range plans {
			rows = append(rows, []string{
				getString(p, "id"),
				getString(p, "name"),
				getString(p, "cpu"),
				getString(p, "ram"),
				getString(p, "disk"),
				getString(p, "daily"),
				getString(p, "monthly"),
			})
		}

		output.PrintTable(rows, []string{"ID", "Name", "CPU", "RAM", "Disk", "Daily", "Monthly"})
	},
}

var planOSCmd = &cobra.Command{
	Use:   "os",
	Short: "List available OS templates",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/os-templates", nil, true)
		templates := extractList(result, "os_templates", "osTemplates", "templates")

		var rows [][]string
		for _, t := range templates {
			rows = append(rows, []string{
				getString(t, "id"),
				getString(t, "name"),
				getString(t, "type"),
			})
		}

		output.PrintTable(rows, []string{"ID", "Name", "Type"})
	},
}

var planDedicatedCmd = &cobra.Command{
	Use:   "dedicated",
	Short: "List available dedicated server plans",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/dedicated-plans", nil, false)
		plans := extractList(result, "plans", "dedicated_plans", "dedicatedPlans")

		var rows [][]string
		for _, p := range plans {
			rows = append(rows, []string{
				getString(p, "id"),
				getString(p, "name"),
				getString(p, "cpu"),
				getString(p, "ram"),
				getString(p, "disk"),
				getString(p, "bandwidth"),
				getString(p, "price"),
			})
		}

		output.PrintTable(rows, []string{"ID", "Name", "CPU", "RAM", "Disk", "Bandwidth", "Price"})
	},
}

var planColocationCmd = &cobra.Command{
	Use:   "colocation",
	Short: "List available colocation plans",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/colocation-plans", nil, false)
		plans := extractList(result, "plans", "colocation_plans", "colocationPlans")

		var rows [][]string
		for _, p := range plans {
			rows = append(rows, []string{
				getString(p, "id"),
				getString(p, "name"),
				getString(p, "size"),
				getString(p, "power"),
				getString(p, "bandwidth"),
				getString(p, "price"),
			})
		}

		output.PrintTable(rows, []string{"ID", "Name", "Size", "Power", "Bandwidth", "Price"})
	},
}

func init() {
	planVMCmd.Flags().String("node-id", "", "Filter plans by node ID")

	PlanCmd.AddCommand(planVMCmd)
	PlanCmd.AddCommand(planOSCmd)
	PlanCmd.AddCommand(planDedicatedCmd)
	PlanCmd.AddCommand(planColocationCmd)
}
