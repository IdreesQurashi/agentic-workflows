---
name: epaper_autopublisher
description: Execution protocol and standalone engine for daily e paper multi batch ingestion, DearFlip post creation, and automated publishing for Daily Pukkar e Azadi and Daily Kashmir Times.
---

# E Paper Auto Publisher Protocol

Autonomous engine for ingesting daily newspaper scans, resolving multi email batch splits, and publishing single unified editions with DearFlip book layout on WordPress.

## 1. Engine Location and Structure
The engine lives in `execution/epaper_autopublisher/` and contains:
* `config.json`: Live endpoints, credentials, and category settings.
* `config.example.json`: Portable template for zero workspace setup on new PCs.
* `publisher.py`: Master CLI orchestrator.
* `gmail_reader.py`: Secure IMAP reader with automatic multi email batch merging and natural page sorting.
* `wp_client.py`: WordPress REST API client handling media uploads and DearFlip post publishing.
* `test_pipeline.py`: Automated unit test suite verifying batch aggregation and sorting.

## 2. Invariants
* **Single Post Guarantee**: Never create multiple posts for a single newspaper issue. All separate email batches (e.g. 2 emails of 2 pages for Pukkar, 4 emails of 2 pages for Kashmir Times) must be aggregated into exactly one post containing all pages.
* **Natural Page Sorting**: Always sort pages ascending (`p1`, `p2`, `p3`, ...). Page 1 is strictly assigned as the featured media and book cover.
* **Zero SaaS Dependence**: Runs completely locally. Eliminates Make.com data transfer caps, monthly fees, and third party limits.
* **Strict Category Assignment**: All daily edition posts must be published in Category 42 (روز نامہ ای نیوز پیپر) with status set to `publish`.

## 3. Operational Commands
* Test WordPress connections: `python3 execution/epaper_autopublisher/publisher.py --test-wp`
* Test with dummy multi batch data: `python3 execution/epaper_autopublisher/publisher.py --test-dummy --dry-run`
* Run automated test suite: `python3 execution/epaper_autopublisher/test_pipeline.py`
* Execute live publishing run: `python3 execution/epaper_autopublisher/publisher.py --live`
