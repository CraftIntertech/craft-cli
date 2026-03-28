package cmd

import (
	"fmt"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var rdnsGetCmd = &cobra.Command{
	Use:   "get [VM_ID]",
	Short: "Get reverse DNS record for a VM",
	Run: func(cmd *cobra.Command, args []string) {
		vmID := ""
		if len(args) > 0 {
			vmID = args[0]
		}
		if vmID == "" {
			vmID = SelectVM("Select VM for rDNS")
		}

		result := client.Get(fmt.Sprintf("/vms/%s/rdns", vmID), nil, true)
		output.PrintItem(extractObj(result))
	},
}

var rdnsSetCmd = &cobra.Command{
	Use:   "set [VM_ID]",
	Short: "Set reverse DNS record for a VM",
	Run: func(cmd *cobra.Command, args []string) {
		vmID := ""
		if len(args) > 0 {
			vmID = args[0]
		}
		if vmID == "" {
			vmID = SelectVM("Select VM for rDNS")
		}

		hostname, _ := cmd.Flags().GetString("hostname")
		if hostname == "" {
			hostname = PromptText("Enter FQDN hostname:")
		}

		body := map[string]interface{}{
			"hostname": hostname,
		}

		result := client.Put(fmt.Sprintf("/vms/%s/rdns", vmID), body, true)
		output.PrintSuccess("Reverse DNS record set.")
		output.PrintItem(extractObj(result))
	},
}

var rdnsDeleteCmd = &cobra.Command{
	Use:   "delete [VM_ID]",
	Short: "Delete reverse DNS record for a VM",
	Run: func(cmd *cobra.Command, args []string) {
		vmID := ""
		if len(args) > 0 {
			vmID = args[0]
		}
		if vmID == "" {
			vmID = SelectVM("Select VM for rDNS deletion")
		}

		if !Confirm("Are you sure you want to delete the reverse DNS record?") {
			output.PrintInfo("Cancelled.")
			return
		}

		client.Delete(fmt.Sprintf("/vms/%s/rdns", vmID), true)
		output.PrintSuccess("Reverse DNS record deleted.")
	},
}

func init() {
	rdnsSetCmd.Flags().String("hostname", "", "FQDN hostname for reverse DNS")

	RDNSCmd.AddCommand(rdnsGetCmd)
	RDNSCmd.AddCommand(rdnsSetCmd)
	RDNSCmd.AddCommand(rdnsDeleteCmd)
}
