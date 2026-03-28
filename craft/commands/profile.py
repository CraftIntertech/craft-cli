import click

from craft.client import get, put
from craft.output import print_item, print_success


@click.command("show")
def profile_show():
    """Show your profile."""
    data = get("/me")
    print_item(data)


@click.command("update")
@click.option("--first-name", help="First name")
@click.option("--last-name", help="Last name")
@click.option("--phone", help="Phone number")
@click.option("--address", help="Address")
@click.option("--company", help="Company name")
def profile_update(first_name, last_name, phone, address, company):
    """Update profile fields."""
    body = {}
    if first_name:
        body["firstName"] = first_name
    if last_name:
        body["lastName"] = last_name
    if phone:
        body["phone"] = phone
    if address:
        body["address"] = address
    if company:
        body["company"] = company

    if not body:
        click.echo("No fields to update. Use --help to see options.")
        return

    data = put("/me", body)
    print_success("Profile updated.")
    print_item(data)


@click.command("change-password")
@click.option("--current-password", prompt=True, hide_input=True)
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True)
def change_password(current_password, new_password):
    """Change account password."""
    put("/me/password", {"currentPassword": current_password, "newPassword": new_password})
    print_success("Password changed.")
