import copy
import hashlib
import json
from pathlib import Path
import unittest

from verbatim_texts import validate_document


class VerbatimTextTests(unittest.TestCase):
    def document(self):
        # Original test text, not a third-party or investor transcript.
        original = "First sentence.\nSecond sentence!\n"
        return {"kind": "verbatim_text", "workId": "test-original", "originalLanguage": "en",
                "originalText": original, "sourceDigest": hashlib.sha256(original.encode()).hexdigest(),
                "reviewStatus": "verified",
                "rights": {"basis": "user_provided", "verified": True, "allowPublication": True,
                           "allowTranslation": True, "evidence": "Original text written for this test"},
                "segments": [{"id": "s1", "original": "First sentence.\n", "en": "First sentence.\n", "zh": "第一句。\n"},
                             {"id": "s2", "original": "Second sentence!\n", "en": "Second sentence!\n", "zh": "第二句！\n"}]}

    def test_complete_sentence_alignment_and_original_whitespace(self):
        self.assertTrue(validate_document(self.document(), "test-original"))

    def test_missing_reordered_and_duplicated_sentences_are_rejected(self):
        for change in [lambda s: s.pop(), lambda s: s.reverse(), lambda s: s.append(copy.deepcopy(s[0]))]:
            d = self.document()
            change(d["segments"])
            with self.assertRaises(ValueError):
                validate_document(d, "test-original")

    def test_rewritten_original_missing_translation_and_changed_digest_are_rejected(self):
        for field in ["en", "zh"]:
            d = self.document()
            d["segments"][0][field] = "" if field == "zh" else "A summary of the first sentence."
            with self.assertRaises(ValueError):
                validate_document(d, "test-original")
        d = self.document()
        d["sourceDigest"] = "wrong"
        with self.assertRaises(ValueError):
            validate_document(d, "test-original")

    def test_original_chinese_without_invented_translation(self):
        d = self.document()
        d["originalLanguage"], d["languages"] = "zh", ["zh"]
        for segment in d["segments"]:
            segment["zh"] = segment["original"]
            del segment["en"]
        self.assertTrue(validate_document(d, "test-original"))

    def test_public_link_alone_is_not_publication_permission(self):
        d = self.document()
        d["rights"] = {"evidence": "https://publisher.example/free-video"}
        with self.assertRaises(ValueError):
            validate_document(d, "test-original")

    def test_summary_and_unreviewed_asr_are_not_complete_verified_texts(self):
        d = self.document()
        d["chapters"] = [{"heading": "Summary"}]
        with self.assertRaises(ValueError):
            validate_document(d, "test-original")
        d = self.document()
        d["reviewStatus"] = "unreviewed_asr"
        with self.assertRaises(ValueError):
            validate_document(d, "test-original")


class CompletedReportPublicationTests(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]

    def test_second_batch_preserves_all_pages_tables_rows_and_images(self):
        manifest = json.loads((self.root / "archive/imports/2026-10-29-batch2.json").read_text())
        self.assertEqual(len(manifest["works"]), 8)
        self.assertEqual(sum(w["pages"] or 0 for w in manifest["works"]), 158)
        tables = rows = images = 0
        for work in manifest["works"]:
            d = json.loads((self.root / work["file"]).read_text())
            validate_document(d, work["workId"])
            self.assertEqual(d["sourceDigest"], work["originalSHA256"])
            if work["pages"]:
                self.assertEqual([s["page"] for s in d["segments"]], list(range(1,work["pages"]+1)))
            if d.get("sourceRawText"):
                self.assertEqual(hashlib.sha256(d["sourceRawText"].encode()).hexdigest(), d["sourceRawTextDigest"])
            for seg in d["segments"]:
                for block in seg["zhBlocks"]:
                    if block["type"] == "table":
                        tables += 1
                        rows += len(block["rows"])
                        self.assertTrue(all(len(r)==len(block["headers"]) for r in block["rows"]))
                    elif block["type"] == "figure":
                        images += 1
                        self.assertEqual(hashlib.sha256((self.root/block["src"]).read_bytes()).hexdigest(),block["sha256"])
        self.assertEqual((tables, rows, images), (67, 821, 6))

    def test_independent_authors_and_report_periods_remain_distinct(self):
        manifest = json.loads((self.root / "archive/imports/2026-10-29-batch2.json").read_text())
        docs={w["key"]:json.loads((self.root/w["file"]).read_text()) for w in manifest["works"]}
        d=docs["buffett2014"]
        self.assertEqual(d["authors"], ["Warren E. Buffett", "Charles T. Munger"])
        self.assertTrue(all(s["author"]=="Charles T. Munger" for s in d["segments"] if s["page"]>=38))
        self.assertTrue(all(s["author"]=="Warren E. Buffett" for s in d["segments"] if s["page"]<38))
        self.assertTrue({"Bruce R. Berkowitz","Peter A. Russ","Lawrence S. Pitkowsky","Keith D. Trauner"} <= set(docs["fairholme2001"]["authors"]))
        for year, manager, financial in [("2022","2022-12-31","2022-11-30"),("2023","2023-06-30","2023-05-31")]:
            periods=docs["fairholme"+year]["reportPeriods"]
            self.assertEqual(periods["manager_report_period_end"],manager)
            self.assertEqual(periods["formal_financial_report_period_end"],financial)


if __name__ == "__main__":
    unittest.main()
