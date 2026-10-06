"""Sealed E24 result mirror; one publisher, no strategy or sizing changes.

The public alias series-02 is separate from the programme's withheld lane.
The source remains retrospective, including the daily continuation.
"""
from __future__ import annotations

import csv
from datetime import date, datetime, timedelta, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import re
import statistics
import warnings
from urllib.error import URLError
from urllib.request import Request, urlopen

SPEC = "3d9b97fd7f5ec8b509e459873cdc32c484f2d56d29ff250f0e20270a5b77435f"
CONTRACT = {"series-02": {"source_repository": "jameskim247/series-2",
    "source_series_id": "series-2", "evidence_basis": "retrospective_reconstruction",
    "frozen_specification_sha256": SPEC}}
NAMES = ("daily.csv", "weekly.csv", "monthly.csv", "summary.csv", "source_anchor.json")
FILES = tuple("data/series-02/" + name for name in (*NAMES, "publication.json")) + ("scripts/verify_e24.py",)
LIMIT = 20 * 1024 * 1024


def sha(body):
    return hashlib.sha256(body).hexdigest()


def expected_files(identity):
    if "external_series" not in identity:
        return ()
    if identity["external_series"] != CONTRACT:
        raise ValueError("unsupported external series contract")
    if "series-02" in identity.get("series_ids", ()):
        raise ValueError("E24 alias collides with a programme lane")
    return FILES


def typed(row):
    counts = {"calendar_days", "settled_days", "partially_settled_days", "ex_top_five_days_count"}
    text = {"date", "signal_date", "status", "evidence_basis", "basis", "start_date",
            "end_date", "period_start", "period_end", "latest_settled_date"}
    result = {}
    for key, value in row.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("malformed result row")
        if key in text or key.endswith("_id") or value == "":
            result[key] = value
        else:
            result[key] = int(value) if key in counts else float(value)
            if not math.isfinite(result[key]):
                raise ValueError("nonfinite result")
    body = {key: value for key, value in result.items() if key != "proof_id"}
    if sha(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()) != row.get("proof_id"):
        raise ValueError("E24 row proof mismatch")
    return result


def check(actual, expected, label, ratio=False):
    tolerance = 1e-5 * max(1.0, abs(expected)) if ratio else 0.10
    if not isinstance(actual, (int, float)) or abs(actual - expected) > tolerance:
        raise ValueError("E24 arithmetic mismatch: " + label)


def validate(files, through):
    if set(files) != set(NAMES) or sum(len(value) for value in files.values()) > LIMIT:
        raise ValueError("unexpected E24 payload inventory/size")
    anchor = json.loads(files["source_anchor.json"])
    if (anchor.get("schema") != "series-2-anchor-v1" or anchor.get("series_id") != "series-2"
            or anchor.get("record_start") != "2023-10-01"
            or anchor.get("specification_frozen") != "2026-10-02"
            or anchor.get("evidence_basis") != "retrospective_reconstruction"
            or anchor.get("public_cost_per_placed_mwh") != 0.4
            or anchor.get("private_commitments_sha256", {}).get("frozen_specification") != SPEC):
        raise ValueError("E24 frozen rule/cost/evidence contract changed")
    start, end = date.fromisoformat(anchor["record_start"]), date.fromisoformat(anchor["record_end"])
    if end < start or end > through:
        raise ValueError("E24 invalid or future record end")
    tables = {name: [typed(row) for row in csv.DictReader(io.StringIO(files[name].decode("utf-8")))]
              for name in NAMES if name.endswith(".csv")}
    daily = tables["daily.csv"]
    calendar = [(start + timedelta(days=i)).isoformat() for i in range((end-start).days+1)]
    if [row["date"] for row in daily] != calendar:
        raise ValueError("E24 daily calendar mismatch")
    equity = peak = 0.0
    for row in daily:
        if row["evidence_basis"] != "retrospective_reconstruction":
            raise ValueError("E24 evidence basis changed")
        if row["signal_date"] != (date.fromisoformat(row["date"]) - timedelta(days=1)).isoformat():
            raise ValueError("E24 signal date mismatch")
        if not 0 <= row["pending_awarded_mw"] <= row["awarded_mw"] <= row["placed_mw"] <= 800:
            raise ValueError("E24 volume bounds violated")
        status = "partially_settled" if row["pending_awarded_mw"] else "settled"
        if row["status"] != status:
            raise ValueError("E24 status/pending mismatch")
        check(row["pnl"], row["gross_pnl"] - 0.4*row["placed_mw"], "cost")
        equity += row["pnl"]; peak = max(peak, equity)
        check(row["cumulative_pnl"], equity, "cumulative")
        check(row["pnl_drawdown"], equity-peak, "drawdown")
        check(row["fill_rate"], row["awarded_mw"]/row["placed_mw"] if row["placed_mw"] else 0, "fill", True)
    for name in ("weekly.csv", "monthly.csv"):
        expected_groups = {}
        for row in daily:
            day = date.fromisoformat(row["date"])
            key = day - timedelta(days=day.weekday()) if name == "weekly.csv" else day.replace(day=1)
            expected_groups.setdefault(key, []).append(row)
        groups = list(expected_groups.values())
        periods = tables[name]
        if len(periods) != len(groups):
            raise ValueError("E24 period coverage mismatch")
        for row, selected in zip(periods, groups):
            if row["period_start"] != selected[0]["date"] or row["period_end"] != selected[-1]["date"]:
                raise ValueError("E24 period boundaries mismatch")
            _totals(row, selected, summary=False)
    ranges = [("full_displayed_history", start, end)] + [
        ("2023_q4" if year == 2023 else str(year) + ("_to_date" if year >= 2026 else ""),
         max(start, date(year, 1, 1)), min(end, date(year, 12, 31)))
        for year in range(start.year, end.year+1)]
    if end >= date(2026, 1, 1):
        ranges.append(("2026_h1", date(2026, 1, 1), min(end, date(2026, 6, 30))))
    if end >= date(2026, 7, 1):
        ranges.append(("2026_h2_to_date", date(2026, 7, 1), end))
    summaries = tables["summary.csv"]
    if len(summaries) != len(ranges):
        raise ValueError("E24 summary coverage mismatch")
    for row, (basis, first, last) in zip(summaries, ranges):
        if (row["basis"], row["start_date"], row["end_date"]) != (basis, str(first), str(last)):
            raise ValueError("E24 summary boundaries mismatch")
        selected = [r for r in daily if str(first) <= r["date"] <= str(last)]
        _totals(row, selected, summary=True)
        pnl = [r["pnl"] for r in selected]
        sd = statistics.stdev(pnl) if len(pnl) > 1 else 0
        if sd:
            check(row["annualized_pnl_mean_to_stdev"], statistics.mean(pnl)/sd*math.sqrt(365), "ratio", True)
        elif row["annualized_pnl_mean_to_stdev"] != "":
            raise ValueError("E24 undefined ratio must be empty")
        eq = pk = mdd = 0.0
        for value in pnl:
            eq += value; pk = max(pk, eq); mdd = min(mdd, eq-pk)
        check(row["max_pnl_drawdown"], mdd, "summary drawdown")
        check(row["worst_day_pnl"], min(pnl), "summary worst day")
        check(row["gross_pnl"], sum(r["gross_pnl"] for r in selected), "gross")
        check(row["costs"], 0.4*sum(r["placed_mw"] for r in selected), "summary costs")
    return anchor


