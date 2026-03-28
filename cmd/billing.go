package cmd

import (
	"fmt"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var billingShowCmd = &cobra.Command{
	Use:   "show [VM_ID]",
	Short: "Show billing information for a VM",
	Run: func(cmd *cobra.Command, args []string) {
		vmID := ""
		if len(args) > 0 {
			vmID = args[0]
		}
		if vmID == "" {
			vmID = SelectVM("Select VM for billing")
		}

		result := client.Get(fmt.Sprintf("/vms/%s/billing", vmID), nil, true)
		output.PrintItem(extractObj(result))
	},
}

var billingRenewCmd = &cobra.Command{
	Use:   "renew [VM_ID]",
	Short: "Renew a VM billing cycle",
	Run: func(cmd *cobra.Command, args []string) {
		vmID := ""
		if len(args) > 0 {
			vmID = args[0]
		}
		if vmID == "" {
			vmID = SelectVM("Select VM to renew")
		}

		billingType, _ := cmd.Flags().GetString("billing-type")
		if billingType == "" {
			billingType = SelectBillingType("Select billing type")
		}

		body := map[string]interface{}{
			"billingType": billingType,
		}

		result := client.Post(fmt.Sprintf("/vms/%s/renew", vmID), body, true, 0)
		output.PrintSuccess("VM renewed successfully.")
		output.PrintItem(extractObj(result))
	},
}

var billingAutoRenewCmd = &cobra.Command{
	Use:   "auto-renew [VM_ID]",
	Short: "Enable or disable auto-renewal for a VM",
	Run: func(cmd *cobra.Command, args []string) {
		vmID := ""
		if len(args) > 0 {
			vmID = args[0]
		}
		if vmID == "" {
			vmID = SelectVM("Select VM for auto-renew")
		}

		enable, _ := cmd.Flags().GetBool("enable")
		disable, _ := cmd.Flags().GetBool("disable")

		var autoRenew bool
		if enable {
			autoRenew = true
		} else if disable {
			autoRenew = false
		} else {
			autoRenew = Confirm("Enable auto-renewal?")
		}

		body := map[string]interface{}{
			"autoRenew": autoRenew,
		}

		client.Patch(fmt.Sprintf("/vms/%s/auto-renew", vmID), body, true)
		if autoRenew {
			output.PrintSuccess("Auto-renewal enabled.")
		} else {
			output.PrintSuccess("Auto-renewal disabled.")
		}
	},
}

func init() {
	billingRenewCmd.Flags().String("billing-type", "", "Billing type (daily, weekly, monthly, yearly)")

	billingAutoRenewCmd.Flags().Bool("enable", false, "Enable auto-renewal")
	billingAutoRenewCmd.Flags().Bool("disable", false, "Disable auto-renewal")

	BillingCmd.AddCommand(billingShowCmd)
	BillingCmd.AddCommand(billingRenewCmd)
	BillingCmd.AddCommand(billingAutoRenewCmd)
}
