package cmd

import (
	"fmt"
	"os"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

// Version can be set at build time via ldflags:
//
//	go build -ldflags "-X github.com/CraftIntertech/craft-cli/cmd.Version=1.0.0"
var Version = "dev"

var rootCmd = &cobra.Command{
	Use:   "craft",
	Short: "CraftIntertech Cloud CLI",
	Long:  "CraftIntertech Cloud CLI — manage VMs, hosting, wallet, and more.",
}

// Subcommand groups.

// VMCmd is the parent command for VM operations.
var VMCmd = &cobra.Command{
	Use:   "vm",
	Short: "Manage virtual machines",
}

// FirewallCmd is the parent command for firewall operations.
var FirewallCmd = &cobra.Command{
	Use:   "firewall",
	Short: "Manage firewall rules",
}

// SnapshotCmd is the parent command for snapshot operations.
var SnapshotCmd = &cobra.Command{
	Use:   "snapshot",
	Short: "Manage snapshots",
}

// RDNSCmd is the parent command for reverse DNS operations.
var RDNSCmd = &cobra.Command{
	Use:   "rdns",
	Short: "Manage reverse DNS records",
}

// RescueCmd is the parent command for rescue mode operations.
var RescueCmd = &cobra.Command{
	Use:   "rescue",
	Short: "Manage rescue mode",
}

// AgentCmd is the parent command for server agent operations.
var AgentCmd = &cobra.Command{
	Use:   "agent",
	Short: "Manage server agent",
}

// BillingCmd is the parent command for billing operations.
var BillingCmd = &cobra.Command{
	Use:   "billing",
	Short: "Manage billing and invoices",
}

// HostingCmd is the parent command for web hosting operations.
var HostingCmd = &cobra.Command{
	Use:   "hosting",
	Short: "Manage web hosting",
}

// WalletCmd is the parent command for wallet operations.
var WalletCmd = &cobra.Command{
	Use:   "wallet",
	Short: "Manage wallet and payments",
}

// SSHKeyCmd is the parent command for SSH key operations.
var SSHKeyCmd = &cobra.Command{
	Use:   "ssh-key",
	Short: "Manage SSH keys",
}

// APIKeyCmd is the parent command for API key operations.
var APIKeyCmd = &cobra.Command{
	Use:   "api-key",
	Short: "Manage API keys",
}

// TFACmd is the parent command for two-factor authentication operations.
var TFACmd = &cobra.Command{
	Use:   "2fa",
	Short: "Manage two-factor authentication",
}

// TicketCmd is the parent command for support ticket operations.
var TicketCmd = &cobra.Command{
	Use:   "ticket",
	Short: "Manage support tickets",
}

// ReferralCmd is the parent command for referral program operations.
var ReferralCmd = &cobra.Command{
	Use:   "referral",
	Short: "Manage referral program",
}

// NodeCmd is the parent command for node operations.
var NodeCmd = &cobra.Command{
	Use:   "node",
	Short: "Manage nodes",
}

// PlanCmd is the parent command for plan operations.
var PlanCmd = &cobra.Command{
	Use:   "plan",
	Short: "View available plans",
}

// SystemCmd is the parent command for system operations.
var SystemCmd = &cobra.Command{
	Use:   "system",
	Short: "System information and status",
}

// ProfileCmd is the parent command for profile operations.
var ProfileCmd = &cobra.Command{
	Use:   "profile",
	Short: "Manage your profile",
}

var testAPICmd = &cobra.Command{
	Use:   "test-api",
	Short: "Test API connectivity",
	Run: func(cmd *cobra.Command, args []string) {
		result, err := client.APIRequest("GET", "/ping", nil, nil, false, 10)
		if err != nil {
			fmt.Fprintf(os.Stderr, "API test failed: %v\n", err)
			os.Exit(1)
		}
		fmt.Println("API connection successful.")
		output.PrintItem(result)
	},
}

var updateCmd = &cobra.Command{
	Use:   "update",
	Short: "Update the CLI to the latest version",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Checking for updates...")
		fmt.Printf("Current version: %s\n", Version)
		fmt.Println("To update, download the latest release from https://github.com/CraftIntertech/craft-cli/releases")
	},
}

func init() {
	// Subcommand groups.
	rootCmd.AddCommand(VMCmd)
	rootCmd.AddCommand(FirewallCmd)
	rootCmd.AddCommand(SnapshotCmd)
	rootCmd.AddCommand(RDNSCmd)
	rootCmd.AddCommand(RescueCmd)
	rootCmd.AddCommand(AgentCmd)
	rootCmd.AddCommand(BillingCmd)
	rootCmd.AddCommand(HostingCmd)
	rootCmd.AddCommand(WalletCmd)
	rootCmd.AddCommand(SSHKeyCmd)
	rootCmd.AddCommand(APIKeyCmd)
	rootCmd.AddCommand(TFACmd)
	rootCmd.AddCommand(TicketCmd)
	rootCmd.AddCommand(ReferralCmd)
	rootCmd.AddCommand(NodeCmd)
	rootCmd.AddCommand(PlanCmd)
	rootCmd.AddCommand(SystemCmd)
	rootCmd.AddCommand(ProfileCmd)

	// Top-level utility commands.
	rootCmd.AddCommand(testAPICmd)
	rootCmd.AddCommand(updateCmd)
}

// Execute runs the root command.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
