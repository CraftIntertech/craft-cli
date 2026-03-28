package cmd

import (
	"fmt"
	"os"
	"strconv"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

func init() {
	// hosting plans
	hostingPlansCmd := &cobra.Command{
		Use:   "plans",
		Short: "List available hosting plans",
		Run:   hostingPlansRun,
	}

	// hosting nodes
	hostingNodesCmd := &cobra.Command{
		Use:   "nodes",
		Short: "List available hosting nodes",
		Run:   hostingNodesRun,
	}

	// hosting list
	hostingListCmd := &cobra.Command{
		Use:   "list",
		Short: "List hosting accounts",
		Run:   hostingListRun,
	}
	hostingListCmd.Flags().Int("page", 1, "Page number")
	hostingListCmd.Flags().Int("limit", 20, "Items per page")

	// hosting get
	hostingGetCmd := &cobra.Command{
		Use:   "get [HOSTING_ID]",
		Short: "Get hosting account details",
		Args:  cobra.MaximumNArgs(1),
		Run:   hostingGetRun,
	}

	// hosting create
	hostingCreateCmd := &cobra.Command{
		Use:   "create",
		Short: "Create a new hosting account",
		Run:   hostingCreateRun,
	}
	hostingCreateCmd.Flags().BoolP("interactive", "i", false, "Interactive mode")
	hostingCreateCmd.Flags().String("name", "", "Hosting name")
	hostingCreateCmd.Flags().String("domain", "", "Domain name")
	hostingCreateCmd.Flags().String("node-id", "", "Node ID")
	hostingCreateCmd.Flags().String("plan-id", "", "Plan ID")
	hostingCreateCmd.Flags().String("billing-type", "", "Billing type")

	// hosting delete
	hostingDeleteCmd := &cobra.Command{
		Use:   "delete [HOSTING_ID]",
		Short: "Delete a hosting account",
		Args:  cobra.MaximumNArgs(1),
		Run:   hostingDeleteRun,
	}

	// hosting login-url
	hostingLoginURLCmd := &cobra.Command{
		Use:   "login-url [HOSTING_ID]",
		Short: "Get the login URL for a hosting account",
		Args:  cobra.MaximumNArgs(1),
		Run:   hostingLoginURLRun,
	}

	// hosting billing
	hostingBillingCmd := &cobra.Command{
		Use:   "billing [HOSTING_ID]",
		Short: "Get billing info for a hosting account",
		Args:  cobra.MaximumNArgs(1),
		Run:   hostingBillingRun,
	}

	// hosting renew
	hostingRenewCmd := &cobra.Command{
		Use:   "renew [HOSTING_ID]",
		Short: "Renew a hosting account",
		Args:  cobra.MaximumNArgs(1),
		Run:   hostingRenewRun,
	}
	hostingRenewCmd.Flags().String("billing-type", "", "Billing type for renewal")

	// hosting auto-renew
	hostingAutoRenewCmd := &cobra.Command{
		Use:   "auto-renew [HOSTING_ID]",
		Short: "Enable or disable auto-renew for a hosting account",
		Args:  cobra.MaximumNArgs(1),
		Run:   hostingAutoRenewRun,
	}
	hostingAutoRenewCmd.Flags().Bool("enable", false, "Enable auto-renew")
	hostingAutoRenewCmd.Flags().Bool("disable", false, "Disable auto-renew")

	HostingCmd.AddCommand(hostingPlansCmd)
	HostingCmd.AddCommand(hostingNodesCmd)
	HostingCmd.AddCommand(hostingListCmd)
	HostingCmd.AddCommand(hostingGetCmd)
	HostingCmd.AddCommand(hostingCreateCmd)
	HostingCmd.AddCommand(hostingDeleteCmd)
	HostingCmd.AddCommand(hostingLoginURLCmd)
	HostingCmd.AddCommand(hostingBillingCmd)
	HostingCmd.AddCommand(hostingRenewCmd)
	HostingCmd.AddCommand(hostingAutoRenewCmd)
}

func hostingPlansRun(cmd *cobra.Command, args []string) {
	result := client.Get("/hosting/plans", nil, true)

	data, ok := result["data"].([]interface{})
	if !ok {
		fmt.Fprintln(os.Stderr, "No hosting plans found.")
		return
	}

	var rows [][]string
	for _, item := range data {
		plan, ok := item.(map[string]interface{})
		if !ok {
			continue
		}
		rows = append(rows, []string{
			fmt.Sprintf("%v", plan["id"]),
			fmt.Sprintf("%v", plan["name"]),
			fmt.Sprintf("%v", plan["disk"]),
			fmt.Sprintf("%v", plan["bandwidth"]),
			fmt.Sprintf("%v", plan["monthly"]),
		})
	}

	output.PrintTable(rows, []string{"ID", "Name", "Disk", "Bandwidth", "Monthly"})
}

func hostingNodesRun(cmd *cobra.Command, args []string) {
	result := client.Get("/hosting/nodes", nil, true)

	data, ok := result["data"].([]interface{})
	if !ok {
		fmt.Fprintln(os.Stderr, "No hosting nodes found.")
		return
	}

	var rows [][]string
	for _, item := range data {
		node, ok := item.(map[string]interface{})
		if !ok {
			continue
		}
		rows = append(rows, []string{
			fmt.Sprintf("%v", node["id"]),
			fmt.Sprintf("%v", node["name"]),
			fmt.Sprintf("%v", node["location"]),
			fmt.Sprintf("%v", node["status"]),
		})
	}

	output.PrintTable(rows, []string{"ID", "Name", "Location", "Status"})
}

func hostingListRun(cmd *cobra.Command, args []string) {
	page, _ := cmd.Flags().GetInt("page")
	limit, _ := cmd.Flags().GetInt("limit")

	params := map[string]string{
		"page":  strconv.Itoa(page),
		"limit": strconv.Itoa(limit),
	}

	result := client.Get("/hosting", params, true)

	data, ok := result["data"].([]interface{})
	if !ok {
		fmt.Fprintln(os.Stderr, "No hosting accounts found.")
		return
	}

	var rows [][]string
	for _, item := range data {
		h, ok := item.(map[string]interface{})
		if !ok {
			continue
		}
		rows = append(rows, []string{
			fmt.Sprintf("%v", h["id"]),
			fmt.Sprintf("%v", h["name"]),
			fmt.Sprintf("%v", h["domain"]),
			fmt.Sprintf("%v", h["status"]),
		})
	}

	output.PrintTable(rows, []string{"ID", "Name", "Domain", "Status"})

	output.PrintPageInfo(result, page, limit)
}

func hostingGetRun(cmd *cobra.Command, args []string) {
	hostingID := ""
	if len(args) > 0 {
		hostingID = args[0]
	} else {
		hostingID = SelectHosting("Select a hosting account:")
	}

	path := fmt.Sprintf("/hosting/%s", hostingID)
	result := client.Get(path, nil, true)

	output.PrintItem(result)
}

func hostingCreateRun(cmd *cobra.Command, args []string) {
	interactive, _ := cmd.Flags().GetBool("interactive")

	name, _ := cmd.Flags().GetString("name")
	domain, _ := cmd.Flags().GetString("domain")
	nodeID, _ := cmd.Flags().GetString("node-id")
	planID, _ := cmd.Flags().GetString("plan-id")
	billingType, _ := cmd.Flags().GetString("billing-type")

	if interactive || (name == "" && domain == "" && nodeID == "" && planID == "") {
		if name == "" {
			name = PromptText("Enter hosting name:")
		}
		if domain == "" {
			domain = PromptText("Enter domain name:")
		}
		if nodeID == "" {
			nodeID = SelectNode("Select a node:")
		}
		if planID == "" {
			planID = SelectPlan(nodeID, "Select a hosting plan:")
		}
		if billingType == "" {
			billingType = SelectBillingType("Select billing type:")
		}
	}

	if name == "" || domain == "" || nodeID == "" || planID == "" {
		fmt.Fprintln(os.Stderr, "Missing required fields. Use -i for interactive mode or provide --name, --domain, --node-id, and --plan-id.")
		os.Exit(1)
	}

	body := map[string]interface{}{
		"name":    name,
		"domain":  domain,
		"node_id": nodeID,
		"plan_id": planID,
	}
	if billingType != "" {
		body["billing_type"] = billingType
	}

	result := client.Post("/hosting", body, true, 0)

	output.PrintSuccess("Hosting account created successfully.")
	output.PrintItem(result)
}

func hostingDeleteRun(cmd *cobra.Command, args []string) {
	hostingID := ""
	if len(args) > 0 {
		hostingID = args[0]
	} else {
		hostingID = SelectHosting("Select a hosting account to delete:")
	}

	if !Confirm(fmt.Sprintf("Delete hosting account %s?", hostingID)) {
		output.PrintInfo("Cancelled.")
		return
	}

	path := fmt.Sprintf("/hosting/%s", hostingID)
	client.Delete(path, true)

	output.PrintSuccess("Hosting account deleted successfully.")
}

func hostingLoginURLRun(cmd *cobra.Command, args []string) {
	hostingID := ""
	if len(args) > 0 {
		hostingID = args[0]
	} else {
		hostingID = SelectHosting("Select a hosting account:")
	}

	path := fmt.Sprintf("/hosting/%s/login-url", hostingID)
	result := client.Post(path, nil, true, 0)

	if url, ok := result["url"].(string); ok {
		fmt.Println(url)
	} else {
		output.PrintItem(result)
	}
}

func hostingBillingRun(cmd *cobra.Command, args []string) {
	hostingID := ""
	if len(args) > 0 {
		hostingID = args[0]
	} else {
		hostingID = SelectHosting("Select a hosting account:")
	}

	path := fmt.Sprintf("/hosting/%s/billing", hostingID)
	result := client.Get(path, nil, true)

	output.PrintItem(result)
}

func hostingRenewRun(cmd *cobra.Command, args []string) {
	hostingID := ""
	if len(args) > 0 {
		hostingID = args[0]
	} else {
		hostingID = SelectHosting("Select a hosting account to renew:")
	}

	billingType, _ := cmd.Flags().GetString("billing-type")

	body := map[string]interface{}{}
	if billingType != "" {
		body["billing_type"] = billingType
	}

	path := fmt.Sprintf("/hosting/%s/renew", hostingID)
	client.Post(path, body, true, 0)

	output.PrintSuccess("Hosting account renewed successfully.")
}

func hostingAutoRenewRun(cmd *cobra.Command, args []string) {
	hostingID := ""
	if len(args) > 0 {
		hostingID = args[0]
	} else {
		hostingID = SelectHosting("Select a hosting account:")
	}

	enableFlag, _ := cmd.Flags().GetBool("enable")
	disableFlag, _ := cmd.Flags().GetBool("disable")

	var autoRenew bool
	if enableFlag {
		autoRenew = true
	} else if disableFlag {
		autoRenew = false
	} else {
		fmt.Fprintln(os.Stderr, "Please specify --enable or --disable.")
		os.Exit(1)
	}

	body := map[string]interface{}{
		"auto_renew": autoRenew,
	}

	path := fmt.Sprintf("/hosting/%s/auto-renew", hostingID)
	client.Patch(path, body, true)

	if autoRenew {
		output.PrintSuccess("Auto-renew enabled.")
	} else {
		output.PrintSuccess("Auto-renew disabled.")
	}
}
