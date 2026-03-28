package cmd

import (
	"fmt"
	"time"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

type apiTestEndpoint struct {
	path string
	auth bool
}

var publicEndpoints = []apiTestEndpoint{
	{"/system/status", false},
	{"/system/plans", false},
	{"/system/nodes", false},
	{"/dedicated-plans", false},
	{"/colocation-plans", false},
}

var authenticatedEndpoints = []apiTestEndpoint{
	{"/me", true},
	{"/vms", true},
	{"/wallet", true},
	{"/ssh-keys", true},
	{"/api-keys", true},
	{"/tickets", true},
	{"/nodes", true},
	{"/plans", true},
	{"/os-templates", true},
	{"/hosting", true},
	{"/hosting/plans", true},
	{"/hosting/nodes", true},
	{"/security/2fa", true},
	{"/referral", true},
	{"/referral/stats", true},
	{"/activity", true},
	{"/wallet/transactions", true},
}

var testAPICmdExtended = &cobra.Command{
	Use:   "test-api-all",
	Short: "Test API connectivity (extended)",
	Run: func(cmd *cobra.Command, args []string) {
		all, _ := cmd.Flags().GetBool("all")
		verbose, _ := cmd.Flags().GetBool("verbose")

		endpoints := make([]apiTestEndpoint, len(publicEndpoints))
		copy(endpoints, publicEndpoints)

		if all {
			endpoints = append(endpoints, authenticatedEndpoints...)
		}

		pass := 0
		fail := 0

		fmt.Println()
		fmt.Printf("Testing %d endpoint(s)...\n\n", len(endpoints))

		for _, ep := range endpoints {
			label := ep.path
			if ep.auth {
				label += " (auth)"
			}

			start := time.Now()
			_, err := client.APIRequest("GET", ep.path, nil, nil, ep.auth, 10)
			elapsed := time.Since(start)

			if err != nil {
				fail++
				color.Red("  FAIL  %s", label)
				if verbose {
					fmt.Printf("        Error: %v\n", err)
					fmt.Printf("        Time:  %s\n", elapsed.Round(time.Millisecond))
				}
			} else {
				pass++
				color.Green("  PASS  %s", label)
				if verbose {
					fmt.Printf("        Time:  %s\n", elapsed.Round(time.Millisecond))
				}
			}
		}

		fmt.Println()
		fmt.Printf("Results: ")
		color.Green("%d passed", pass)
		if fail > 0 {
			fmt.Printf(", ")
			color.Red("%d failed", fail)
		}
		fmt.Println()
	},
}

func init() {
	testAPICmdExtended.Flags().BoolP("all", "a", false, "Test all endpoints including authenticated ones")
	testAPICmdExtended.Flags().BoolP("verbose", "v", false, "Show response times and error details")

	rootCmd.AddCommand(testAPICmdExtended)
}
