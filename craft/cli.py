import os
import shutil
import subprocess
import sys
from pathlib import Path

import click

from craft import __version__
from craft.commands.auth import login, logout, refresh
from craft.commands.profile import change_password, profile_show, profile_update
from craft.commands.vm import (
    vm_console,
    vm_create,
    vm_delete,
    vm_get,
    vm_list,
    vm_metrics,
    vm_network,
    vm_reboot,
    vm_reinstall,
    vm_rename,
    vm_reset_network,
    vm_reset_password,
    vm_resize,
    vm_start,
    vm_status,
    vm_stop,
)
from craft.commands.firewall import fw_add, fw_delete, fw_list, fw_options
from craft.commands.snapshot import snap_create, snap_delete, snap_list, snap_rollback, snap_sync
from craft.commands.rdns import rdns_delete, rdns_get, rdns_set
from craft.commands.rescue import rescue_disable, rescue_enable
from craft.commands.agent import agent_enable, agent_fstrim, agent_info
from craft.commands.billing import billing_auto_renew, billing_renew, billing_show
from craft.commands.hosting import (
    hosting_auto_renew,
    hosting_billing,
    hosting_create,
    hosting_delete,
    hosting_get,
    hosting_list,
    hosting_login_url,
    hosting_nodes,
    hosting_plans,
    hosting_renew,
)
from craft.commands.wallet import wallet_balance, wallet_topup, wallet_transactions
from craft.commands.ssh_keys import sshkey_add, sshkey_add_file, sshkey_delete, sshkey_list
from craft.commands.api_keys import apikey_create, apikey_list, apikey_revoke
from craft.commands.security import twofa_disable, twofa_setup, twofa_status, twofa_verify
from craft.commands.tickets import ticket_close, ticket_create, ticket_get, ticket_list, ticket_reply
from craft.commands.referral import referral_check, referral_code, referral_stats
from craft.commands.nodes import node_hardware, node_list
from craft.commands.plans import plans_colocation, plans_dedicated, plans_os, plans_vm
from craft.commands.system import system_nodes, system_plans, system_status
from craft.commands.activity import activity_list
from craft.commands.test_api import test_api
from craft.config import get_base_url, load_config, save_config


@click.group()
@click.version_option(__version__, prog_name="craft")
def cli():
    """CraftIntertech Cloud CLI — manage VMs, hosting, wallet, and more.

    \b
    Quick start:
      craft login <token>          # Login with API key (cit_...) or JWT
      craft vm list                # List your VMs
      craft vm create -i           # Create VM (interactive wizard)
      craft test-api               # Test API connectivity

    \b
    Common shortcuts:
      craft vm list                # = craft vm list --page 1
      craft wallet balance         # Check wallet balance
      craft hosting list           # List hosting accounts
      craft system status          # Public system status (no login needed)
    """
    pass


# --- Auth (top-level) ---
cli.add_command(login)
cli.add_command(logout)
cli.add_command(refresh, "refresh-token")


# --- Config ---
@cli.command("config")
@click.option("--base-url", default=None, help="Set API base URL")
@click.option("--token", default=None, help="Set access token directly (e.g. API key)")
@click.option("--show", is_flag=True, help="Show current config")
def config_cmd(base_url, token, show):
    """View or update CLI configuration."""
    cfg = load_config()
    if show:
        click.echo(f"Base URL:  {cfg.get('base_url', '')}")
        click.echo(f"Token:     {'****' + cfg['access_token'][-8:] if cfg.get('access_token') else '(none)'}")
        return
    if base_url:
        cfg["base_url"] = base_url
    if token:
        cfg["access_token"] = token
    save_config(cfg)
    click.echo("Config updated.")


# --- Profile ---
@cli.group()
def profile():
    """Manage your profile."""
    pass

profile.add_command(profile_show)
profile.add_command(profile_update)
profile.add_command(change_password)


# --- VM ---
@cli.group()
def vm():
    """Manage virtual machines."""
    pass

vm.add_command(vm_list)
vm.add_command(vm_get)
vm.add_command(vm_create)
vm.add_command(vm_delete)
vm.add_command(vm_status)
vm.add_command(vm_start)
vm.add_command(vm_stop)
vm.add_command(vm_reboot)
vm.add_command(vm_rename)
vm.add_command(vm_reset_password)
vm.add_command(vm_reset_network)
vm.add_command(vm_resize)
vm.add_command(vm_reinstall)
vm.add_command(vm_console)
vm.add_command(vm_network)
vm.add_command(vm_metrics)


# --- Firewall ---
@cli.group()
def firewall():
    """Manage VM firewall rules."""
    pass

firewall.add_command(fw_list)
firewall.add_command(fw_add)
firewall.add_command(fw_delete)
firewall.add_command(fw_options)


