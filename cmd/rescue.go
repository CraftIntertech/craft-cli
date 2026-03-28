package cmd

import (
	"fmt"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var rescueEnableCmd = &cobra.Command{
	Use:   "enable [VM_ID]",
	Short: "Enable rescue mode for a VM",
	Run: func(cmd *cobra.Command, args []string) {
		vmID := ""
		if len(args) > 0 {
			vmID = args[0]
		}
		if vmID == "" {
			vmID = SelectVM("Select VM to enable rescue mode")
		}

		result := client.Post(fmt.Sprintf("/vms/%s/rescue/enable", vmID), nil, true, 0)
		output.PrintSuccess("Rescue mode enabled.")
		output.PrintItem(extractObj(result))
	},
}

var rescueDisableCmd = &cobra.Command{
	Use:   "disable [VM_ID]",
	Short: "Disable rescue mode for a VM",
	Run: func(cmd *cobra.Command, args []string) {
		vmID := ""
		if len(args) > 0 {
			vmID = args[0]
		}
		if vmID == "" {
			vmID = SelectVM("Select VM to disable rescue mode")
		}

		result := client.Post(fmt.Sprintf("/vms/%s/rescue/disable", vmID), nil, true, 0)
		output.PrintSuccess("Rescue mode disabled.")
		output.PrintItem(extractObj(result))
	},
}

func init() {
	RescueCmd.AddCommand(rescueEnableCmd)
	RescueCmd.AddCommand(rescueDisableCmd)
}
