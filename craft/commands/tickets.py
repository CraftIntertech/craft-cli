import click

from craft.client import get, patch, post
from craft.output import print_item, print_json, print_success, print_table


@click.command("list")
def ticket_list():
    """List support tickets."""
    data = get("/tickets")
    items = data.get("data", data)
    if isinstance(items, dict):
        items = items.get("items", items.get("tickets", []))
    if isinstance(items, list) and items:
        rows = []
        for t in items:
            rows.append([
                t.get("id", ""),
                t.get("subject", ""),
                t.get("status", ""),
                t.get("createdAt", ""),
            ])
        print_table(rows, ["ID", "Subject", "Status", "Created"])
    else:
        print_json(data)


@click.command("get")
@click.argument("ticket_id")
def ticket_get(ticket_id):
    """Get ticket with message history."""
    data = get(f"/tickets/{ticket_id}")
    print_item(data)


@click.command("create")
@click.option("--subject", default=None, help="Subject (1-255 chars)")
@click.option("--body", "body_text", default=None, help="Message (1-10,000 chars)")
@click.option("--vm-id", default=None, help="Link to a VM (optional)")
def ticket_create(subject, body_text, vm_id):
    """Create a support ticket.

    \b
    If --subject or --body is omitted, you will be prompted interactively.

    \b
    Examples:
      craft ticket create --subject "Help" --body "Details..."
      craft ticket create                    # Interactive prompts
    """
    if not subject:
        subject = click.prompt("Subject")
    if not body_text:
        body_text = click.prompt("Message")
    body = {"subject": subject, "body": body_text}
    if vm_id:
        body["vmId"] = vm_id
    data = post("/tickets", body)
    print_success("Ticket created.")
    print_item(data)


@click.command("reply")
@click.argument("ticket_id")
@click.option("--body", "body_text", default=None, help="Reply message")
def ticket_reply(ticket_id, body_text):
    """Reply to a ticket."""
    if not body_text:
        body_text = click.prompt("Message")
    post(f"/tickets/{ticket_id}/messages", {"body": body_text})
    print_success("Reply sent.")


@click.command("close")
@click.argument("ticket_id")
def ticket_close(ticket_id):
    """Close a ticket."""
    patch(f"/tickets/{ticket_id}/close")
    print_success(f"Ticket {ticket_id} closed.")
