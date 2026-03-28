package cmd

import (
	"fmt"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var tfaStatusCmd = &cobra.Command{
	Use:   "status",
	Short: "Show 2FA status",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/security/2fa", nil, true)
		output.PrintItem(extractObj(result))
	},
}

var tfaSetupCmd = &cobra.Command{
	Use:   "setup",
	Short: "Set up two-factor authentication",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Post("/security/2fa/setup", nil, true, 0)
		obj := extractObj(result)

		output.PrintSuccess("2FA setup initiated.")
		fmt.Println()

		secret := getString(obj, "secret")
		if secret != "" {
			fmt.Printf("  Secret: %s\n", secret)
			fmt.Println()
			fmt.Println("  Add this secret to your authenticator app (e.g. Google Authenticator).")
			fmt.Println("  Then verify with: craft 2fa verify --code <CODE>")
		}

		qrURL := getString(obj, "qrCodeUrl")
		if qrURL == "" {
			qrURL = getString(obj, "qr_code_url")
		}
		if qrURL == "" {
			qrURL = getString(obj, "otpauthUrl")
		}
		if qrURL != "" {
			fmt.Println()
			fmt.Printf("  QR URL: %s\n", qrURL)
		}

		fmt.Println()
		output.PrintItem(obj)
	},
}

var tfaVerifyCmd = &cobra.Command{
	Use:   "verify",
	Short: "Verify 2FA setup with a code",
	Run: func(cmd *cobra.Command, args []string) {
		code, _ := cmd.Flags().GetString("code")
		if code == "" {
			code = PromptText("Enter 2FA code:")
		}

		body := map[string]interface{}{
			"code": code,
		}

		client.Post("/security/2fa/verify", body, true, 0)
		output.PrintSuccess("2FA verified and enabled.")
	},
}

var tfaDisableCmd = &cobra.Command{
	Use:   "disable",
	Short: "Disable two-factor authentication",
	Run: func(cmd *cobra.Command, args []string) {
		code, _ := cmd.Flags().GetString("code")
		if code == "" {
			code = PromptText("Enter 2FA code to disable:")
		}

		body := map[string]interface{}{
			"code": code,
		}

		client.Post("/security/2fa/disable", body, true, 0)
		output.PrintSuccess("2FA disabled.")
	},
}

func init() {
	tfaVerifyCmd.Flags().String("code", "", "2FA verification code")
	tfaDisableCmd.Flags().String("code", "", "2FA code to confirm disable")

	TFACmd.AddCommand(tfaStatusCmd)
	TFACmd.AddCommand(tfaSetupCmd)
	TFACmd.AddCommand(tfaVerifyCmd)
	TFACmd.AddCommand(tfaDisableCmd)
}
