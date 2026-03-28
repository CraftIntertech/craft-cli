"""Tests for all CLI commands — verifies correct API endpoints are called."""

import pytest
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner

from craft.cli import cli
from tests.conftest import make_response


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_api():
    """Mock the requests.request to return success for all calls."""
    with patch("craft.client.get_token", return_value="test-token"), \
         patch("craft.client.get_base_url", return_value="https://api.test.com"), \
         patch("craft.client.requests.request") as mock_req:
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"data": {}}
        mock_req.return_value = resp
        yield mock_req


# ─── Auth ───

class TestAuth:
    def test_login(self, runner):
        with patch("craft.commands.auth.save_tokens") as mock_save:
            result = runner.invoke(cli, ["login", "cit_test12345678"])
            assert result.exit_code == 0
            assert "Token saved" in result.output
            mock_save.assert_called_once_with("cit_test12345678")

    def test_logout(self, runner, mock_api):
        with patch("craft.commands.auth.load_config", return_value={"refresh_token": "rt"}), \
             patch("craft.commands.auth.clear_tokens") as mock_clear:
            result = runner.invoke(cli, ["logout"])
            assert result.exit_code == 0
            assert "Logged out" in result.output
            mock_clear.assert_called_once()

    def test_refresh_token(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": {"accessToken": "new-token", "refreshToken": "new-refresh"}
        })
        with patch("craft.commands.auth.load_config", return_value={"refresh_token": "old-refresh"}), \
             patch("craft.commands.auth.save_tokens") as mock_save:
            result = runner.invoke(cli, ["refresh-token"])
            assert result.exit_code == 0
            mock_save.assert_called_once_with("new-token", "new-refresh")


# ─── Profile ───

class TestProfile:
    def test_profile_show(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": {"email": "test@example.com", "firstName": "John"}
        })
        result = runner.invoke(cli, ["profile", "show"])
        assert result.exit_code == 0

    def test_profile_update(self, runner, mock_api):
        result = runner.invoke(cli, ["profile", "update", "--first-name", "Jane"])
        assert result.exit_code == 0
        _, kwargs = mock_api.call_args
        assert kwargs["json"]["firstName"] == "Jane"

    def test_profile_update_no_fields(self, runner, mock_api):
        result = runner.invoke(cli, ["profile", "update"])
        assert "No fields to update" in result.output

    def test_change_password(self, runner, mock_api):
        result = runner.invoke(cli, ["profile", "change-password"],
                               input="oldpass\nnewpass\nnewpass\n")
        assert result.exit_code == 0


# ─── VM ───

class TestVM:
    def test_vm_list(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": [{"id": "vm-1", "name": "test", "status": "running", "ip": "1.2.3.4", "os": "Ubuntu"}]
        })
        result = runner.invoke(cli, ["vm", "list"])
        assert result.exit_code == 0

    def test_vm_list_pagination(self, runner, mock_api):
        mock_api.return_value = make_response({"data": []})
        result = runner.invoke(cli, ["vm", "list", "--page", "2", "--limit", "5"])
        assert result.exit_code == 0
        _, kwargs = mock_api.call_args
        assert kwargs["params"] == {"page": 2, "limit": 5}

    def test_vm_get(self, runner, mock_api):
        mock_api.return_value = make_response({"data": {"id": "vm-1", "name": "test"}})
        result = runner.invoke(cli, ["vm", "get", "vm-1"])
        assert result.exit_code == 0
        args, _ = mock_api.call_args
        assert "/vms/vm-1" in args[1]

    def test_vm_delete_confirm(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "delete", "vm-1"], input="y\n")
        assert result.exit_code == 0
        args, _ = mock_api.call_args
        assert args[0] == "DELETE"
        assert "/vms/vm-1" in args[1]

    def test_vm_delete_cancel(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "delete", "vm-1"], input="n\n")
        assert "Cancelled" in result.output

    def test_vm_start(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "start", "vm-1"])
        assert result.exit_code == 0
        args, _ = mock_api.call_args
        assert args[0] == "POST"
        assert "/vms/vm-1/start" in args[1]

    def test_vm_stop(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "stop", "vm-1"])
        assert result.exit_code == 0
        args, _ = mock_api.call_args
        assert "/vms/vm-1/stop" in args[1]

    def test_vm_reboot(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "reboot", "vm-1"])
        assert result.exit_code == 0
        args, _ = mock_api.call_args
        assert "/vms/vm-1/reboot" in args[1]

    def test_vm_rename(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "rename", "vm-1", "--name", "new-name"])
        assert result.exit_code == 0
        _, kwargs = mock_api.call_args
        assert kwargs["json"]["name"] == "new-name"

    def test_vm_status(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "status", "vm-1"])
        assert result.exit_code == 0
        args, _ = mock_api.call_args
        assert "/vms/vm-1/status" in args[1]

    def test_vm_console(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "console", "vm-1"])
        assert result.exit_code == 0
        args, _ = mock_api.call_args
        assert "/vms/vm-1/console" in args[1]

    def test_vm_network(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "network", "vm-1"])
        assert result.exit_code == 0
        args, _ = mock_api.call_args
        assert "/vms/vm-1/network" in args[1]

    def test_vm_metrics(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "metrics", "vm-1", "--hours", "48"])
        assert result.exit_code == 0
        _, kwargs = mock_api.call_args
        assert kwargs["params"]["hours"] == 48

    def test_vm_reset_password(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "reset-password", "vm-1",
                                     "--username", "root", "--new-password", "newpass123"])
        assert result.exit_code == 0

    def test_vm_reset_network(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "reset-network", "vm-1"])
        assert result.exit_code == 0

    def test_vm_reinstall_confirm(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "reinstall", "vm-1",
                                     "--os-template-id", "os-1",
                                     "--root-password", "pass123"],
                               input="y\n")
        assert result.exit_code == 0

    def test_vm_reinstall_cancel(self, runner, mock_api):
        result = runner.invoke(cli, ["vm", "reinstall", "vm-1",
                                     "--os-template-id", "os-1",
                                     "--root-password", "pass123"],
                               input="n\n")
        assert "Cancelled" in result.output