def _totals(row, selected, *, summary):
    check(row["calendar_days"], len(selected), "calendar count")
    check(row["settled_days"], sum(r["status"] == "settled" for r in selected), "settled count")
    check(row["partially_settled_days"], sum(r["status"] == "partially_settled" for r in selected), "partial count")
    for key in ("placed_mw", "awarded_mw", "pending_awarded_mw"):
        check(row[key], sum(r[key] for r in selected), key)
    check(row["total_pnl" if summary else "pnl"], sum(r["pnl"] for r in selected), "period pnl")
    check(row["fill_rate"], row["awarded_mw"]/row["placed_mw"] if row["placed_mw"] else 0, "period fill", True)


def verify(root, identity):
    try:
        if not expected_files(identity):
            return []
        root = Path(root)
        files = {name: (root/"data/series-02"/name).read_bytes() for name in NAMES}
        anchor = validate(files, date.fromisoformat(identity["record_end"]))
        receipt = json.loads((root/"data/series-02/publication.json").read_text())
        missing = (date.fromisoformat(receipt["checked_through"]) - date.fromisoformat(anchor["record_end"])).days
        if (receipt["record_end"] != anchor["record_end"] or receipt["source_repository"] != "jameskim247/series-2"
                or not re.fullmatch("[0-9a-f]{40}", receipt["source_commit"])
                or receipt["state"] not in ("verified_source", "retained_verified_source")
                or receipt["missing_result_days"] != missing
                or receipt["status"] != ("current" if missing == 0 else "stale")):
            raise ValueError("E24 publication receipt mismatch")
        return []
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [str(exc)]


