# craft-cli

Command-line tool สำหรับจัดการ CraftIntertech Cloud Platform บน Linux

```
craft vm list
craft vm start my-server-id
craft wallet balance
```

## Installation

### วิธีที่ 1: One-line install (แนะนำ)

```bash
curl -fsSL https://raw.githubusercontent.com/CraftIntertech/craft-cli/main/install.sh | bash
```

หรือถ้าอยากดู script ก่อนรัน:

```bash
curl -fsSL https://raw.githubusercontent.com/CraftIntertech/craft-cli/main/install.sh -o install.sh
less install.sh        # อ่าน script
bash install.sh        # ติดตั้ง
```

### วิธีที่ 2: ติดตั้งเอง (pip)

```bash
git clone https://github.com/CraftIntertech/craft-cli.git
cd craft-cli
pip install .
```

### Requirements

- Python 3.8+
- git
- pip

## Quick Start

```bash
# เข้าสู่ระบบด้วย API key หรือ JWT token
craft login cit_your_api_key_here

# ดู VM ทั้งหมด
craft vm list

# ดูยอดเงิน
craft wallet balance
```

## Commands

### Authentication

| Command | Description |
|---|---|
| `craft login <token>` | เข้าสู่ระบบด้วย API key (`cit_...`) หรือ JWT token |
| `craft logout` | ออกจากระบบ (ลบ token) |
| `craft refresh-token` | รีเฟรช access token |
| `craft config --token <key>` | ตั้งค่า token ตรง |
| `craft config --show` | ดูการตั้งค่าปัจจุบัน |

### Profile

| Command | Description |
|---|---|
| `craft profile show` | ดูข้อมูลโปรไฟล์ |
| `craft profile update --first-name "John"` | แก้ไขโปรไฟล์ |
| `craft profile change-password` | เปลี่ยนรหัสผ่าน |

### Virtual Machines

```bash
# CRUD
craft vm list                       # ดู VM ทั้งหมด
craft vm get <vm-id>                # ดูรายละเอียด VM
craft vm create --name my-server \
  --hostname my-server.example.com \
  --node-id <uuid> \
  --os-template-id <uuid>           # สร้าง VM ใหม่
craft vm delete <vm-id>             # ลบ VM

# Power
craft vm start <vm-id>              # เปิด VM
craft vm stop <vm-id>               # ปิด VM (ACPI)
craft vm reboot <vm-id>             # รีบูท VM

# Manage
craft vm rename <vm-id> --name new-name
craft vm resize <vm-id> --plan-id <uuid>
craft vm reinstall <vm-id> --os-template-id <uuid>
craft vm reset-password <vm-id>
craft vm reset-network <vm-id>

# Monitor
craft vm status <vm-id>             # สถานะ real-time
craft vm console <vm-id>            # noVNC console
craft vm network <vm-id>            # ข้อมูล network
craft vm metrics <vm-id> --hours 24 # กราฟ performance
```

### Firewall

```bash
craft firewall list <vm-id>
craft firewall add <vm-id> --type in --action ACCEPT --proto tcp --dport 80,443
craft firewall delete <vm-id> <position>
craft firewall options <vm-id> --enable --policy-in DROP --policy-out ACCEPT
```

### Snapshots

```bash
craft snapshot list <vm-id>
craft snapshot create <vm-id> --description "Before upgrade"
craft snapshot rollback <vm-id> <snap-id>
craft snapshot delete <vm-id> <snap-id>
craft snapshot sync <vm-id>
```

### Reverse DNS

```bash
craft rdns get <vm-id>
craft rdns set <vm-id> --hostname mail.example.com
craft rdns delete <vm-id>
```

### Rescue Mode

```bash
craft rescue enable <vm-id>         # เปิด rescue mode
craft rescue disable <vm-id>        # ปิด rescue mode
```

### Guest Agent (QEMU)

```bash
craft agent enable <vm-id>
craft agent info <vm-id>
craft agent fstrim <vm-id>
```

### VM Billing