# ─── Firewall ───

class TestFirewall:
    def test_fw_list(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": {"rules": [{"type": "in", "action": "ACCEPT", "proto": "tcp", "dport": "80"}]}
        })
        result = runner.invoke(cli, ["firewall", "list", "vm-1"])
        assert result.exit_code == 0

    def test_fw_add(self, runner, mock_api):
        result = runner.invoke(cli, ["firewall", "add", "vm-1",
                                     "--type", "in", "--action", "ACCEPT",
                                     "--proto", "tcp", "--dport", "80"])
        assert result.exit_code == 0
        _, kwargs = mock_api.call_args
        assert kwargs["json"]["type"] == "in"
        assert kwargs["json"]["action"] == "ACCEPT"

    def test_fw_delete(self, runner, mock_api):
        result = runner.invoke(cli, ["firewall", "delete", "vm-1", "0"], input="y\n")
        assert result.exit_code == 0
        args, _ = mock_api.call_args
        assert "/firewall/0" in args[1]

    def test_fw_options(self, runner, mock_api):
        result = runner.invoke(cli, ["firewall", "options", "vm-1",
                                     "--enable", "--policy-in", "DROP"])
        assert result.exit_code == 0
        _, kwargs = mock_api.call_args
        assert kwargs["json"]["enable"] == 1
        assert kwargs["json"]["policy_in"] == "DROP"

    def test_fw_options_empty(self, runner, mock_api):
        result = runner.invoke(cli, ["firewall", "options", "vm-1"])
        assert "No options to update" in result.output


# ─── Snapshot ───

class TestSnapshot:
    def test_snap_list(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": {"snapshots": [{"id": "s1", "description": "test", "createdAt": "2024-01-01"}]}
        })
        result = runner.invoke(cli, ["snapshot", "list", "vm-1"])
        assert result.exit_code == 0

    def test_snap_create(self, runner, mock_api):
        result = runner.invoke(cli, ["snapshot", "create", "vm-1", "--description", "before update"])
        assert result.exit_code == 0

    def test_snap_delete_confirm(self, runner, mock_api):
        result = runner.invoke(cli, ["snapshot", "delete", "vm-1", "snap-1"], input="y\n")
        assert result.exit_code == 0

    def test_snap_rollback_confirm(self, runner, mock_api):
        result = runner.invoke(cli, ["snapshot", "rollback", "vm-1", "snap-1"], input="y\n")
        assert result.exit_code == 0

    def test_snap_sync(self, runner, mock_api):
        result = runner.invoke(cli, ["snapshot", "sync", "vm-1"])
        assert result.exit_code == 0


# ─── Hosting ───

