package cmd

import (
	"fmt"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var apiKeyListCmd = &cobra.Command{
	Use:   "list",
	Short: "List all API keys",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/api-keys", nil, true)
		keys := extractList(result, "api_keys", "apiKeys")

		var rows [][]string
		for _, k := range keys {
			rows = append(rows, []string{
				getString(k, "id"),
				getString(k, "name"),
				getString(k, "prefix"),
				getString(k, "created"),
			})
		}

		output.PrintTable(rows, []string{"ID", "Name", "Prefix", "Created"})
	},
}

var apiKeyCreateCmd = &cobra.Command{
	Use:   "create",
	Short: "Create a new API key",
	Run: func(cmd *cobra.Command, args []string) {
		name, _ := cmd.Flags().GetString("name")
		if name == "" {
			name = PromptText("API key name:")
		}

		body := map[string]interface{}{
			"name": name,
		}

		result := client.Post("/api-keys", body, true, 0)
		obj := extractObj(result)

		output.PrintSuccess("API key created. Save this key -- it will only be shown once!")
		fmt.Println()

		key := getString(obj, "key")
		if key == "" {
			key = getString(obj, "apiKey")
		}
		if key == "" {
			key = getString(obj, "token")
		}
		if key != "" {
			fmt.Printf("  Key: %s\n\n", key)
		}

		output.PrintItem(obj)
	},
}

var apiKeyRevokeCmd = &cobra.Command{
	Use:   "revoke [KEY_ID]",
	Short: "Revoke an API key",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		keyID := args[0]

		if !Confirm(fmt.Sprintf("Are you sure you want to revoke API key %s?", keyID)) {
			output.PrintInfo("Cancelled.")
			return
		}

		client.Delete(fmt.Sprintf("/api-keys/%s", keyID), true)
		output.PrintSuccess("API key revoked.")
	},
}

func init() {
	apiKeyCreateCmd.Flags().String("name", "", "Name for the API key")

	APIKeyCmd.AddCommand(apiKeyListCmd)
	APIKeyCmd.AddCommand(apiKeyCreateCmd)
	APIKeyCmd.AddCommand(apiKeyRevokeCmd)
}
