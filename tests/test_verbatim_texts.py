import copy
import hashlib
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


if __name__ == "__main__":
    unittest.main()