# --- Snapshot ---
@cli.group()
def snapshot():
    """Manage VM snapshots."""
    pass

snapshot.add_command(snap_list)
snapshot.add_command(snap_create)
snapshot.add_command(snap_delete)
snapshot.add_command(snap_rollback)
snapshot.add_command(snap_sync)


# --- rDNS ---
@cli.group()
def rdns():
    """Manage reverse DNS records."""
    pass

rdns.add_command(rdns_get)
rdns.add_command(rdns_set)
rdns.add_command(rdns_delete)


# --- Rescue ---
@cli.group()
def rescue():
    """VM rescue mode."""
    pass

rescue.add_command(rescue_enable)
rescue.add_command(rescue_disable)


# --- Guest Agent ---
@cli.group("agent")
def guest_agent():
    """QEMU guest agent commands."""
    pass

guest_agent.add_command(agent_enable)
guest_agent.add_command(agent_info)
guest_agent.add_command(agent_fstrim)


# --- Billing ---
@cli.group()
def billing():
    """VM billing and renewal."""
    pass

billing.add_command(billing_show)
billing.add_command(billing_renew)
billing.add_command(billing_auto_renew)


# --- Hosting ---
@cli.group()
def hosting():
    """Manage web hosting accounts."""
    pass

hosting.add_command(hosting_plans)
hosting.add_command(hosting_nodes)
hosting.add_command(hosting_list)
hosting.add_command(hosting_get)
hosting.add_command(hosting_create)
hosting.add_command(hosting_delete)
hosting.add_command(hosting_login_url)
hosting.add_command(hosting_billing)
hosting.add_command(hosting_renew)
hosting.add_command(hosting_auto_renew)


# --- Wallet ---
@cli.group()
def wallet():
    """Wallet balance and transactions."""
    pass

wallet.add_command(wallet_balance)
wallet.add_command(wallet_transactions)
wallet.add_command(wallet_topup)


# --- SSH Keys ---
@cli.group("ssh-key")
def ssh_key():
    """Manage SSH public keys."""
    pass

ssh_key.add_command(sshkey_list)
ssh_key.add_command(sshkey_add)
ssh_key.add_command(sshkey_add_file)
ssh_key.add_command(sshkey_delete)


# --- API Keys ---
@cli.group("api-key")
def api_key():
    """Manage API keys."""
    pass

api_key.add_command(apikey_list)
api_key.add_command(apikey_create)
api_key.add_command(apikey_revoke)


# --- 2FA ---
@cli.group("2fa")
def twofa():
    """Two-factor authentication."""
    pass

twofa.add_command(twofa_status)
twofa.add_command(twofa_setup)
twofa.add_command(twofa_verify)
twofa.add_command(twofa_disable)


# --- Tickets ---
@cli.group()
def ticket():
    """Support tickets."""
    pass

ticket.add_command(ticket_list)
ticket.add_command(ticket_get)
ticket.add_command(ticket_create)
ticket.add_command(ticket_reply)
ticket.add_command(ticket_close)


# --- Referral ---
@cli.group()
def referral():
    """Referral program."""
    pass

referral.add_command(referral_code)
referral.add_command(referral_stats)
referral.add_command(referral_check)


# --- Nodes ---
@cli.group()
def node():
    """Infrastructure nodes."""
    pass

node.add_command(node_list)
node.add_command(node_hardware)


# --- Plans ---
@cli.group()
def plan():
    """VM plans and OS templates."""
    pass

plan.add_command(plans_vm)
plan.add_command(plans_os)
plan.add_command(plans_dedicated)
plan.add_command(plans_colocation)


# --- System ---
@cli.group()
def system():
    """System status (public, no auth required)."""
    pass

system.add_command(system_status)
system.add_command(system_plans)
system.add_command(system_nodes)


# --- Activity ---
cli.add_command(activity_list, "activity")

# --- Test API ---
cli.add_command(test_api)


