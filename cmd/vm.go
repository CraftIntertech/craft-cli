package cmd

import (
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

func init() {
	// vm list
	vmListCmd.Flags().Int("page", 1, "Page number")
	vmListCmd.Flags().Int("limit", 20, "Items per page")
	VMCmd.AddCommand(vmListCmd)

	// vm get
	VMCmd.AddCommand(vmGetCmd)

	// vm create
	vmCreateCmd.Flags().BoolP("interactive", "i", false, "Interactive wizard mode")
	vmCreateCmd.Flags().String("name", "", "VM name")
	vmCreateCmd.Flags().String("hostname", "", "VM hostname")
	vmCreateCmd.Flags().String("node-id", "", "Node ID")
	vmCreateCmd.Flags().String("os-template-id", "", "OS template ID")
	vmCreateCmd.Flags().String("root-password", "", "Root password")
	vmCreateCmd.Flags().String("plan-id", "", "Plan ID")
	vmCreateCmd.Flags().String("billing-type", "", "Billing type (daily/weekly/monthly/yearly)")
	vmCreateCmd.Flags().Int("cpu", 0, "Number of CPUs")
	vmCreateCmd.Flags().Int("ram-mb", 0, "RAM in MB")
	vmCreateCmd.Flags().Int("disk-gb", 0, "Disk size in GB")
	vmCreateCmd.Flags().String("ssh-keys", "", "Comma-separated SSH key IDs")
	VMCmd.AddCommand(vmCreateCmd)

	// vm delete
	VMCmd.AddCommand(vmDeleteCmd)

	// vm status
	VMCmd.AddCommand(vmStatusCmd)

	// vm start
	VMCmd.AddCommand(vmStartCmd)

	// vm stop
	VMCmd.AddCommand(vmStopCmd)

	// vm reboot
	VMCmd.AddCommand(vmRebootCmd)

	// vm rename
	vmRenameCmd.Flags().String("name", "", "New VM name")
	VMCmd.AddCommand(vmRenameCmd)

	// vm reset-password
	vmResetPasswordCmd.Flags().String("username", "", "Username")
	vmResetPasswordCmd.Flags().String("new-password", "", "New password")
	VMCmd.AddCommand(vmResetPasswordCmd)

	// vm reset-network
	VMCmd.AddCommand(vmResetNetworkCmd)

	// vm resize
	vmResizeCmd.Flags().String("plan-id", "", "New plan ID")
	VMCmd.AddCommand(vmResizeCmd)

	// vm reinstall
	vmReinstallCmd.Flags().String("os-template-id", "", "OS template ID")
	vmReinstallCmd.Flags().String("root-password", "", "Root password")
	vmReinstallCmd.Flags().String("ssh-keys", "", "Comma-separated SSH key IDs")
	VMCmd.AddCommand(vmReinstallCmd)

	// vm console
	VMCmd.AddCommand(vmConsoleCmd)

	// vm network
	VMCmd.AddCommand(vmNetworkCmd)

	// vm metrics
	vmMetricsCmd.Flags().Int("hours", 24, "Number of hours of metrics to retrieve")
	VMCmd.AddCommand(vmMetricsCmd)
}

// resolveVMID returns the VM ID from args or prompts the user to select one.
func resolveVMID(args []string) string {
	if len(args) > 0 && args[0] != "" {
		return args[0]
	}
	return SelectVM("Select a VM")
}

// ---------- vm list ----------

var vmListCmd = &cobra.Command{
	Use:   "list",
	Short: "List all virtual machines",
	Run: func(cmd *cobra.Command, args []string) {
		page, _ := cmd.Flags().GetInt("page")
		limit, _ := cmd.Flags().GetInt("limit")

		params := map[string]string{
			"page":  strconv.Itoa(page),
			"limit": strconv.Itoa(limit),
		}

		result := client.Get("/vms", params, true)
		vms := extractList(result, "vms", "items")

		headers := []string{"ID", "Name", "Status", "IP", "OS"}
		rows := make([][]string, len(vms))
		for i, vm := range vms {
			ip := getString(vm, "ip")
			if ip == "" {
				ip = getString(vm, "ipAddress")
			}
			osName := getString(vm, "os")
			if osName == "" {
				osName = getString(vm, "os_template")
			}
			rows[i] = []string{
				getString(vm, "id"),
				getString(vm, "name"),
				getString(vm, "status"),
				ip,
				osName,
			}
		}

		output.PrintTable(rows, headers)

		// Show pagination info if available.
		output.PrintPageInfo(result, page, limit)
	},
}

// ---------- vm get ----------

var vmGetCmd = &cobra.Command{
	Use:   "get [VM_ID]",
	Short: "Get details of a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)
		path := fmt.Sprintf("/vms/%s", vmID)
		result := client.Get(path, nil, true)
		output.PrintItem(extractObj(result))
	},
}

// ---------- vm create ----------