def attach(root, files, *, source_commit, through, state="verified_source"):
    """Attach only validated economic bytes; reseal without changing programme identity."""
    root = Path(root)
    anchor = validate(files, through)
    if not re.fullmatch("[0-9a-f]{40}", source_commit):
        raise ValueError("invalid E24 source commit")
    folder = root/"data/series-02"; folder.mkdir(parents=True, exist_ok=True)
    for name, body in files.items():
        (folder/name).write_bytes(body)
    receipt = {"source_repository": "jameskim247/series-2", "source_commit": source_commit,
        "record_end": anchor["record_end"], "checked_through": str(through), "state": state,
        "evidence_basis": "retrospective_reconstruction",
        "missing_result_days": (through - date.fromisoformat(anchor["record_end"])).days,
        "status": "current" if anchor["record_end"] == str(through) else "stale"}
    (folder/"publication.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    (root/"scripts/verify_e24.py").write_bytes(Path(__file__).read_bytes())
    readme = root/"README.md"
    readme.write_text(readme.read_text(encoding="utf-8").partition("\n## Series-02 / E24\n")[0] +
        "\n## Series-02 / E24\n\n[Daily](data/series-02/daily.csv) · "
        "[Weekly](data/series-02/weekly.csv) · [Monthly](data/series-02/monthly.csv) · "
        "[Summary](data/series-02/summary.csv)\n\n"
        f"Frozen E24 results: {anchor['record_start']}–{anchor['record_end']}. "
        "Retrospective reconstruction, not an on-time live commitment or untouched validation. "
        "Separate from Series-01 and from the programme's withheld lane; no combined performance claim. "
        "Incomplete settlement prices remain explicitly pending, never zero-filled. "
        "The existing GCP publisher refreshes this mirror on its regular runs. "
        "[Source and original proof](https://github.com/jameskim247/series-2), "
        "[source anchor](data/series-02/source_anchor.json), "
        "[mirror status](data/series-02/publication.json).\n", encoding="utf-8")
    seal(root)
    return receipt


def seal(root):
    root = Path(root)
    manifest = root/"proof/records.sha256"
    paths = {line.split("  ", 1)[1] for line in manifest.read_text().splitlines()}
    paths.update(FILES)
    manifest.write_text("".join(f"{sha((root/rel).read_bytes())}  {rel}\n" for rel in sorted(paths)), encoding="utf-8")
    path = root/"proof/private_anchor.json"
    identity = json.loads(path.read_text())
    identity["external_series"] = CONTRACT
    identity["records_sha256"] = sha(manifest.read_bytes())
    path.write_text(json.dumps(identity, indent=2, sort_keys=True)+"\n", encoding="utf-8")


def preserve(root, previous, through):
    previous = Path(previous)
    path = previous/"proof/private_anchor.json"
    if not path.is_file():
        return None
    identity = json.loads(path.read_text())
    if not expected_files(identity):
        return None
    manifest = previous/"proof/records.sha256"
    if sha(manifest.read_bytes()) != identity.get("records_sha256"):
        raise ValueError("existing E24 manifest hash mismatch")
    listed = dict((rel, digest) for digest, rel in
                  (line.split("  ", 1) for line in manifest.read_text().splitlines()))
    if any(not (previous/rel).is_file() or sha((previous/rel).read_bytes()) != listed.get(rel) for rel in FILES):
        raise ValueError("existing E24 file hash mismatch")
    errors = verify(previous, identity)
    if errors:
        raise ValueError("existing E24 mirror invalid: " + "; ".join(errors))
    files = {name: (previous/"data/series-02"/name).read_bytes() for name in NAMES}
    receipt = json.loads((previous/"data/series-02/publication.json").read_text())
    return attach(root, files, source_commit=receipt["source_commit"], through=through,
                  state="retained_verified_source")


def _get(url):
    with urlopen(Request(url, headers={"User-Agent": "ptp-results-mirror"}), timeout=20) as response:
        body = response.read(LIMIT+1)
    if len(body) > LIMIT:
        raise ValueError("E24 source exceeds size limit")
    return body


def refresh(root, previous, through):
    """Consumer: sole GCP publication transaction. Never adds another Git writer."""
    try:
        commit = json.loads(_get("https://api.github.com/repos/jameskim247/series-2/commits/main"))["sha"]
        if not re.fullmatch("[0-9a-f]{40}", commit):
            raise ValueError("invalid source revision")
        prefix = "https://raw.githubusercontent.com/jameskim247/series-2/" + commit + "/"
        files = {name: _get(prefix + ("proof/anchor.json" if name == "source_anchor.json"
                                      else "data/series-2/" + name)) for name in NAMES}
        incoming = validate(files, through)
        prior_path = Path(previous)/"data/series-02/source_anchor.json"
        if prior_path.is_file():
            if incoming["record_end"] < json.loads(prior_path.read_text())["record_end"]:
                raise ValueError("E24 source regressed")
            before = list(csv.DictReader(io.StringIO((Path(previous)/"data/series-02/daily.csv").read_text())))
            after = list(csv.DictReader(io.StringIO(files["daily.csv"].decode("utf-8"))))
            if (len(after) < len(before) or any((a["date"], a["decision_proof_id"]) !=
                    (b["date"], b["decision_proof_id"]) for a, b in zip(before, after))):
                raise ValueError("E24 source changed an existing frozen decision")
    except (OSError, URLError, ValueError, KeyError, TypeError) as exc:
        # Explicit degraded receipt, not a silent drop and not a Series-01 outage.
        retained = preserve(root, previous, through)
        warnings.warn("E24 mirror refresh rejected; retaining verified results: " + type(exc).__name__)
        return retained or {"state": "source_unavailable", "error_kind": type(exc).__name__}
    # Validation precedes all staging writes; filesystem/install errors are fatal.
    return attach(root, files, source_commit=commit, through=through)
