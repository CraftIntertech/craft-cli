package cmd

import (
	"fmt"
	"os"
	"strconv"

	"github.com/AlecAivazis/survey/v2"
	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

func init() {
	// firewall list
	firewallListCmd := &cobra.Command{
		Use:   "list [VM_ID]",
		Short: "List firewall rules for a VM",
		Args:  cobra.MaximumNArgs(1),
		Run:   firewallListRun,
	}

	// firewall add
	firewallAddCmd := &cobra.Command{
		Use:   "add [VM_ID]",
		Short: "Add a firewall rule to a VM",
		Args:  cobra.MaximumNArgs(1),
		Run:   firewallAddRun,
	}
	firewallAddCmd.Flags().String("type", "", "Rule type: in or out")
	firewallAddCmd.Flags().String("action", "", "Rule action: ACCEPT, DROP, or REJECT")
	firewallAddCmd.Flags().String("proto", "", "Protocol: tcp, udp, or icmp")
	firewallAddCmd.Flags().String("dport", "", "Destination port")
	firewallAddCmd.Flags().String("sport", "", "Source port")
	firewallAddCmd.Flags().String("source", "", "Source CIDR")
	firewallAddCmd.Flags().String("dest", "", "Destination CIDR")
	firewallAddCmd.Flags().String("comment", "", "Rule comment")
	firewallAddCmd.Flags().Bool("enable", false, "Enable the rule")
	firewallAddCmd.Flags().Bool("disable", false, "Disable the rule")

	// firewall delete
	firewallDeleteCmd := &cobra.Command{
		Use:   "delete [VM_ID] [POSITION]",
		Short: "Delete a firewall rule",
		Args:  cobra.MaximumNArgs(2),
		Run:   firewallDeleteRun,
	}

	// firewall options
	firewallOptionsCmd := &cobra.Command{
		Use:   "options [VM_ID]",
		Short: "Set firewall options for a VM",
		Args:  cobra.MaximumNArgs(1),
		Run:   firewallOptionsRun,
	}
	firewallOptionsCmd.Flags().Bool("enable", false, "Enable firewall")
	firewallOptionsCmd.Flags().Bool("disable", false, "Disable firewall")
	firewallOptionsCmd.Flags().String("policy-in", "", "Input policy (ACCEPT, DROP, REJECT)")
	firewallOptionsCmd.Flags().String("policy-out", "", "Output policy (ACCEPT, DROP, REJECT)")

	FirewallCmd.AddCommand(firewallListCmd)
	FirewallCmd.AddCommand(firewallAddCmd)
	FirewallCmd.AddCommand(firewallDeleteCmd)
	FirewallCmd.AddCommand(firewallOptionsCmd)
}

func firewallListRun(cmd *cobra.Command, args []string) {
	vmID := ""
	if len(args) > 0 {
		vmID = args[0]
	} else {
		vmID = SelectVM("Select a VM:")
	}

	path := fmt.Sprintf("/vms/%s/firewall", vmID)
	result := client.Get(path, nil, true)

	data, ok := result["data"].([]interface{})
	if !ok {
		fmt.Fprintln(os.Stderr, "No firewall rules found.")
		return
	}

	var rows [][]string
	for i, item := range data {
		rule, ok := item.(map[string]interface{})
		if !ok {
			continue
		}
		rows = append(rows, []string{
			strconv.Itoa(i + 1),
			fmt.Sprintf("%v", rule["type"]),
			fmt.Sprintf("%v", rule["action"]),
			fmt.Sprintf("%v", rule["proto"]),
			fmt.Sprintf("%v", rule["dport"]),
			fmt.Sprintf("%v", rule["source"]),
			fmt.Sprintf("%v", rule["enable"]),
			fmt.Sprintf("%v", rule["comment"]),
		})
	}

	output.PrintTable(rows, []string{"#", "Type", "Action", "Proto", "DPort", "Source", "Enabled", "Comment"})
}

func firewallAddRun(cmd *cobra.Command, args []string) {
	vmID := ""
	if len(args) > 0 {
		vmID = args[0]
	} else {
		vmID = SelectVM("Select a VM:")
	}

	ruleType, _ := cmd.Flags().GetString("type")
	action, _ := cmd.Flags().GetString("action")
	proto, _ := cmd.Flags().GetString("proto")
	dport, _ := cmd.Flags().GetString("dport")
	sport, _ := cmd.Flags().GetString("sport")
	source, _ := cmd.Flags().GetString("source")
	dest, _ := cmd.Flags().GetString("dest")
	comment, _ := cmd.Flags().GetString("comment")
	enableFlag, _ := cmd.Flags().GetBool("enable")
	disableFlag, _ := cmd.Flags().GetBool("disable")

	// Interactive prompts for required fields if missing.
	if ruleType == "" {
		var selected string
		prompt := &survey.Select{
			Message: "Select rule type:",
			Options: []string{"in", "out"},
		}
		if err := survey.AskOne(prompt, &selected); err != nil {
			fmt.Fprintf(os.Stderr, "Prompt cancelled: %v\n", err)
			os.Exit(1)
		}
		ruleType = selected
	}

	if action == "" {
		var selected string
		prompt := &survey.Select{
			Message: "Select action:",
			Options: []string{"ACCEPT", "DROP", "REJECT"},
		}
		if err := survey.AskOne(prompt, &selected); err != nil {
			fmt.Fprintf(os.Stderr, "Prompt cancelled: %v\n", err)
			os.Exit(1)
		}
		action = selected
	}

	body := map[string]interface{}{
		"type":   ruleType,
		"action": action,
	}
	if proto != "" {
		body["proto"] = proto
	}
	if dport != "" {
		body["dport"] = dport
	}
	if sport != "" {
		body["sport"] = sport
	}
	if source != "" {
		body["source"] = source
	}
	if dest != "" {
		body["dest"] = dest
	}
	if comment != "" {
		body["comment"] = comment
	}
	if enableFlag {
		body["enable"] = true
	} else if disableFlag {
		body["enable"] = false
	} else {
		body["enable"] = true
	}

	path := fmt.Sprintf("/vms/%s/firewall", vmID)
	client.Post(path, body, true, 0)

	output.PrintSuccess("Firewall rule added successfully.")
}

func firewallDeleteRun(cmd *cobra.Command, args []string) {
	vmID := ""
	position := ""

	switch len(args) {
	case 2:
		vmID = args[0]
		position = args[1]
	case 1:
		vmID = args[0]
		position = PromptText("Enter rule position to delete:")
	default:
		vmID = SelectVM("Select a VM:")
		position = PromptText("Enter rule position to delete:")
	}

	if !Confirm(fmt.Sprintf("Delete firewall rule at position %s?", position)) {
		output.PrintInfo("Cancelled.")
		return
	}

	path := fmt.Sprintf("/vms/%s/firewall/%s", vmID, position)
	client.Delete(path, true)

	output.PrintSuccess("Firewall rule deleted successfully.")
}

func firewallOptionsRun(cmd *cobra.Command, args []string) {
	vmID := ""
	if len(args) > 0 {
		vmID = args[0]
	} else {
		vmID = SelectVM("Select a VM:")
	}

	enableFlag, _ := cmd.Flags().GetBool("enable")
	disableFlag, _ := cmd.Flags().GetBool("disable")
	policyIn, _ := cmd.Flags().GetString("policy-in")
	policyOut, _ := cmd.Flags().GetString("policy-out")

	body := map[string]interface{}{}

	if enableFlag {
		body["enable"] = true
	} else if disableFlag {
		body["enable"] = false
	}
	if policyIn != "" {
		body["policy_in"] = policyIn
	}
	if policyOut != "" {
		body["policy_out"] = policyOut
	}

	if len(body) == 0 {
		fmt.Fprintln(os.Stderr, "No options specified. Use --enable/--disable, --policy-in, or --policy-out.")
		os.Exit(1)
	}

	path := fmt.Sprintf("/vms/%s/firewall/options", vmID)
	client.Put(path, body, true)

	output.PrintSuccess("Firewall options updated successfully.")
}
