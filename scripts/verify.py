#!/usr/bin/env python3
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main():
    errors = []
    manifest = ROOT / "proof" / "records.sha256"
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        if not path.is_file() or digest(path) != expected:
            errors.append("hash mismatch: " + relative)
    anchor = json.loads((ROOT / "proof" / "private_anchor.json").read_text())
    if digest(manifest) != anchor.get("records_sha256"):
        errors.append("records manifest hash mismatch")
    daily = {}
    for series_id in ("series-01", "series-02", "series-03"):
        path = ROOT / "data" / series_id / "daily.csv"
        rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
        daily[series_id] = rows
        if not rows or rows[0]["date"] != anchor["record_start"]:
            errors.append("daily range mismatch: " + series_id)
    economic = ("placed_mw", "awarded_mw", "fill_rate", "modeled_pnl",
                "always_clear_modeled_pnl", "limit_increment_modeled_pnl")
    paired = [(a, b) for a, b in zip(daily["series-01"], daily["series-02"])
              if a["status"] == b["status"] == "settled"]
    if paired and all(all(a[key] == b[key] for key in economic) for a, b in paired):
        errors.append("series-01 and series-02 are economically indistinguishable")
    print(json.dumps({"ok": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
