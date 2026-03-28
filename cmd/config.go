package cmd

import (
	"fmt"

	"github.com/CraftIntertech/craft-cli/internal/config"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var configCmd = &cobra.Command{
	Use:   "config",
	Short: "View or update CLI configuration",
	Run: func(cmd *cobra.Command, args []string) {
		show, _ := cmd.Flags().GetBool("show")
		baseURL, _ := cmd.Flags().GetString("base-url")
		token, _ := cmd.Flags().GetString("token")

		cfg := config.LoadConfig()
		changed := false

		if baseURL != "" {
			cfg.BaseURL = baseURL
			changed = true
		}

		if token != "" {
			cfg.AccessToken = token
			changed = true
		}

		if changed {
			config.SaveConfig(cfg)
			output.PrintSuccess("Configuration updated.")
		}

		if show || !changed {
			fmt.Printf("Base URL : %s\n", cfg.BaseURL)
			masked := "(not set)"
			if cfg.AccessToken != "" {
				masked = maskToken(cfg.AccessToken)
			}
			fmt.Printf("Token    : %s\n", masked)
		}
	},
}

func init() {
	configCmd.Flags().Bool("show", false, "Display current configuration")
	configCmd.Flags().String("base-url", "", "Set the API base URL")
	configCmd.Flags().String("token", "", "Set the access token")
	rootCmd.AddCommand(configCmd)
}