var vmCreateCmd = &cobra.Command{
	Use:   "create",
	Short: "Create a new virtual machine",
	Run: func(cmd *cobra.Command, args []string) {
		interactive, _ := cmd.Flags().GetBool("interactive")

		body := map[string]interface{}{}

		if interactive {
			body["name"] = PromptText("VM name:")
			body["hostname"] = PromptText("Hostname:")
			nodeID := SelectNode("Select node")
			body["node_id"] = nodeID
			body["os_template_id"] = SelectOSTemplate("Select OS template")
			body["plan_id"] = SelectPlan(nodeID, "Select plan")
			body["billing_type"] = SelectBillingType("Select billing type")
			sshKeys := SelectSSHKeys()
			if sshKeys != "" {
				body["ssh_keys"] = sshKeys
			}
			body["root_password"] = PromptPassword("Root password:")
		} else {
			name, _ := cmd.Flags().GetString("name")
			hostname, _ := cmd.Flags().GetString("hostname")
			nodeID, _ := cmd.Flags().GetString("node-id")
			osTemplateID, _ := cmd.Flags().GetString("os-template-id")
			rootPassword, _ := cmd.Flags().GetString("root-password")
			planID, _ := cmd.Flags().GetString("plan-id")
			billingType, _ := cmd.Flags().GetString("billing-type")
			cpu, _ := cmd.Flags().GetInt("cpu")
			ramMB, _ := cmd.Flags().GetInt("ram-mb")
			diskGB, _ := cmd.Flags().GetInt("disk-gb")
			sshKeys, _ := cmd.Flags().GetString("ssh-keys")

			if name == "" {
				fmt.Fprintln(os.Stderr, "Error: --name is required (or use -i for interactive mode)")
				os.Exit(1)
			}

			body["name"] = name
			if hostname != "" {
				body["hostname"] = hostname
			}
			if nodeID != "" {
				body["node_id"] = nodeID
			}
			if osTemplateID != "" {
				body["os_template_id"] = osTemplateID
			}
			if rootPassword != "" {
				body["root_password"] = rootPassword
			}
			if planID != "" {
				body["plan_id"] = planID
			}
			if billingType != "" {
				body["billing_type"] = billingType
			}
			if cpu > 0 {
				body["cpu"] = cpu
			}
			if ramMB > 0 {
				body["ram_mb"] = ramMB
			}
			if diskGB > 0 {
				body["disk_gb"] = diskGB
			}
			if sshKeys != "" {
				body["ssh_keys"] = sshKeys
			}
		}

		result := client.Post("/vms", body, true, 120)
		output.PrintSuccess("VM creation initiated.")
		output.PrintItem(extractObj(result))
	},
}

// ---------- vm delete ----------

var vmDeleteCmd = &cobra.Command{
	Use:   "delete [VM_ID]",
	Short: "Delete a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)

		if !Confirm(fmt.Sprintf("Are you sure you want to delete VM %s?", vmID)) {
			fmt.Println("Aborted.")
			return
		}

		path := fmt.Sprintf("/vms/%s", vmID)
		client.Delete(path, true)
		output.PrintSuccess(fmt.Sprintf("VM %s deleted.", vmID))
	},
}

// ---------- vm status ----------

var vmStatusCmd = &cobra.Command{
	Use:   "status [VM_ID]",
	Short: "Get status of a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)
		path := fmt.Sprintf("/vms/%s/status", vmID)
		result := client.Get(path, nil, true)
		output.PrintItem(extractObj(result))
	},
}

// ---------- vm start ----------

var vmStartCmd = &cobra.Command{
	Use:   "start [VM_ID]",
	Short: "Start a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)
		path := fmt.Sprintf("/vms/%s/start", vmID)
		client.Post(path, nil, true, 120)
		output.PrintSuccess(fmt.Sprintf("VM %s start initiated.", vmID))
	},
}

// ---------- vm stop ----------

var vmStopCmd = &cobra.Command{
	Use:   "stop [VM_ID]",
	Short: "Stop a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)
		path := fmt.Sprintf("/vms/%s/stop", vmID)
		client.Post(path, nil, true, 120)
		output.PrintSuccess(fmt.Sprintf("VM %s stop initiated.", vmID))
	},
}

// ---------- vm reboot ----------

var vmRebootCmd = &cobra.Command{
	Use:   "reboot [VM_ID]",
	Short: "Reboot a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)
		path := fmt.Sprintf("/vms/%s/reboot", vmID)
		client.Post(path, nil, true, 120)
		output.PrintSuccess(fmt.Sprintf("VM %s reboot initiated.", vmID))
	},
}

// ---------- vm rename ----------

var vmRenameCmd = &cobra.Command{
	Use:   "rename [VM_ID]",
	Short: "Rename a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)

		name, _ := cmd.Flags().GetString("name")
		if name == "" {
			name = PromptText("New VM name:")
		}

		path := fmt.Sprintf("/vms/%s/rename", vmID)
		body := map[string]interface{}{
			"name": name,
		}
		client.Patch(path, body, true)
		output.PrintSuccess(fmt.Sprintf("VM %s renamed to %s.", vmID, name))
	},
}

