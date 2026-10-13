import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import speech_archive as archive


class SpeechArchiveTests(unittest.TestCase):
    def work(self, title="Lecture at Columbia on April 23, 2015", url="https://publisher.example/talk"):
        return archive.make_work("lilu", title, url, "Publisher", "https://publisher.example/archive")

    def test_source_index_does_not_merge_distinct_works(self):
        a = self.work()
        b = self.work("Different lecture on April 23, 2015", "https://publisher.example/other")
        merged = archive.merge_works([a], [b])
        self.assertEqual(len(merged), 2)

    def test_editions_of_one_event_merge_sources_and_keep_editorial(self):
        old = self.work()
        old["noteFile"] = "archive/notes/lilu-verified.json"
        old["title"]["zh"] = "已核对的中文题目"
        new = self.work(url="https://publisher.example/talk.pdf")
        merged = archive.merge_works([old], [new])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["noteFile"], old["noteFile"])
        self.assertEqual(merged[0]["title"]["zh"], old["title"]["zh"])
        self.assertEqual(len(merged[0]["sources"]), 3)

    def test_url_normalisation_removes_tracking_not_episode(self):
        self.assertEqual(archive.canonical("https://www.youtube.com/watch?v=abcdefghijk&utm_source=x"),
                         archive.canonical("https://youtu.be/abcdefghijk"))
        self.assertNotEqual(archive.canonical("https://publisher.example/?episode=1"),
                            archive.canonical("https://publisher.example/?episode=2"))

    def test_same_source_never_merges_different_people(self):
        a = self.work()
        b = self.work()
        b["investor"], b["id"] = "pabrai", "pabrai-another"
        self.assertEqual(len(archive.merge_works([a], [b])), 2)

    def test_event_date_does_not_use_filename_publication_date(self):
        self.assertEqual(archive.event_date("Interview on December 25, 2025 Transcript"), "2025-12-25")
        self.assertEqual(archive.event_date("Lecture in June 2014"), "2014-06")
        self.assertIsNone(archive.event_date("A discussion with a business owner"))

    def test_bilingual_validation_rejects_missing_translation_and_invented_number(self):
        text = "The company has an operating history. " * 8
        chunks = [{"id": "s0", "text": text}]
        pair = {"zh": "研究企业要先确定经营特征，再理解它面临的竞争，以及哪些条件可能发生改变。" * 2,
                "en": "Understand a business before comparing its price with value."}
        note = {"lead": pair, "chapters": [{"heading": {"zh": "研究", "en": "Research"},
                                          "paragraphs": [pair], "evidenceIds": ["s0"]} for _ in range(3)]}
        self.assertTrue(archive.validate_note(note, chunks))
        bad = copy.deepcopy(note)
        bad["chapters"][1]["paragraphs"][0]["en"] = ""
        with self.assertRaises(ValueError):
            archive.validate_note(bad, chunks)
        bad = copy.deepcopy(note)
        bad["lead"]["en"] += " It returned 999%."
        with self.assertRaises(ValueError):
            archive.validate_note(bad, chunks)

    def test_invalid_evidence_is_rejected(self):
        pair = {"zh": "研究", "en": "Research"}
        note = {"lead": pair, "chapters": [{"heading": pair, "paragraphs": [pair], "evidenceIds": ["invented"]}]*3}
        with self.assertRaises(ValueError):
            archive.validate_note(note, [{"id": "s0", "text": "Source text"}])

    def test_caption_parser_removes_adjacent_rolling_duplicates(self):
        vtt = b"WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nHello there\n\n00:00:02.000 --> 00:00:03.000\nHello there\n\n00:00:03.000 --> 00:00:04.000\nA new line\n"
        self.assertEqual(archive.parse_captions(vtt), "Hello there\nA new line")

    def test_source_passages_preserve_reasoning_not_pdf_line_fragments(self):
        footer = "This transcript is provided for educational purposes only."
        text = ("Page 1 of 3\n" + "An investor first studies the economics of a business,\nthen evaluates its competition and the durability of its earnings.\n" * 8 + footer + "\n\n")*3
        chunks = archive.source_chunks(text)
        self.assertGreaterEqual(len(chunks), 3)
        self.assertTrue(all(len(c["text"]) > 300 for c in chunks))
        self.assertTrue(all(footer not in c["text"] for c in chunks))
        self.assertIn("business, then", chunks[0]["text"])

    def test_other_speakers_in_an_owned_catalogue_are_not_attributed(self):
        source = {"adapter": "pabrai", "investor": "pabrai", "url": "https://publisher.example/transcripts",
                  "publisher": "Publisher", "excludePattern": "Nisaba Godrej.*Omar Momin"}
        html = b'<a href="https://publisher.example/guest.pdf">Session with Nisaba Godrej and Omar Momin</a><a href="https://publisher.example/pabrai.pdf">Lecture by Mohnish Pabrai on May 5, 2025</a>'
        works = archive.link_catalog(source, get=lambda u: (html, "text/html"))
        self.assertEqual(len(works), 1)
        self.assertIn("Mohnish Pabrai", works[0]["title"]["en"])

    def test_source_outage_preserves_all_existing_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = {"schemaVersion": 1, "works": [self.work()]}
            archive.write(root / "archive/catalog.json", old)
            archive.write(root / "archive/sources.json", {"catalogues": [{"adapter": "lilu", "investor": "lilu", "url": "https://publisher.example/archive", "publisher": "Publisher"}]})
            with patch.object(archive, "link_catalog", side_effect=TimeoutError), patch.object(archive, "validate_catalog"):
                updated = archive.discover(root)
            self.assertEqual(updated["works"], old["works"])
            self.assertEqual(updated["discovery"][0]["status"], "retained")

    def test_published_catalogue_covers_every_configured_investor(self):
        catalog = archive.read(archive.ROOT / "archive/catalog.json")
        self.assertTrue(archive.validate_catalog(catalog))
        people = {p["id"] for p in archive.read(archive.ROOT / "investors.json")["investors"]}
        self.assertEqual({w["investor"] for w in catalog["works"]}, people)
        self.assertTrue(all(not w.get("noteFile") for w in catalog["works"]))


if __name__ == "__main__":
    unittest.main()