class TestHosting:
    def test_hosting_plans(self, runner, mock_api):
        result = runner.invoke(cli, ["hosting", "plans"])
        assert result.exit_code == 0

    def test_hosting_nodes(self, runner, mock_api):
        result = runner.invoke(cli, ["hosting", "nodes"])
        assert result.exit_code == 0

    def test_hosting_list(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": [{"id": "h1", "name": "test", "domain": "example.com", "status": "active"}]
        })
        result = runner.invoke(cli, ["hosting", "list"])
        assert result.exit_code == 0

    def test_hosting_get(self, runner, mock_api):
        result = runner.invoke(cli, ["hosting", "get", "h1"])
        assert result.exit_code == 0

    def test_hosting_delete_confirm(self, runner, mock_api):
        result = runner.invoke(cli, ["hosting", "delete", "h1"], input="y\n")
        assert result.exit_code == 0

    def test_hosting_login_url(self, runner, mock_api):
        mock_api.return_value = make_response({"data": {"loginUrl": "https://example.com/login"}})
        result = runner.invoke(cli, ["hosting", "login-url", "h1"])
        assert result.exit_code == 0

    def test_hosting_billing(self, runner, mock_api):
        result = runner.invoke(cli, ["hosting", "billing", "h1"])
        assert result.exit_code == 0

    def test_hosting_renew(self, runner, mock_api):
        result = runner.invoke(cli, ["hosting", "renew", "h1", "--billing-type", "monthly"])
        assert result.exit_code == 0


# ─── Wallet ───

class TestWallet:
    def test_wallet_balance(self, runner, mock_api):
        mock_api.return_value = make_response({"data": {"balance": 1000.50}})
        result = runner.invoke(cli, ["wallet", "balance"])
        assert result.exit_code == 0

    def test_wallet_transactions(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": [{"id": "t1", "type": "topup", "amount": 100, "createdAt": "2024-01-01"}]
        })
        result = runner.invoke(cli, ["wallet", "transactions"])
        assert result.exit_code == 0

    def test_wallet_topup(self, runner, mock_api):
        result = runner.invoke(cli, ["wallet", "topup", "--amount", "100", "--reference", "REF123"])
        assert result.exit_code == 0
        _, kwargs = mock_api.call_args
        assert kwargs["json"]["amount"] == 100.0
        assert kwargs["json"]["reference"] == "REF123"

    def test_wallet_topup_interactive(self, runner, mock_api):
        result = runner.invoke(cli, ["wallet", "topup"], input="500\nTRF456\n")
        assert result.exit_code == 0


# ─── Billing ───

class TestBilling:
    def test_billing_show(self, runner, mock_api):
        result = runner.invoke(cli, ["billing", "show", "vm-1"])
        assert result.exit_code == 0

    def test_billing_renew(self, runner, mock_api):
        result = runner.invoke(cli, ["billing", "renew", "vm-1", "--billing-type", "monthly"])
        assert result.exit_code == 0

    def test_billing_auto_renew_enable(self, runner, mock_api):
        result = runner.invoke(cli, ["billing", "auto-renew", "vm-1", "--enable"])
        assert result.exit_code == 0
        _, kwargs = mock_api.call_args
        assert kwargs["json"]["autoRenew"] is True


# ─── rDNS ───

class TestRDNS:
    def test_rdns_get(self, runner, mock_api):
        result = runner.invoke(cli, ["rdns", "get", "vm-1"])
        assert result.exit_code == 0

    def test_rdns_set(self, runner, mock_api):
        result = runner.invoke(cli, ["rdns", "set", "vm-1", "--hostname", "mail.example.com"])
        assert result.exit_code == 0
        _, kwargs = mock_api.call_args
        assert kwargs["json"]["hostname"] == "mail.example.com"

    def test_rdns_delete(self, runner, mock_api):
        result = runner.invoke(cli, ["rdns", "delete", "vm-1"], input="y\n")
        assert result.exit_code == 0


# ─── Rescue ───

class TestRescue:
    def test_rescue_enable(self, runner, mock_api):
        result = runner.invoke(cli, ["rescue", "enable", "vm-1"])
        assert result.exit_code == 0
        args, _ = mock_api.call_args
        assert "/rescue/enable" in args[1]

    def test_rescue_disable(self, runner, mock_api):
        result = runner.invoke(cli, ["rescue", "disable", "vm-1"])
        assert result.exit_code == 0


