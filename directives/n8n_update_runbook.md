# n8n Enterprise Update Runbook and Migration Protocol

## 1. System Overview and Version Gap
* Target Instance: MAK Web Hosted n8n Automation Engine
* Version Lag: 27 Releases behind Current Stable
* Target Execution Window: Sunday Night Maintenance Period
* Test Authority: n8n Instance Daily Health Monitor

## 2. Breaking Changes Matrix across the 27 Version Delta
Upgrading across 27 minor and patch releases introduces specific operational considerations:

### A. Database Schema Auto Migration
* Impact: High
* Detail: n8n utilizes TypeORM for automatic schema migrations during container bootstrap.
* Risk: If incoming webhooks or scheduled triggers fire during the migration phase, SQLite table lock errors occur.
* Action: Cease webhook traffic or disable active workflows prior to launching the upgraded container.

### B. Credential Decryption and Encryption Key Integrity
* Impact: Critical
* Detail: The environment variable N8N_ENCRYPTION_KEY must remain identical.
* Risk: If the container restarts without this exact string, every database credential becomes permanently undecryptable.
* Action: Verify N8N_ENCRYPTION_KEY exists in .env and is backed up independently before touching any container.

### C. Node Sandbox and Execution Isolation
* Impact: Medium
* Detail: Recent n8n versions enforce stricter VM isolation for Code nodes.
* Risk: Custom scripts relying on unapproved Node.js global modules throw runtime reference errors.
* Action: Ensure required packages are explicitly declared in NODE_FUNCTION_ALLOW_BUILTIN and NODE_FUNCTION_ALLOW_EXTERNAL.

### D. HTTP Request Node Versioning
* Impact: Low to Medium
* Detail: HTTP Request node engine upgrades default to strict error bubbling and JSON validation.
* Action: Verify older workflows continue executing through backward compatibility layers.

## 3. Step by Step Pre Update Snapshot Protocol (10 Minutes)
Execute these actions on the host server before updating:

1. Trigger the on demand backup workflow:
   * Open the canvas for "n8n Pre-Update Snapshot & Backup Engine".
   * Click "Test workflow" to generate the full workflow and credential name manifest.

2. Access the host server via terminal.

3. Navigate to the n8n application directory:
   cd /opt/n8n

4. Halt the container gracefully to flush memory and database buffers:
   docker compose down

5. Create a dated cold storage snapshot of the data volume:
   tar -czvf /opt/backups/n8n_backup_pre_update_$(date +%Y%m%d_%H%M%S).tar.gz -C /var/lib/docker/volumes/n8n_data/_data .

6. Duplicate configuration files:
   cp .env docker-compose.yml /opt/backups/

## 4. Container Update and Schema Migration Sequence (Sunday Night)
Execute during the agreed maintenance window:

1. Inspect docker-compose.yml and set the target image tag:
   docker.n8n.io/n8nio/n8n:latest

2. Pull the latest release image:
   docker compose pull

3. Launch the upgraded container in detached mode:
   docker compose up -d

4. Stream live logs to verify database migration completion:
   docker compose logs -f n8n

5. Confirm log output states:
   "Migrations completed successfully"
   "Editor is now accessible via..."

## 5. Post Update Verification via Health Monitor
Validate instance health immediately after container startup:

1. Navigate to the web editor interface.
2. Open the "n8n Daily Instance Health Monitor" workflow.
3. Click "Test workflow" manually.
4. Verify execution metrics:
   * Node 3A (Fetch Workflows): Returns 200 OK with identical workflow count.
   * Node 3B (Fetch 24h Executions): Returns 200 OK without API schema validation errors.
   * Node 4 (Aggregate Metrics & Format HTML): Produces clean success calculations.
   * Node 5 (Check If Failures Exist): Routes to clean status branch.
5. Trigger one test webhook to verify live execution scheduling.

## 6. Rollback Protocol (Under 3 Minutes)
If migration fails, database locks, or credential decryption fails:

1. Stop the failing container immediately:
   docker compose down

2. Revert docker-compose.yml to the previous working image tag.

3. Restore database storage from the pre update cold snapshot:
   rm -rf /var/lib/docker/volumes/n8n_data/_data/*
   tar -xzvf /opt/backups/n8n_backup_pre_update_[TIMESTAMP].tar.gz -C /var/lib/docker/volumes/n8n_data/_data/

4. Restart the previous container version:
   docker compose up -d

5. Run the Health Monitor workflow to confirm 100% operational restoration.