// ---------- vm reset-password ----------

var vmResetPasswordCmd = &cobra.Command{
	Use:   "reset-password [VM_ID]",
	Short: "Reset password for a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)

		username, _ := cmd.Flags().GetString("username")
		newPassword, _ := cmd.Flags().GetString("new-password")

		if username == "" {
			username = PromptText("Username:")
		}
		if newPassword == "" {
			newPassword = PromptPassword("New password:")
		}

		path := fmt.Sprintf("/vms/%s/reset-password", vmID)
		body := map[string]interface{}{
			"username":     username,
			"new_password": newPassword,
		}
		client.Post(path, body, true, 0)
		output.PrintSuccess(fmt.Sprintf("Password reset for user %s on VM %s.", username, vmID))
	},
}

// ---------- vm reset-network ----------

var vmResetNetworkCmd = &cobra.Command{
	Use:   "reset-network [VM_ID]",
	Short: "Reset network configuration for a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)
		path := fmt.Sprintf("/vms/%s/reset-network", vmID)
		client.Post(path, nil, true, 0)
		output.PrintSuccess(fmt.Sprintf("Network reset initiated for VM %s.", vmID))
	},
}

// ---------- vm resize ----------

var vmResizeCmd = &cobra.Command{
	Use:   "resize [VM_ID]",
	Short: "Resize a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)

		planID, _ := cmd.Flags().GetString("plan-id")
		if planID == "" {
			planID = SelectPlan("", "Select new plan")
		}

		path := fmt.Sprintf("/vms/%s/resize", vmID)
		body := map[string]interface{}{
			"plan_id": planID,
		}
		client.Post(path, body, true, 0)
		output.PrintSuccess(fmt.Sprintf("VM %s resize initiated with plan %s.", vmID, planID))
	},
}

// ---------- vm reinstall ----------

var vmReinstallCmd = &cobra.Command{
	Use:   "reinstall [VM_ID]",
	Short: "Reinstall a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)

		if !Confirm(fmt.Sprintf("Are you sure you want to reinstall VM %s? This will destroy all data.", vmID)) {
			fmt.Println("Aborted.")
			return
		}

		osTemplateID, _ := cmd.Flags().GetString("os-template-id")
		rootPassword, _ := cmd.Flags().GetString("root-password")
		sshKeys, _ := cmd.Flags().GetString("ssh-keys")

		if osTemplateID == "" {
			osTemplateID = SelectOSTemplate("Select OS template")
		}
		if rootPassword == "" {
			rootPassword = PromptPassword("Root password:")
		}

		body := map[string]interface{}{
			"os_template_id": osTemplateID,
			"root_password":  rootPassword,
		}
		if sshKeys != "" {
			body["ssh_keys"] = sshKeys
		}

		path := fmt.Sprintf("/vms/%s/reinstall", vmID)
		client.Post(path, body, true, 0)
		output.PrintSuccess(fmt.Sprintf("VM %s reinstall initiated.", vmID))
	},
}

// ---------- vm console ----------

var vmConsoleCmd = &cobra.Command{
	Use:   "console [VM_ID]",
	Short: "Get console access URL for a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)
		path := fmt.Sprintf("/vms/%s/console", vmID)
		result := client.Get(path, nil, true)
		obj := extractObj(result)

		// Try to display the console URL prominently.
		url := getString(obj, "url")
		if url == "" {
			url = getString(obj, "console_url")
		}
		if url != "" {
			output.PrintInfo(fmt.Sprintf("Console URL: %s", url))
		}
		output.PrintItem(obj)
	},
}

// ---------- vm network ----------

var vmNetworkCmd = &cobra.Command{
	Use:   "network [VM_ID]",
	Short: "Get network information for a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)
		path := fmt.Sprintf("/vms/%s/network", vmID)
		result := client.Get(path, nil, true)
		output.PrintItem(extractObj(result))
	},
}

// ---------- vm metrics ----------

var vmMetricsCmd = &cobra.Command{
	Use:   "metrics [VM_ID]",
	Short: "Get metrics for a virtual machine",
	Args:  cobra.MaximumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		vmID := resolveVMID(args)
		hours, _ := cmd.Flags().GetInt("hours")

		path := fmt.Sprintf("/vms/%s/metrics", vmID)
		params := map[string]string{
			"hours": strconv.Itoa(hours),
		}
		result := client.Get(path, params, true)
		obj := extractObj(result)

		// Format metrics output if structured data is available.
		formatted := false
		for _, key := range []string{"cpu", "memory", "disk", "network", "bandwidth"} {
			if val, ok := obj[key]; ok {
				fmt.Printf("\n%s:\n", strings.ToUpper(key))
				if m, ok := val.(map[string]interface{}); ok {
					for k, v := range m {
						fmt.Printf("  %-20s %v\n", k+":", v)
					}
					formatted = true
				} else {
					fmt.Printf("  %v\n", val)
					formatted = true
				}
			}
		}

		if !formatted {
			output.PrintItem(obj)
		}
	},
}