# ─── Guest Agent ───

class TestAgent:
    def test_agent_enable(self, runner, mock_api):
        result = runner.invoke(cli, ["agent", "enable", "vm-1"])
        assert result.exit_code == 0

    def test_agent_info(self, runner, mock_api):
        result = runner.invoke(cli, ["agent", "info", "vm-1"])
        assert result.exit_code == 0

    def test_agent_fstrim(self, runner, mock_api):
        result = runner.invoke(cli, ["agent", "fstrim", "vm-1"])
        assert result.exit_code == 0


# ─── SSH Keys ───

class TestSSHKeys:
    def test_sshkey_list(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": [{"id": "k1", "name": "my-key", "fingerprint": "SHA256:..."}]
        })
        result = runner.invoke(cli, ["ssh-key", "list"])
        assert result.exit_code == 0

    def test_sshkey_add(self, runner, mock_api):
        result = runner.invoke(cli, ["ssh-key", "add", "--name", "my-key",
                                     "--public-key", "ssh-rsa AAAA..."])
        assert result.exit_code == 0

    def test_sshkey_add_file(self, runner, mock_api, tmp_path):
        key_file = tmp_path / "id_rsa.pub"
        key_file.write_text("ssh-rsa AAAA... test@host")
        result = runner.invoke(cli, ["ssh-key", "add-file", "--name", "my-key",
                                     "--file", str(key_file)])
        assert result.exit_code == 0

    def test_sshkey_delete(self, runner, mock_api):
        result = runner.invoke(cli, ["ssh-key", "delete", "k1"], input="y\n")
        assert result.exit_code == 0


# ─── API Keys ───

class TestAPIKeys:
    def test_apikey_list(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": [{"id": "ak1", "name": "test", "prefix": "cit_", "createdAt": "2024-01-01"}]
        })
        result = runner.invoke(cli, ["api-key", "list"])
        assert result.exit_code == 0

    def test_apikey_create(self, runner, mock_api):
        mock_api.return_value = make_response({"data": {"key": "cit_abcdef123456"}})
        result = runner.invoke(cli, ["api-key", "create", "--name", "test-key"])
        assert result.exit_code == 0
        assert "cit_abcdef123456" in result.output

    def test_apikey_revoke(self, runner, mock_api):
        result = runner.invoke(cli, ["api-key", "revoke", "ak1", "--yes"])
        assert result.exit_code == 0


# ─── 2FA ───

class TestSecurity:
    def test_2fa_status(self, runner, mock_api):
        result = runner.invoke(cli, ["2fa", "status"])
        assert result.exit_code == 0

    def test_2fa_setup(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": {"secret": "BASE32SECRET", "otpauthUrl": "otpauth://totp/..."}
        })
        result = runner.invoke(cli, ["2fa", "setup"])
        assert result.exit_code == 0
        assert "BASE32SECRET" in result.output

    def test_2fa_verify(self, runner, mock_api):
        result = runner.invoke(cli, ["2fa", "verify", "--code", "123456"])
        assert result.exit_code == 0
        assert "2FA activated" in result.output

    def test_2fa_disable(self, runner, mock_api):
        result = runner.invoke(cli, ["2fa", "disable", "--code", "123456"])
        assert result.exit_code == 0
        assert "2FA disabled" in result.output


# ─── Tickets ───

class TestTickets:
    def test_ticket_list(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": [{"id": "t1", "subject": "Help", "status": "open", "createdAt": "2024-01-01"}]
        })
        result = runner.invoke(cli, ["ticket", "list"])
        assert result.exit_code == 0

    def test_ticket_get(self, runner, mock_api):
        result = runner.invoke(cli, ["ticket", "get", "t1"])
        assert result.exit_code == 0

    def test_ticket_create(self, runner, mock_api):
        result = runner.invoke(cli, ["ticket", "create",
                                     "--subject", "Help",
                                     "--body", "I need help"])
        assert result.exit_code == 0

    def test_ticket_create_interactive(self, runner, mock_api):
        result = runner.invoke(cli, ["ticket", "create"], input="Help\nI need help\n")
        assert result.exit_code == 0

    def test_ticket_reply(self, runner, mock_api):
        result = runner.invoke(cli, ["ticket", "reply", "t1", "--body", "Thanks"])
        assert result.exit_code == 0

    def test_ticket_reply_interactive(self, runner, mock_api):
        result = runner.invoke(cli, ["ticket", "reply", "t1"], input="Thanks\n")
        assert result.exit_code == 0

    def test_ticket_close(self, runner, mock_api):
        result = runner.invoke(cli, ["ticket", "close", "t1"])
        assert result.exit_code == 0