```bash
craft billing show <vm-id>
craft billing renew <vm-id> --billing-type monthly
craft billing auto-renew <vm-id> --enable
craft billing auto-renew <vm-id> --disable
```

### Web Hosting

```bash
craft hosting plans                 # ดูแพลนที่มี
craft hosting nodes                 # ดู node ที่มี
craft hosting list                  # ดู hosting ทั้งหมด
craft hosting get <id>              # ดูรายละเอียด
craft hosting create --name mysite --domain example.com \
  --node-id <uuid> --plan-id <uuid>
craft hosting delete <id>
craft hosting login-url <id>        # SSO เข้า DirectAdmin
craft hosting billing <id>
craft hosting renew <id> --billing-type monthly
craft hosting auto-renew <id> --enable
```

### Wallet

```bash
craft wallet balance                # ดูยอดเงิน
craft wallet transactions           # ดูรายการธุรกรรม
craft wallet topup --amount 1000 --reference "BANK-REF-12345"
```

### SSH Keys

```bash
craft ssh-key list
craft ssh-key add --name "My Laptop" --public-key "ssh-ed25519 AAAA..."
craft ssh-key add-file --name "My Laptop" --file ~/.ssh/id_ed25519.pub
craft ssh-key delete <key-id>
```

### API Keys

```bash
craft api-key list
craft api-key create --name "CI/CD Pipeline"  # แสดง key ครั้งเดียว!
craft api-key revoke <key-id>
```

### Two-Factor Authentication (2FA)

```bash
craft 2fa status
craft 2fa setup                     # ได้ TOTP secret + QR URL
craft 2fa verify --code 123456      # เปิดใช้งาน 2FA
craft 2fa disable --code 123456
```

### Support Tickets

```bash
craft ticket list
craft ticket get <ticket-id>
craft ticket create --subject "VM not responding" --body "Details..."
craft ticket reply <ticket-id> --body "Thank you"
craft ticket close <ticket-id>
```

### Referral Program

```bash
craft referral code                 # ดู referral code
craft referral stats                # ดูสถิติ
craft referral check ABC123         # ตรวจสอบ code (ไม่ต้อง login)
```

### Nodes & Plans

```bash
craft node list                     # ดู node ที่มี
craft node hardware <node-id>       # ดู hardware info

craft plan vm                       # ดูแพลน VM
craft plan vm --node-id <uuid>      # กรองตาม node
craft plan os                       # ดู OS templates
craft plan dedicated                # แพลน dedicated (public)
craft plan colocation               # แพลน colocation (public)
```

### System Status (ไม่ต้อง login)

```bash
craft system status                 # สถานะระบบ
craft system plans                  # แพลนสำหรับหน้าเว็บ
craft system nodes                  # node สำหรับหน้าเว็บ
```

### Activity Log

```bash
craft activity                      # ดู log การใช้งาน
craft activity --page 2 --limit 50
```

## Configuration

Config ถูกเก็บที่ `~/.config/craft/config.json`:

```json
{
  "base_url": "https://craftintertech.co.th/api/v1",
  "access_token": "...",
  "refresh_token": "..."
}
```

```bash
# เปลี่ยน API base URL
craft config --base-url https://custom.api.example.com/v1

# ตั้ง token ตรง (เช่น API key)
craft config --token cit_xxxxxxxxxxxx

# ดูการตั้งค่า
craft config --show
```

## Authentication

```bash
# ใช้ API key (สร้างได้จาก web dashboard หรือ craft api-key create)
craft login cit_xxxxxxxxxxxx

# หรือใช้ JWT token
craft login eyJhbGciOi...
```

Token ถูกเก็บที่ `~/.config/craft/config.json` (chmod 600)

## Update

```bash
# เช็ค version ปัจจุบัน + เทียบกับ latest
craft version

# อัปเดตเป็นเวอร์ชันล่าสุด
craft update
```

## Uninstall

```bash
craft uninstall
```

หรือถ้าติดตั้งด้วย pip:

```bash
pip uninstall craft-cli
```

## License

MIT
