# Antigravity E Paper Auto Publisher

Standalone, fully portable automation engine for daily e paper publishing. Eliminates all third party SaaS limits, monthly subscription fees, and data transfer caps.

***

## How To Export To Any Other PC

This package has zero workspace dependencies and runs on any PC running Linux, macOS, or Windows with Python 3.8+.

### Step 1: Copy Folder
Copy the entire `epaper_autopublisher/` folder to the target computer.

### Step 2: Install Minimal Requirements
```bash
pip install -r requirements.txt
```

### Step 3: Configure Credentials
Copy `config.example.json` to `config.json` and fill in:
1. Gmail App Password for `n.maloom557@gmail.com`.
2. Make Connector API Key for Daily Pukkar e Azadi (`dailypukkareazadi.com`).
3. Kashmir Times key is already pre populated.

### Step 4: Verify Handshake
```bash
python3 publisher.py --test-wp
```

### Step 5: Test With Dummy Data
```bash
python3 publisher.py --test-dummy --dry-run
```

***

## Daily Automated Scheduling

### Option A: Local Linux Cron (Recommended)
Add this entry to your crontab (`crontab -e`) to trigger automatically at 02:00 AM PKT (21:00 UTC):
```bash
0 2 * * * cd /path/to/epaper_autopublisher && python3 publisher.py --live >> publisher.log 2>&1
```

### Option B: Antigravity Slash Command
Run `/schedule` inside Antigravity:
* Cron Expression: `0 2 * * *`
* Prompt: `Run python3 execution/epaper_autopublisher/publisher.py --live`

***

## Architecture Features
* **Multi Email Batch Merging**: Combines separate email batches (e.g. 2 emails of 2 pages each for Pukkar, 4 emails of 2 pages each for Kashmir Times) into strictly ONE post per newspaper.
* **Natural Page Ordering**: Automatically detects page numbers and sorts images ascending (`p1`, `p2`, `p3`, ...).
* **Native Flipbook Viewer**: Generates the exact DearFlip HTML block and inline initialization script in Category 42.
* **Deterministic Guard**: Ensures that if a newspaper receives zero emails in a run, zero empty posts are created.
