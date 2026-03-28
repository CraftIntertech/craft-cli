package cmd

import (
	"fmt"
	"os"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

func init() {
	// snapshot list
	snapshotListCmd := &cobra.Command{
		Use:   "list [VM_ID]",
		Short: "List snapshots for a VM",
		Args:  cobra.MaximumNArgs(1),
		Run:   snapshotListRun,
	}

	// snapshot create
	snapshotCreateCmd := &cobra.Command{
		Use:   "create [VM_ID]",
		Short: "Create a snapshot for a VM",
		Args:  cobra.MaximumNArgs(1),
		Run:   snapshotCreateRun,
	}
	snapshotCreateCmd.Flags().String("description", "", "Snapshot description")

	// snapshot delete
	snapshotDeleteCmd := &cobra.Command{
		Use:   "delete [VM_ID] [SNAP_ID]",
		Short: "Delete a snapshot",
		Args:  cobra.MaximumNArgs(2),
		Run:   snapshotDeleteRun,
	}

	// snapshot rollback
	snapshotRollbackCmd := &cobra.Command{
		Use:   "rollback [VM_ID] [SNAP_ID]",
		Short: "Rollback a VM to a snapshot",
		Args:  cobra.MaximumNArgs(2),
		Run:   snapshotRollbackRun,
	}

	// snapshot sync
	snapshotSyncCmd := &cobra.Command{
		Use:   "sync [VM_ID]",
		Short: "Sync snapshots for a VM",
		Args:  cobra.MaximumNArgs(1),
		Run:   snapshotSyncRun,
	}

	SnapshotCmd.AddCommand(snapshotListCmd)
	SnapshotCmd.AddCommand(snapshotCreateCmd)
	SnapshotCmd.AddCommand(snapshotDeleteCmd)
	SnapshotCmd.AddCommand(snapshotRollbackCmd)
	SnapshotCmd.AddCommand(snapshotSyncCmd)
}

func snapshotListRun(cmd *cobra.Command, args []string) {
	vmID := ""
	if len(args) > 0 {
		vmID = args[0]
	} else {
		vmID = SelectVM("Select a VM:")
	}

	path := fmt.Sprintf("/vms/%s/snapshots", vmID)
	result := client.Get(path, nil, true)

	data, ok := result["data"].([]interface{})
	if !ok {
		fmt.Fprintln(os.Stderr, "No snapshots found.")
		return
	}

	var rows [][]string
	for _, item := range data {
		snap, ok := item.(map[string]interface{})
		if !ok {
			continue
		}
		rows = append(rows, []string{
			fmt.Sprintf("%v", snap["id"]),
			fmt.Sprintf("%v", snap["description"]),
			fmt.Sprintf("%v", snap["created"]),
		})
	}

	output.PrintTable(rows, []string{"ID", "Description", "Created"})
}

func snapshotCreateRun(cmd *cobra.Command, args []string) {
	vmID := ""
	if len(args) > 0 {
		vmID = args[0]
	} else {
		vmID = SelectVM("Select a VM:")
	}

	description, _ := cmd.Flags().GetString("description")

	body := map[string]interface{}{}
	if description != "" {
		body["description"] = description
	}

	path := fmt.Sprintf("/vms/%s/snapshots", vmID)
	client.Post(path, body, true, 0)

	output.PrintSuccess("Snapshot created successfully.")
}

func snapshotDeleteRun(cmd *cobra.Command, args []string) {
	vmID := ""
	snapID := ""

	switch len(args) {
	case 2:
		vmID = args[0]
		snapID = args[1]
	case 1:
		vmID = args[0]
		snapID = PromptText("Enter snapshot ID to delete:")
	default:
		vmID = SelectVM("Select a VM:")
		snapID = PromptText("Enter snapshot ID to delete:")
	}

	if !Confirm(fmt.Sprintf("Delete snapshot %s?", snapID)) {
		output.PrintInfo("Cancelled.")
		return
	}

	path := fmt.Sprintf("/vms/%s/snapshots/%s", vmID, snapID)
	client.Delete(path, true)

	output.PrintSuccess("Snapshot deleted successfully.")
}

func snapshotRollbackRun(cmd *cobra.Command, args []string) {
	vmID := ""
	snapID := ""

	switch len(args) {
	case 2:
		vmID = args[0]
		snapID = args[1]
	case 1:
		vmID = args[0]
		snapID = PromptText("Enter snapshot ID to rollback to:")
	default:
		vmID = SelectVM("Select a VM:")
		snapID = PromptText("Enter snapshot ID to rollback to:")
	}

	if !Confirm(fmt.Sprintf("Rollback VM %s to snapshot %s? This may cause data loss.", vmID, snapID)) {
		output.PrintInfo("Cancelled.")
		return
	}

	path := fmt.Sprintf("/vms/%s/snapshots/%s/rollback", vmID, snapID)
	client.Post(path, nil, true, 0)

	output.PrintSuccess("Snapshot rollback initiated successfully.")
}

func snapshotSyncRun(cmd *cobra.Command, args []string) {
	vmID := ""
	if len(args) > 0 {
		vmID = args[0]
	} else {
		vmID = SelectVM("Select a VM:")
	}

	path := fmt.Sprintf("/vms/%s/snapshots/sync", vmID)
	client.Post(path, nil, true, 0)

	output.PrintSuccess("Snapshot sync initiated successfully.")
}
