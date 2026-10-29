"""Publish only verified, permitted full texts with unchanged originals.

No summaries, invented dialogue, or third-party full text without permission.
Input must contain the complete original and reviewed sentence-aligned versions.
"""
import hashlib
import json
import re
from pathlib import Path


def validate_document(document, work_id):
    if document.get("kind") != "verbatim_text" or document.get("workId") != work_id:
        raise ValueError("Only original full-text documents are accepted")
    if any(k in document for k in ("lead", "chapters", "questions", "summary")):
        raise ValueError("A summary cannot be published as an original text")
    rights = document.get("rights", {})
    if (rights.get("basis") not in {"permission", "open_license", "public_domain", "user_provided"}
            or rights.get("verified") is not True or rights.get("allowPublication") is not True
            or rights.get("allowTranslation") is not True or not rights.get("evidence")):
        raise ValueError("Verified publication and translation permission is required")
    if document.get("reviewStatus") != "verified":
        raise ValueError("A draft or unreviewed ASR transcript must not be published as verified text")
    language = document.get("originalLanguage")
    original = document.get("originalText")
    if language not in {"zh", "en"} or not isinstance(original, str) or not original.strip():
        raise ValueError("Missing complete original text")
    digest = hashlib.sha256(original.encode("utf-8")).hexdigest()
    if document.get("sourceDigest") != digest:
        raise ValueError("Original text digest differs")
    segments = document.get("segments")
    if not isinstance(segments, list) or not segments:
        raise ValueError("Missing sentence-aligned translation")
    languages = document.get("languages", ["zh", "en"])
    if (not isinstance(languages, list) or language not in languages or not languages
            or any(k not in {"zh", "en"} for k in languages)):
        raise ValueError("Invalid available languages")
    seen = set()
    for segment in segments:
        if not isinstance(segment, dict) or not segment.get("id") or segment["id"] in seen:
            raise ValueError("Missing or duplicate sentence identifier")
        seen.add(segment["id"])
        if any(not isinstance(segment.get(k), str) or not segment[k].strip() for k in ["original", *languages]):
            raise ValueError("Each original sentence must have Chinese and English text")
        if segment[language] != segment["original"]:
            raise ValueError("The original-language version was altered")
    if "".join(s["original"] for s in segments) != original:
        raise ValueError("Sentences do not reconstruct the complete original exactly")
    return True


def import_document(root, work_id, input_path):
    root = Path(root)
    catalog_path = root / "archive/catalog.json"
    catalog = json.loads(catalog_path.read_text())
    work = next((w for w in catalog["works"] if w["id"] == work_id), None)
    if not work or not re.fullmatch(r"[a-z0-9_-]+", work_id):
        raise ValueError("Unknown investor document")
    document = json.loads(Path(input_path).read_text())
    validate_document(document, work_id)
    path = f"archive/texts/{work_id}.json"
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
    work["fullTextFile"], work["fullTextStatus"] = path, "ready"
    work.pop("noteFile", None)
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    return path