# ─── Referral ───

class TestReferral:
    def test_referral_code(self, runner, mock_api):
        result = runner.invoke(cli, ["referral", "code"])
        assert result.exit_code == 0

    def test_referral_stats(self, runner, mock_api):
        result = runner.invoke(cli, ["referral", "stats"])
        assert result.exit_code == 0

    def test_referral_check(self, runner, mock_api):
        result = runner.invoke(cli, ["referral", "check", "ABC123"])
        assert result.exit_code == 0


# ─── Activity ───

class TestActivity:
    def test_activity_list(self, runner, mock_api):
        mock_api.return_value = make_response({
            "data": [{"action": "login", "description": "Logged in", "ip": "1.2.3.4", "createdAt": "2024-01-01"}]
        })
        result = runner.invoke(cli, ["activity"])
        assert result.exit_code == 0


# ─── Nodes ───

class TestNodes:
    def test_node_list(self, runner, mock_api):
        result = runner.invoke(cli, ["node", "list"])
        assert result.exit_code == 0

    def test_node_hardware(self, runner, mock_api):
        result = runner.invoke(cli, ["node", "hardware", "node-1"])
        assert result.exit_code == 0


# ─── Test API ───

class TestTestApi:
    def test_test_api_public(self, runner, mock_api):
        result = runner.invoke(cli, ["test-api"])
        assert result.exit_code == 0
        assert "API Connectivity Test" in result.output

    def test_test_api_all(self, runner, mock_api):
        result = runner.invoke(cli, ["test-api", "--all"])
        assert result.exit_code == 0

    def test_test_api_verbose(self, runner, mock_api):
        result = runner.invoke(cli, ["test-api", "-v"])
        assert result.exit_code == 0


# ─── Plans ───

class TestPlans:
    def test_plans_vm(self, runner, mock_api):
        result = runner.invoke(cli, ["plan", "vm"])
        assert result.exit_code == 0

    def test_plans_vm_with_node(self, runner, mock_api):
        result = runner.invoke(cli, ["plan", "vm", "--node-id", "n1"])
        assert result.exit_code == 0
        _, kwargs = mock_api.call_args
        assert kwargs["params"]["nodeId"] == "n1"

    def test_plans_os(self, runner, mock_api):
        result = runner.invoke(cli, ["plan", "os"])
        assert result.exit_code == 0

    def test_plans_dedicated(self, runner, mock_api):
        result = runner.invoke(cli, ["plan", "dedicated"])
        assert result.exit_code == 0

    def test_plans_colocation(self, runner, mock_api):
        result = runner.invoke(cli, ["plan", "colocation"])
        assert result.exit_code == 0


# ─── System ───

class TestSystem:
    def test_system_status(self, runner, mock_api):
        result = runner.invoke(cli, ["system", "status"])
        assert result.exit_code == 0

    def test_system_plans(self, runner, mock_api):
        result = runner.invoke(cli, ["system", "plans"])
        assert result.exit_code == 0

    def test_system_nodes(self, runner, mock_api):
        result = runner.invoke(cli, ["system", "nodes"])
        assert result.exit_code == 0


# ─── Config ───

class TestConfig:
    def test_config_show(self, runner):
        with patch("craft.cli.load_config", return_value={
            "base_url": "https://api.test.com",
            "access_token": "cit_test1234567890",
        }):
            result = runner.invoke(cli, ["config", "--show"])
            assert "Base URL" in result.output
            assert "****" in result.output

    def test_config_set_token(self, runner):
        with patch("craft.cli.load_config", return_value={}), \
             patch("craft.cli.save_config") as mock_save:
            result = runner.invoke(cli, ["config", "--token", "new-token"])
            assert "Config updated" in result.output

    def test_config_set_base_url(self, runner):
        with patch("craft.cli.load_config", return_value={}), \
             patch("craft.cli.save_config") as mock_save:
            result = runner.invoke(cli, ["config", "--base-url", "https://new.api.com"])
            assert "Config updated" in result.output


# ─── Version ───

class TestVersion:
    def test_version_cmd(self, runner):
        with patch("subprocess.run"):
            result = runner.invoke(cli, ["version"])
            assert "craft-cli" in result.output
