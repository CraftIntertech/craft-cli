package cmd

import (
	"fmt"
	"os"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var profileShowCmd = &cobra.Command{
	Use:   "show",
	Short: "Display your profile information",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/me", nil, true)
		output.PrintItem(result)
	},
}

var profileUpdateCmd = &cobra.Command{
	Use:   "update",
	Short: "Update your profile information",
	Run: func(cmd *cobra.Command, args []string) {
		body := make(map[string]interface{})

		if v, _ := cmd.Flags().GetString("first-name"); v != "" {
			body["firstName"] = v
		}
		if v, _ := cmd.Flags().GetString("last-name"); v != "" {
			body["lastName"] = v
		}
		if v, _ := cmd.Flags().GetString("phone"); v != "" {
			body["phone"] = v
		}
		if v, _ := cmd.Flags().GetString("address"); v != "" {
			body["address"] = v
		}
		if v, _ := cmd.Flags().GetString("company"); v != "" {
			body["company"] = v
		}

		if len(body) == 0 {
			fmt.Fprintln(os.Stderr, "Error: at least one field must be provided (--first-name, --last-name, --phone, --address, --company).")
			os.Exit(1)
		}

		result := client.Put("/me", body, true)
		output.PrintSuccess("Profile updated.")
		output.PrintItem(result)
	},
}

var profileChangePasswordCmd = &cobra.Command{
	Use:   "change-password",
	Short: "Change your account password",
	Run: func(cmd *cobra.Command, args []string) {
		currentPassword := PromptPassword("Current password:")
		newPassword := PromptPassword("New password:")
		confirmPassword := PromptPassword("Confirm new password:")

		if newPassword != confirmPassword {
			fmt.Fprintln(os.Stderr, "Error: new passwords do not match.")
			os.Exit(1)
		}

		body := map[string]interface{}{
			"currentPassword": currentPassword,
			"newPassword":     newPassword,
		}

		client.Put("/me/password", body, true)
		output.PrintSuccess("Password changed successfully.")
	},
}

func init() {
	profileUpdateCmd.Flags().String("first-name", "", "First name")
	profileUpdateCmd.Flags().String("last-name", "", "Last name")
	profileUpdateCmd.Flags().String("phone", "", "Phone number")
	profileUpdateCmd.Flags().String("address", "", "Address")
	profileUpdateCmd.Flags().String("company", "", "Company name")

	ProfileCmd.AddCommand(profileShowCmd)
	ProfileCmd.AddCommand(profileUpdateCmd)
	ProfileCmd.AddCommand(profileChangePasswordCmd)
}
