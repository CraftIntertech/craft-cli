package cmd

import (
	"fmt"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

var referralCodeCmd = &cobra.Command{
	Use:   "code",
	Short: "Show your referral code",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/referral", nil, true)
		output.PrintItem(extractObj(result))
	},
}

var referralStatsCmd = &cobra.Command{
	Use:   "stats",
	Short: "Show referral statistics",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/referral/stats", nil, true)
		output.PrintItem(extractObj(result))
	},
}

var referralCheckCmd = &cobra.Command{
	Use:   "check [CODE]",
	Short: "Check if a referral code is valid",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		code := args[0]
		result := client.Get(fmt.Sprintf("/referral/check/%s", code), nil, false)
		output.PrintItem(extractObj(result))
	},
}

func init() {
	ReferralCmd.AddCommand(referralCodeCmd)
	ReferralCmd.AddCommand(referralStatsCmd)
	ReferralCmd.AddCommand(referralCheckCmd)
}
