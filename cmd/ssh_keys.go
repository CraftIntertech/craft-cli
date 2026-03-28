package cmd

import (
	"fmt"
	"os"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var sshKeyListCmd = &cobra.Command{
	Use:   "list",
	Short: "List all SSH keys",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/ssh-keys", nil, true)
		keys := extractList(result, "ssh_keys", "sshKeys")

		var rows [][]string
		for _, k := range keys {
			rows = append(rows, []string{
				getString(k, "id"),
				getString(k, "name"),
				getString(k, "fingerprint"),
			})
		}

		output.PrintTable(rows, []string{"ID", "Name", "Fingerprint"})
	},
}

var sshKeyAddCmd = &cobra.Command{
	Use:   "add",
	Short: "Add a new SSH key",
	Run: func(cmd *cobra.Command, args []string) {
		name, _ := cmd.Flags().GetString("name")
		publicKey, _ := cmd.Flags().GetString("public-key")

		if name == "" {
			name = PromptText("SSH key name:")
		}
		if publicKey == "" {
			publicKey = PromptText("Public key:")
		}

		body := map[string]interface{}{
			"name":      name,
			"publicKey": publicKey,
		}

		result := client.Post("/ssh-keys", body, true, 0)
		output.PrintSuccess("SSH key added.")
		output.PrintItem(extractObj(result))
	},
}

var sshKeyAddFileCmd = &cobra.Command{
	Use:   "add-file",
	Short: "Add a new SSH key from a file",
	Run: func(cmd *cobra.Command, args []string) {
		name, _ := cmd.Flags().GetString("name")
		filePath, _ := cmd.Flags().GetString("file")

		if name == "" {
			name = PromptText("SSH key name:")
		}
		if filePath == "" {
			filePath = PromptText("Path to public key file:")
		}

		data, err := os.ReadFile(filePath)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error reading file: %v\n", err)
			os.Exit(1)
		}

		body := map[string]interface{}{
			"name":      name,
			"publicKey": string(data),
		}

		result := client.Post("/ssh-keys", body, true, 0)
		output.PrintSuccess("SSH key added from file.")
		output.PrintItem(extractObj(result))
	},
}

var sshKeyDeleteCmd = &cobra.Command{
	Use:   "delete [KEY_ID]",
	Short: "Delete an SSH key",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		keyID := args[0]

		if !Confirm(fmt.Sprintf("Are you sure you want to delete SSH key %s?", keyID)) {
			output.PrintInfo("Cancelled.")
			return
		}

		client.Delete(fmt.Sprintf("/ssh-keys/%s", keyID), true)
		output.PrintSuccess("SSH key deleted.")
	},
}

func init() {
	sshKeyAddCmd.Flags().String("name", "", "Name for the SSH key")
	sshKeyAddCmd.Flags().String("public-key", "", "Public key content")

	sshKeyAddFileCmd.Flags().String("name", "", "Name for the SSH key")
	sshKeyAddFileCmd.Flags().String("file", "", "Path to public key file")

	SSHKeyCmd.AddCommand(sshKeyListCmd)
	SSHKeyCmd.AddCommand(sshKeyAddCmd)
	SSHKeyCmd.AddCommand(sshKeyAddFileCmd)
	SSHKeyCmd.AddCommand(sshKeyDeleteCmd)
}