# --- Update ---
@cli.command()
def update():
    """Update craft-cli to the latest version."""
    import platform

    install_dir = Path.home() / ".local" / "share" / "craft-cli"
    if not install_dir.exists():
        click.echo("Error: Installation not found at ~/.local/share/craft-cli", err=True)
        click.echo("Reinstall with: curl -fsSL https://raw.githubusercontent.com/CraftIntertech/craft-cli/main/install.sh | bash", err=True)
        sys.exit(1)

    old_version = __version__
    click.echo(f"Current version: {old_version}")
    click.echo("Checking for updates...")

    try:
        subprocess.run(
            ["git", "-C", str(install_dir), "fetch", "origin", "main"],
            check=True, capture_output=True,
        )

        # Read remote VERSION before reset
        result = subprocess.run(
            ["git", "-C", str(install_dir), "show", "origin/main:VERSION"],
            check=True, capture_output=True, text=True,
        )
        new_version = result.stdout.strip()

        if new_version == old_version:
            click.echo(click.style(f"Already up to date (v{old_version}).", fg="green"))
            return

        click.echo(f"New version available: {old_version} → {new_version}")

        # v2.0+ is a Go rewrite — cannot pip install, need to download binary
        major = int(new_version.split(".")[0])
        if major >= 2:
            click.echo()
            click.echo(click.style("v2.0+ is rewritten in Go — single binary, no Python needed!", fg="cyan", bold=True))
            click.echo()

            # Detect platform
            system = platform.system().lower()  # linux, darwin, windows
            machine = platform.machine().lower()
            if machine in ("x86_64", "amd64"):
                arch = "amd64"
            elif machine in ("aarch64", "arm64"):
                arch = "arm64"
            else:
                arch = machine

            binary = f"craft-{system}-{arch}"
            if system == "windows":
                binary += ".exe"

            url = f"https://github.com/CraftIntertech/craft-cli/releases/download/v{new_version}/{binary}"
            bin_path = Path.home() / ".local" / "bin" / "craft"

            click.echo(f"Downloading {binary}...")
            try:
                import urllib.request
                urllib.request.urlretrieve(url, str(bin_path))
                bin_path.chmod(0o755)
                click.echo(click.style(f"Updated: v{old_version} → v{new_version} (Go binary)", fg="green"))
                click.echo(f"Installed to: {bin_path}")
                click.echo()
                click.echo("You can remove the old Python installation:")
                click.echo(f"  rm -rf {install_dir}")
                return
            except Exception as e:
                click.echo(click.style(f"Auto-download failed: {e}", fg="yellow"), err=True)
                click.echo()
                click.echo("Install manually:")
                click.echo(f"  curl -fsSL {url} -o {bin_path}")
                click.echo(f"  chmod +x {bin_path}")
                click.echo()
                click.echo(f"Or visit: https://github.com/CraftIntertech/craft-cli/releases/tag/v{new_version}")
                return

        subprocess.run(
            ["git", "-C", str(install_dir), "reset", "--hard", "origin/main"],
            check=True, capture_output=True,
        )

        venv_pip = install_dir / ".venv" / "bin" / "pip"
        if venv_pip.exists():
            subprocess.run(
                [str(venv_pip), "install", "-e", str(install_dir), "-q"],
                check=True, capture_output=True,
            )

        click.echo(click.style(f"Updated: v{old_version} → v{new_version}", fg="green"))

    except subprocess.CalledProcessError as e:
        click.echo(f"Error: Update failed — {e}", err=True)
        sys.exit(1)


# --- Version ---
@cli.command("version")
def version_cmd():
    """Show version and check for updates."""
    click.echo(f"craft-cli v{__version__}")

    install_dir = Path.home() / ".local" / "share" / "craft-cli"
    if not install_dir.exists():
        return

    try:
        subprocess.run(
            ["git", "-C", str(install_dir), "fetch", "origin", "main"],
            check=True, capture_output=True, timeout=10,
        )
        result = subprocess.run(
            ["git", "-C", str(install_dir), "show", "origin/main:VERSION"],
            check=True, capture_output=True, text=True, timeout=5,
        )
        remote_version = result.stdout.strip()

        if remote_version != __version__:
            click.echo(click.style(
                f"Update available: v{__version__} → v{remote_version}  (run: craft update)",
                fg="yellow",
            ))
        else:
            click.echo(click.style("Up to date.", fg="green"))
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        click.echo("Could not check for updates.")


# --- Uninstall ---
@cli.command()
def uninstall():
    """Remove craft-cli from this machine."""
    install_dir = Path.home() / ".local" / "share" / "craft-cli"
    bin_file = Path.home() / ".local" / "bin" / "craft"
    config_dir = Path.home() / ".config" / "craft"

    click.echo("This will remove:")
    click.echo(f"  - {install_dir}")
    click.echo(f"  - {bin_file}")
    if not click.confirm("\nContinue?", default=False):
        click.echo("Cancelled.")
        return

    if bin_file.exists():
        bin_file.unlink()
        click.echo(f"  Removed {bin_file}")
    if install_dir.exists():
        shutil.rmtree(install_dir)
        click.echo(f"  Removed {install_dir}")

    if config_dir.exists():
        if click.confirm(f"\nAlso remove config ({config_dir})?", default=False):
            shutil.rmtree(config_dir)
            click.echo(f"  Removed {config_dir}")
        else:
            click.echo(f"  Config kept at {config_dir}")

    click.echo(click.style("\ncraft-cli uninstalled.", fg="green"))
