package cmd

import (
	"fmt"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var agentEnableCmd = &cobra.Command{
	Use:   "enable [VM_ID]",
	Short: "Enable the server agent on a VM",
	Run: func(cmd *cobra.Command, args []string) {
		vmID := ""
		if len(args) > 0 {
			vmID = args[0]
		}
		if vmID == "" {
			vmID = SelectVM("Select VM to enable agent")
		}

		result := client.Post(fmt.Sprintf("/vms/%s/agent/enable", vmID), nil, true, 0)
		output.PrintSuccess("Agent enabled.")
		output.PrintItem(extractObj(result))
	},
}

var agentInfoCmd = &cobra.Command{
	Use:   "info [VM_ID]",
	Short: "Show agent information for a VM",
	Run: func(cmd *cobra.Command, args []string) {
		vmID := ""
		if len(args) > 0 {
			vmID = args[0]
		}
		if vmID == "" {
			vmID = SelectVM("Select VM for agent info")
		}

		result := client.Get(fmt.Sprintf("/vms/%s/agent/info", vmID), nil, true)
		output.PrintItem(extractObj(result))
	},
}

var agentFstrimCmd = &cobra.Command{
	Use:   "fstrim [VM_ID]",
	Short: "Run fstrim on a VM via the agent",
	Run: func(cmd *cobra.Command, args []string) {
		vmID := ""
		if len(args) > 0 {
			vmID = args[0]
		}
		if vmID == "" {
			vmID = SelectVM("Select VM for fstrim")
		}

		result := client.Post(fmt.Sprintf("/vms/%s/agent/fstrim", vmID), nil, true, 0)
		output.PrintSuccess("Fstrim completed.")
		output.PrintItem(extractObj(result))
	},
}

func init() {
	AgentCmd.AddCommand(agentEnableCmd)
	AgentCmd.AddCommand(agentInfoCmd)
	AgentCmd.AddCommand(agentFstrimCmd)
}
