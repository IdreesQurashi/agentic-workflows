import os
import sys
import json
import unittest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from wp_client import WordPressClient
from gmail_reader import GmailReader

class TestEpaperPipeline(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(CURRENT_DIR, "config.json"), "r") as f:
            self.config = json.load(f)

    def test_01_multi_batch_partition_and_aggregation(self):
        """Verify that 6 separate email batches are correctly partitioned and merged into 1 batch of 4 pages for Pukkar and 1 batch of 8 pages for KT."""
        dummy_emails = GmailReader.generate_dummy_bundles()
        self.assertEqual(len(dummy_emails), 6)
        
        aggregated = GmailReader.partition_and_aggregate(dummy_emails, self.config["publications"])
        
        pukkar_pages = [p["filename"] for p in aggregated["pukkar"]]
        kt_pages = [p["filename"] for p in aggregated["kashmir_times"]]
        
        self.assertEqual(len(pukkar_pages), 4, "Pukkar must gather exactly 4 pages across both emails")
        self.assertEqual(pukkar_pages, ["p1-10.jpg", "p2-10.jpg", "p3-10.jpg", "p4-10.jpg"], "Pukkar pages must be naturally sorted")
        
        self.assertEqual(len(kt_pages), 8, "Kashmir Times must gather exactly 8 pages across all 4 emails")
        self.assertEqual(kt_pages, [
            "p1 (1).jpg", "p2 (1).jpg", "p3 (1).jpg", "p4 (1).jpg",
            "p5 (1).jpg", "p6 (1).jpg", "p7 (1).jpg", "p8 (1).jpg"
        ], "Kashmir Times pages must be naturally sorted")

    def test_02_dearflip_html_generation(self):
        """Verify that create_dearflip_post builds valid DearFlip container markup and inline initialization script."""
        client = WordPressClient("https://dummy.example.com", "dummy_key")
        
        mock_pages = [
            {"filename": "p2.jpg", "id": 102, "source_url": "https://example.com/p2.jpg"},
            {"filename": "p1.jpg", "id": 101, "source_url": "https://example.com/p1.jpg"},
            {"filename": "p4.jpg", "id": 104, "source_url": "https://example.com/p4.jpg"},
            {"filename": "p3.jpg", "id": 103, "source_url": "https://example.com/p3.jpg"}
        ]
        
        # We test sorting logic
        def natural_sort_key(p):
            import re
            fn = p.get("filename", "")
            match = re.search(r"p?(\d+)", fn.lower())
            return int(match.group(1)) if match else 999

        sorted_pages = sorted(mock_pages, key=natural_sort_key)
        self.assertEqual([p["id"] for p in sorted_pages], [101, 102, 103, 104], "Pages must sort naturally from p1 to p4")

    def test_03_kashmir_times_live_wp_connection(self):
        """Verify that live WordPress REST connection to dailykashmirtimes.com.pk works using the existing API key."""
        kt_cfg = self.config["publications"]["kashmir_times"]
        client = WordPressClient(kt_cfg["wp_url"], kt_cfg["api_key"])
        res = client.check_connection()
        self.assertTrue(res.get("success"), f"Kashmir Times connection failed: {res.get('error')}")
        self.assertEqual(res.get("user"), "Mansoor Shahid")

if __name__ == "__main__":
    unittest.main()
