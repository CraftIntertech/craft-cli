package cmd

import (
	"fmt"
	"os"
	"strings"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/config"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

// maskToken returns a masked version of a token, showing only the first 4
// and last 4 characters.
func maskToken(token string) string {
	if len(token) <= 8 {
		return strings.Repeat("*", len(token))
	}
	return token[:4] + strings.Repeat("*", len(token)-8) + token[len(token)-4:]
}

var loginCmd = &cobra.Command{
	Use:   "login <token>",
	Short: "Save an access token to the CLI config",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		token := args[0]
		cfg := config.LoadConfig()
		cfg.AccessToken = token
		config.SaveConfig(cfg)
		output.PrintSuccess(fmt.Sprintf("Token saved: %s", maskToken(token)))
	},
}

var logoutCmd = &cobra.Command{
	Use:   "logout",
	Short: "Log out and clear saved tokens",
	Run: func(cmd *cobra.Command, args []string) {
		cfg := config.LoadConfig()

		// Attempt to invalidate the refresh token on the server; ignore errors.
		if cfg.RefreshToken != "" {
			body := map[string]interface{}{
				"refreshToken": cfg.RefreshToken,
			}
			_, _ = client.APIRequest("POST", "/auth/logout", body, nil, true, 0)
		}

		config.ClearTokens()
		output.PrintSuccess("Logged out. Tokens cleared.")
	},
}

var refreshTokenCmd = &cobra.Command{
	Use:   "refresh-token",
	Short: "Refresh the access token using the stored refresh token",
	Run: func(cmd *cobra.Command, args []string) {
		cfg := config.LoadConfig()
		if cfg.RefreshToken == "" {
			fmt.Fprintln(os.Stderr, "Error: no refresh token found. Please log in first.")
			os.Exit(1)
		}

		body := map[string]interface{}{
			"refreshToken": cfg.RefreshToken,
		}

		result, err := client.APIRequest("POST", "/auth/refresh", body, nil, false, 0)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error: %v\n", err)
			os.Exit(1)
		}

		accessToken, _ := result["accessToken"].(string)
		refreshToken, _ := result["refreshToken"].(string)
		if accessToken == "" {
			// Try nested "data" envelope.
			if data, ok := result["data"].(map[string]interface{}); ok {
				accessToken, _ = data["accessToken"].(string)
				refreshToken, _ = data["refreshToken"].(string)
			}
		}

		if accessToken == "" {
			fmt.Fprintln(os.Stderr, "Error: no access token in response.")
			os.Exit(1)
		}

		if refreshToken == "" {
			refreshToken = cfg.RefreshToken
		}

		config.SaveTokens(accessToken, refreshToken)
		output.PrintSuccess(fmt.Sprintf("Token refreshed: %s", maskToken(accessToken)))
	},
}

func init() {
	rootCmd.AddCommand(loginCmd)
	rootCmd.AddCommand(logoutCmd)
	rootCmd.AddCommand(refreshTokenCmd)
}
