"""
Integration tests for the full Analytics & Export Pipeline.
"""

import unittest
from src.analytics.pipeline import AnalyticsPipeline
from src.dashboard.export_pipeline import ExportPipeline
from src.dashboard.sheets_sync import GoogleSheetsSync


class TestFullPipeline(unittest.TestCase):
    def test_full_pipeline_run_and_export(self):
        # 1. Run Analytics Pipeline
        pipeline = AnalyticsPipeline()
        master_df = pipeline.run()

        self.assertGreater(len(master_df), 0)
        self.assertIn("composite_score", master_df.columns)
        self.assertIn("vorp", master_df.columns)
        self.assertIn("adp_delta_consensus", master_df.columns)

        # 2. Test Export Pipeline
        exporter = ExportPipeline()
        outputs = exporter.export(master_df)

        self.assertIn("csv", outputs)
        self.assertTrue(outputs["csv"].exists())
        self.assertIn("sqlite", outputs)
        self.assertTrue(outputs["sqlite"].exists())
        self.assertIn("summary", outputs)
        self.assertTrue(outputs["summary"].exists())

        # 3. Test Google Sheets Sync (Dry Run)
        sheets_sync = GoogleSheetsSync()
        sync_res = sheets_sync.sync(master_df, dry_run=True)
        self.assertEqual(sync_res.get("status"), "dry_run_verified")


if __name__ == "__main__":
    unittest.main()
