#!/usr/bin/env python3
import argparse, csv, hashlib, json
from datetime import date, datetime, time, timedelta
from pathlib import Path

EXPECTED_BINDING = {'generation': 'programme-02', 'registry_sha256': 'a7c43a6691ac36d4e27a852d0476de8a08e7d56e96c1db1413c6c982807d721f'}
EXPECTED_IDS = ('series-01', 'series-02', 'series-03', 'series-04')
ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Verify public paper records and optional publication freshness")
    parser.add_argument("--require-current", action="store_true")
    parser.add_argument("--timezone", default="America/Chicago")
    parser.add_argument("--not-before", default="08:30")
    args = parser.parse_args()
    errors = []
    freshness = {"required": args.require_current, "checked": False}
    manifest = ROOT / "proof" / "records.sha256"
    listed = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        listed.append(relative)
        path = ROOT / relative
        if not path.is_file() or digest(path) != expected:
            errors.append("hash mismatch: " + relative)
    anchor = json.loads((ROOT / "proof" / "private_anchor.json").read_text())
    if args.require_current:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo(args.timezone))
        deadline = time.fromisoformat(args.not_before)
        if deadline.tzinfo is not None:
            parser.error("--not-before must be a local time without an offset")
        freshness.update(observed_at=now.isoformat(), not_before=args.not_before,
                         display_through=anchor.get("record_end"))
        if now.time() >= deadline:
            expected = (now.date() - timedelta(days=1)).isoformat()
            freshness.update(checked=True, expected_display_through=expected)
            if anchor.get("record_end") != expected:
                errors.append("stale display-through date: " + str(anchor.get("record_end")) + " != " + expected)
    if digest(manifest) != anchor.get("records_sha256"):
        errors.append("records manifest hash mismatch")
    if EXPECTED_BINDING and any(anchor.get(k) != v for k, v in EXPECTED_BINDING.items()):
        errors.append("programme generation/registry mismatch")
    if tuple(anchor.get("series_ids", ())) != EXPECTED_IDS:
        errors.append("series identity mismatch")
    if EXPECTED_BINDING:
        expected_files = {"README.md", "STATUS.md", "scripts/verify.py",
                          "data/comparison/daily.csv", "data/comparison/summary.csv"}
        if anchor.get("publication_documentation_version") == 1:
            expected_files.update({"VERIFY.md", ".gitattributes"})
        elif "publication_documentation_version" in anchor:
            errors.append("unsupported publication documentation version")
        expected_files.update("data/" + sid + "/" + name for sid in EXPECTED_IDS
                              for name in ("daily.csv", "weekly.csv", "monthly.csv", "summary.csv"))
        for path in (ROOT / "commitments").rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(ROOT).as_posix()
            expected_files.add(relative)
            try:
                value = json.loads(path.read_text())
                keys = {"schema", "generation", "registry_sha256", "series_id", "target_date", "decision_sha256"}
                wanted = "commitments/" + EXPECTED_BINDING["generation"] + "/" + value["target_date"] + "/" + value["series_id"] + ".json"
                if (set(value) != keys or value["schema"] != "neutral-paper-commitment-v1"
                        or any(value.get(k) != v for k, v in EXPECTED_BINDING.items())
                        or value["series_id"] not in EXPECTED_IDS or relative != wanted
                        or len(value["decision_sha256"]) != 64
                        or any(c not in "0123456789abcdef" for c in value["decision_sha256"])):
                    errors.append("invalid commitment: " + relative)
                date.fromisoformat(value["target_date"])
            except (ValueError, KeyError, TypeError):
                errors.append("unreadable commitment: " + relative)
        if set(listed) != expected_files or len(listed) != len(expected_files):
            errors.append("replacement manifest inventory mismatch")
        actual_data = {p.relative_to(ROOT).as_posix() for p in (ROOT / "data").rglob("*") if p.is_file()}
        if actual_data != {p for p in expected_files if p.startswith("data/")}:
            errors.append("replacement data inventory mismatch")
    daily = {}
    for series_id in EXPECTED_IDS:
        path = ROOT / "data" / series_id / "daily.csv"
        rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
        daily[series_id] = rows
        start, end = date.fromisoformat(anchor["record_start"]), date.fromisoformat(anchor["record_end"])
        calendar = [(start + timedelta(days=i)).isoformat() for i in range((end-start).days+1)]
        if [row["date"] for row in rows] != calendar:
            errors.append("daily calendar mismatch: " + series_id)
        if not rows or rows[0]["date"] != anchor["record_start"]:
            errors.append("daily range mismatch: " + series_id)
    economic = ("placed_mw", "awarded_mw", "fill_rate", "modeled_pnl",
                "always_clear_modeled_pnl", "limit_increment_modeled_pnl")
    paired = [(a, b) for a, b in zip(daily["series-01"], daily["series-02"])
              if a["status"] == b["status"] == "settled"]
    if not EXPECTED_BINDING and paired and all(all(a[key] == b[key] for key in economic) for a, b in paired):
        errors.append("series-01 and series-02 are economically indistinguishable")
    print(json.dumps({"ok": not errors, "errors": errors, "freshness": freshness}, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
