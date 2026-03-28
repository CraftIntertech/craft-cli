package cmd

import (
	"fmt"
	"strings"

	"github.com/CraftIntertech/craft-cli/internal/client"
	"github.com/CraftIntertech/craft-cli/internal/output"
	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

// statusColor returns a colored string for ticket status.
func statusColor(status string) string {
	switch strings.ToLower(status) {
	case "open":
		return color.GreenString(status)
	case "closed":
		return color.RedString(status)
	case "pending":
		return color.YellowString(status)
	case "answered":
		return color.CyanString(status)
	default:
		return status
	}
}

// priorityColor returns a colored string for ticket priority.
func priorityColor(priority string) string {
	switch strings.ToLower(priority) {
	case "high", "urgent":
		return color.RedString(priority)
	case "medium":
		return color.YellowString(priority)
	case "low":
		return color.GreenString(priority)
	default:
		return priority
	}
}

var ticketListCmd = &cobra.Command{
	Use:   "list",
	Short: "List all support tickets",
	Run: func(cmd *cobra.Command, args []string) {
		result := client.Get("/tickets", nil, true)
		tickets := extractList(result, "tickets")

		var rows [][]string
		for _, t := range tickets {
			rows = append(rows, []string{
				getString(t, "id"),
				getString(t, "subject"),
				getString(t, "status"),
				getString(t, "created"),
			})
		}

		output.PrintTable(rows, []string{"ID", "Subject", "Status", "Created"})
	},
}

var ticketGetCmd = &cobra.Command{
	Use:   "get [TICKET_ID]",
	Short: "View a support ticket and its messages",
	Run: func(cmd *cobra.Command, args []string) {
		ticketID := ""
		if len(args) > 0 {
			ticketID = args[0]
		}
		if ticketID == "" {
			ticketID = SelectTicket("Select ticket to view")
		}

		result := client.Get(fmt.Sprintf("/tickets/%s", ticketID), nil, true)
		ticket := extractObj(result)

		// Print header.
		fmt.Println()
		fmt.Printf("  ID:       %s\n", getString(ticket, "id"))
		fmt.Printf("  Subject:  %s\n", getString(ticket, "subject"))
		fmt.Printf("  Status:   %s\n", statusColor(getString(ticket, "status")))
		fmt.Printf("  Priority: %s\n", priorityColor(getString(ticket, "priority")))
		fmt.Printf("  Created:  %s\n", getString(ticket, "created"))
		fmt.Printf("  Updated:  %s\n", getString(ticket, "updated"))
		fmt.Println()

		// Extract messages.
		var messages []map[string]interface{}
		if msgVal, ok := ticket["messages"]; ok {
			if arr, ok := msgVal.([]interface{}); ok {
				messages = toMapSlice(arr)
			}
		}

		fmt.Printf("── Messages (%d) ──\n", len(messages))
		fmt.Println()

		for _, msg := range messages {
			author := getString(msg, "author")
			if author == "" {
				author = getString(msg, "name")
			}
			timestamp := getString(msg, "created")
			if timestamp == "" {
				timestamp = getString(msg, "createdAt")
			}
			body := getString(msg, "body")
			if body == "" {
				body = getString(msg, "message")
			}
			if body == "" {
				body = getString(msg, "content")
			}

			isStaff := false
			if role, ok := msg["role"]; ok {
				if r, ok := role.(string); ok && strings.ToLower(r) == "staff" {
					isStaff = true
				}
			}
			if staff, ok := msg["isStaff"]; ok {
				if b, ok := staff.(bool); ok && b {
					isStaff = true
				}
			}
			if t, ok := msg["type"]; ok {
				if s, ok := t.(string); ok && strings.ToLower(s) == "staff" {
					isStaff = true
				}
			}

			tag := color.CyanString("[You]")
			if isStaff {
				tag = color.YellowString("[Staff]")
			}

			fmt.Printf("%s %s  %s\n", tag, author, timestamp)
			// Indent the message body.
			for _, line := range strings.Split(body, "\n") {
				fmt.Printf("  %s\n", line)
			}
			fmt.Println()
		}
	},
}

var ticketCreateCmd = &cobra.Command{
	Use:   "create",
	Short: "Create a new support ticket",
	Run: func(cmd *cobra.Command, args []string) {
		subject, _ := cmd.Flags().GetString("subject")
		body, _ := cmd.Flags().GetString("body")
		vmID, _ := cmd.Flags().GetString("vm-id")

		if subject == "" {
			subject = PromptText("Ticket subject:")
		}
		if body == "" {
			body = PromptText("Ticket body:")
		}

		reqBody := map[string]interface{}{
			"subject": subject,
			"body":    body,
		}
		if vmID != "" {
			reqBody["vmId"] = vmID
		}

		result := client.Post("/tickets", reqBody, true, 0)
		output.PrintSuccess("Ticket created.")
		output.PrintItem(extractObj(result))
	},
}

var ticketReplyCmd = &cobra.Command{
	Use:   "reply [TICKET_ID]",
	Short: "Reply to a support ticket",
	Run: func(cmd *cobra.Command, args []string) {
		ticketID := ""
		if len(args) > 0 {
			ticketID = args[0]
		}
		if ticketID == "" {
			ticketID = SelectTicket("Select ticket to reply to")
		}

		body, _ := cmd.Flags().GetString("body")
		if body == "" {
			body = PromptText("Reply message:")
		}

		reqBody := map[string]interface{}{
			"body": body,
		}

		result := client.Post(fmt.Sprintf("/tickets/%s/messages", ticketID), reqBody, true, 0)
		output.PrintSuccess("Reply sent.")
		output.PrintItem(extractObj(result))
	},
}

var ticketCloseCmd = &cobra.Command{
	Use:   "close [TICKET_ID]",
	Short: "Close a support ticket",
	Run: func(cmd *cobra.Command, args []string) {
		ticketID := ""
		if len(args) > 0 {
			ticketID = args[0]
		}
		if ticketID == "" {
			ticketID = SelectTicket("Select ticket to close")
		}

		if !Confirm(fmt.Sprintf("Are you sure you want to close ticket %s?", ticketID)) {
			output.PrintInfo("Cancelled.")
			return
		}

		client.Patch(fmt.Sprintf("/tickets/%s/close", ticketID), nil, true)
		output.PrintSuccess("Ticket closed.")
	},
}

func init() {
	ticketCreateCmd.Flags().String("subject", "", "Ticket subject")
	ticketCreateCmd.Flags().String("body", "", "Ticket body")
	ticketCreateCmd.Flags().String("vm-id", "", "Associated VM ID")

	ticketReplyCmd.Flags().String("body", "", "Reply message body")

	TicketCmd.AddCommand(ticketListCmd)
	TicketCmd.AddCommand(ticketGetCmd)
	TicketCmd.AddCommand(ticketCreateCmd)
	TicketCmd.AddCommand(ticketReplyCmd)
	TicketCmd.AddCommand(ticketCloseCmd)
}
