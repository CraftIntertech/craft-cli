# Changelog

## v1.3.0 (2026-03-28)

### New Features
- **`craft test-api`** — ทดสอบ API connectivity ทุก endpoint (public + authenticated)
- **Status สี** — running/active = เขียว, stopped/error = แดง, pending = เหลือง ในตารางและ item display
- **Pagination info** — แสดง "Page X of Y (N total)" ท้ายทุก list command
- **Interactive tickets** — `ticket create/reply` ไม่ต้องใส่ flag ก็ได้ จะ prompt ถามให้
- **Interactive wallet topup** — `wallet topup` ไม่ต้องใส่ flag ก็ได้ จะ prompt ถามให้

### Improvements
- **ตารางแทน JSON** — `node list`, `plan vm/os/dedicated/colocation`, `hosting plans/nodes`, `system plans/nodes` แสดงตารางสวยแทน raw JSON
- **Confirmation prompts** — เพิ่มถามยืนยันก่อนลบ firewall rule, SSH key, rDNS record
- **Interactive node hardware** — `node hardware` เลือก node จาก list ได้ถ้าไม่ใส่ ID
- **Help text** — ปรับคำอธิบาย CLI ให้ดีขึ้น มี quick start + examples

### Testing
- เพิ่ม **144 unit tests** ครอบคลุมทุก API endpoint, client layer, config, output formatting
- เพิ่ม pytest config ใน `pyproject.toml`

---

## v1.2.0 (2026-03-28)

### New Features
- **Node hardware info** — เลือก node แล้วแสดง CPU model, cores, RAM จาก `/nodes/:id/hardware`
- **Plan pricing** — เลือก plan แสดงราคาทุก billing type (daily/weekly/monthly/yearly)
- **Billing type with price** — เลือก billing type แสดงราคาตาม plan ที่เลือก
- **Summary with price** — สรุปแสดง plan specs + ราคาก่อนยืนยันสร้าง VM

### Bug Fixes
- เพิ่ม timeout เป็น 120s สำหรับ VM power ops (start/stop/reboot/create) แก้ Cloudflare 502
- แก้ error messages แสดงข้อมูลจาก API ครบ + hints สำหรับ HTTP status codes
- แก้ output formatting flatten nested objects, boolean แสดงเป็น Yes/No

---

## v1.1.0 (2026-03-28)

### New Features
- **Interactive mode** — ทุกคำสั่งที่ต้องใส่ ID สามารถเลือกจาก list ได้ (arrow keys + fuzzy search)
- `craft vm create` wizard — เลือก node → OS → plan/custom specs → billing → SSH keys
- `craft hosting create` wizard — เลือก node → plan → billing
- `craft firewall add` — เลือก direction/action/protocol แบบ interactive
- VM commands (start/stop/reboot/delete/status) — เลือก VM จาก list ถ้าไม่ใส่ ID
- Snapshot, rDNS, rescue, agent, billing — ทุกตัวรองรับ interactive

### Other
- `craft update` / `craft uninstall` — จัดการ CLI ได้จากตัว CLI เอง
- `craft version` — เช็ค version + เทียบกับ latest บน GitHub
- Version file (`VERSION`) เป็น single source of truth
- `craft login <token>` — ใช้ token/API key ตรง (เอา register ออก)

---

## v1.0.0 (2026-03-28)

### Initial Release
CLI tool สำหรับ CraftIntertech Cloud Platform ครอบคลุมทุก API:

- **Authentication** — login, logout, refresh token, config
- **VM Management** — create, delete, start, stop, reboot, rename, resize, reinstall, console, metrics
- **Firewall** — list, add, delete rules, update options
- **Snapshots** — create, delete, rollback, sync (max 5 per VM)
- **Reverse DNS** — get, set, delete PTR records
- **Rescue Mode** — enable/disable rescue boot
- **Guest Agent** — enable, info, fstrim
- **VM Billing** — show, renew, auto-renew toggle
- **Web Hosting** — create, delete, SSO login, billing, plans
- **Wallet** — balance, transactions, top-up
- **SSH Keys** — list, add, add from file, delete
- **API Keys** — list, create, revoke
- **2FA** — status, setup, verify, disable
- **Support Tickets** — list, get, create, reply, close
- **Referral** — code, stats, validate
- **Nodes & Plans** — list nodes, hardware info, VM/OS/dedicated/colocation plans
- **System Status** — public status, plans, nodes (no auth)
- **Activity Log** — account activity with pagination

### Install
```bash
curl -fsSL https://raw.githubusercontent.com/CraftIntertech/craft-cli/main/install.sh | bash
```
