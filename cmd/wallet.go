package cmd

import (
	"fmt"
	"os"
	"strconv"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/spf13/cobra"
)

func init() {
	// wallet balance
	walletBalanceCmd := &cobra.Command{
		Use:   "balance",
		Short: "Show wallet balance",
		Run:   walletBalanceRun,
	}

	// wallet transactions
	walletTransactionsCmd := &cobra.Command{
		Use:   "transactions",
		Short: "List wallet transactions",
		Run:   walletTransactionsRun,
	}
	walletTransactionsCmd.Flags().Int("page", 1, "Page number")
	walletTransactionsCmd.Flags().Int("limit", 20, "Items per page")

	// wallet topup
	walletTopupCmd := &cobra.Command{
		Use:   "topup",
		Short: "Top up wallet balance",
		Run:   walletTopupRun,
	}
	walletTopupCmd.Flags().Float64("amount", 0, "Top-up amount")
	walletTopupCmd.Flags().String("reference", "", "Payment reference")
	walletTopupCmd.Flags().String("note", "", "Optional note")

	WalletCmd.AddCommand(walletBalanceCmd)
	WalletCmd.AddCommand(walletTransactionsCmd)
	WalletCmd.AddCommand(walletTopupCmd)
}

func walletBalanceRun(cmd *cobra.Command, args []string) {
	result := client.Get("/wallet", nil, true)
	output.PrintItem(result)
}

func walletTransactionsRun(cmd *cobra.Command, args []string) {
	page, _ := cmd.Flags().GetInt("page")
	limit, _ := cmd.Flags().GetInt("limit")

	params := map[string]string{
		"page":  strconv.Itoa(page),
		"limit": strconv.Itoa(limit),
	}

	result := client.Get("/wallet/transactions", params, true)

	data, ok := result["data"].([]interface{})
	if !ok {
		fmt.Fprintln(os.Stderr, "No transactions found.")
		return
	}

	var rows [][]string
	for _, item := range data {
		tx, ok := item.(map[string]interface{})
		if !ok {
			continue
		}
		rows = append(rows, []string{
			fmt.Sprintf("%v", tx["id"]),
			fmt.Sprintf("%v", tx["type"]),
			fmt.Sprintf("%v", tx["amount"]),
			fmt.Sprintf("%v", tx["description"]),
			fmt.Sprintf("%v", tx["date"]),
		})
	}

	output.PrintTable(rows, []string{"ID", "Type", "Amount", "Description", "Date"})

	output.PrintPageInfo(result, page, limit)
}

func walletTopupRun(cmd *cobra.Command, args []string) {
	amount, _ := cmd.Flags().GetFloat64("amount")
	reference, _ := cmd.Flags().GetString("reference")
	note, _ := cmd.Flags().GetString("note")

	if amount <= 0 {
		amountStr := PromptText("Enter top-up amount:")
		parsed, err := strconv.ParseFloat(amountStr, 64)
		if err != nil || parsed <= 0 {
			fmt.Fprintln(os.Stderr, "Invalid amount.")
			os.Exit(1)
		}
		amount = parsed
	}

	if reference == "" {
		reference = PromptText("Enter payment reference:")
	}

	body := map[string]interface{}{
		"amount":    amount,
		"reference": reference,
	}
	if note != "" {
		body["note"] = note
	}

	result := client.Post("/wallet/topup", body, true, 0)

	output.PrintSuccess("Top-up request submitted successfully.")
	output.PrintItem(result)
}
