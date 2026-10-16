#!/usr/bin/env python3
import csv
from datetime import date, datetime, timedelta
import hashlib, io, json, math, statistics
from pathlib import Path
START = '2024-01-01'
FOLDER = 'data/ptp-paper'
PAIRS = ('pairs-500', 'pairs-100', 'pairs-50')
NAMES = ('daily.csv', 'weekly.csv', 'monthly.csv', 'summary.csv', 'source_anchor.json', 'publication.json')
E24_SPEC = '3d9b97fd7f5ec8b509e459873cdc32c484f2d56d29ff250f0e20270a5b77435f'
PAIRS_DAILY = ('date', 'signal_date', 'status', 'pnl', 'gross_pnl', 'cumulative_pnl', 'pnl_drawdown', 'placed_mw', 'awarded_mw', 'fill_rate', 'pending_awarded_mw', 'pairs', 'pair_hours', 'eligibility_snapshot_id', 'decision_proof_id', 'settlement_proof_id', 'proof_id')

def digest(body):
    return hashlib.sha256(body).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def proved(row):
    return {**row, "proof_id": digest(encoded(row))}


def read_rows(body):
    integers = {"calendar_days", "settled_days", "pending_price_days", "ex_top_five_days_count", "path_count",
                "pairs", "pair_hours"}
    strings = {"date", "signal_date", "status", "basis", "start_date", "end_date",
               "period_start", "period_end", "latest_settled_date"}
    result = []
    for raw in csv.DictReader(io.StringIO(body.decode())):
        row = {}
        for key, value in raw.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("malformed paper row")
            row[key] = (value if value == "" or key in strings or key.endswith("_id")
                        else int(value) if key in integers else float(value))
            if isinstance(row[key], float) and not math.isfinite(row[key]):
                raise ValueError("nonfinite paper value")
        proof = row.pop("proof_id")
        if digest(encoded(row)) != proof:
            raise ValueError("paper row proof mismatch")
        result.append({**row, "proof_id": proof})
    return result


def totals(rows, *, include_counts=False):
    placed = round(math.fsum(r["placed_mw"] for r in rows), 1)
    awarded = round(math.fsum(r["awarded_mw"] for r in rows), 1)
    pending = round(math.fsum(r["pending_awarded_mw"] for r in rows), 1)
    counts = {"settled_days": sum(r["status"] == "settled" for r in rows),
              "pending_price_days": sum(r["status"] == "prices_pending" for r in rows)} if include_counts else {}
    return {"calendar_days": len(rows), **counts,
            "placed_mw": placed, "awarded_mw": awarded, "pending_awarded_mw": pending,
            "fill_rate": round(awarded / placed, 6) if placed else 0.0}


def ratio(values):
    sd = statistics.stdev(values) if len(values) > 1 else 0
    return round(statistics.mean(values) / sd * math.sqrt(365), 6) if sd else ""


def summary(basis, rows, *, include_counts=False):
    pnl = [r["pnl"] for r in rows]
    total, gross = math.fsum(pnl), math.fsum(r["gross_pnl"] for r in rows)
    equity = peak = drawdown = 0.0
    for value in pnl:
        equity += value
        peak = max(peak, equity)
        drawdown = min(drawdown, equity - peak)
    ex = sorted(pnl, reverse=True)[5:]
    downside = math.sqrt(statistics.mean(min(value, 0) ** 2 for value in pnl))
    losses = -math.fsum(value for value in pnl if value < 0)
    settled = [r["date"] for r in rows if r["status"] == "settled"]
    return proved({"basis": basis, "start_date": rows[0]["date"], "end_date": rows[-1]["date"],
        **totals(rows, include_counts=include_counts), "total_pnl": round(total, 4), "gross_pnl": round(gross, 4),
        "costs": round(gross - total, 4), "mean_day_pnl": round(statistics.mean(pnl), 6),
        "median_day_pnl": round(statistics.median(pnl), 4),
        "daily_pnl_stdev": round(statistics.stdev(pnl), 6) if len(pnl) > 1 else "",
        "annualized_pnl_mean_to_stdev": ratio(pnl), "worst_day_pnl": min(pnl),
        "pnl_es10": round(statistics.mean(sorted(pnl)[:math.ceil(len(pnl) / 10)]), 6),
        "max_pnl_drawdown": round(drawdown, 4),
        "annualized_zero_target_sortino": round(statistics.mean(pnl) / downside * math.sqrt(365), 6) if downside else "",
        "winning_day_fraction": round(sum(value > 0 for value in pnl) / len(pnl), 6),
        "profit_factor": round(math.fsum(value for value in pnl if value > 0) / losses, 6) if losses else "",
        "best_day_fraction_of_total_pnl": round(max(pnl) / total, 6) if total else "",
        "top_five_days_fraction_of_total_pnl": round(math.fsum(sorted(pnl, reverse=True)[:5]) / total, 6) if total else "",
        "ex_top_five_days_count": len(ex), "ex_top_five_total_pnl": round(math.fsum(ex), 4),
        "ex_top_five_annualized_pnl_mean_to_stdev": ratio(ex) if ex else "",
        "latest_settled_date": settled[-1] if settled else ""})


def tables(daily, *, include_counts=False):
    if not daily:
        raise ValueError("empty public paper window")
    result = {"daily.csv": daily}
    for name in ("weekly.csv", "monthly.csv"):
        groups = {}
        for row in daily:
            day = date.fromisoformat(row["date"])
            key = day - timedelta(days=day.weekday()) if name == "weekly.csv" else day.replace(day=1)
            groups.setdefault(key, []).append(row)
        result[name] = [proved({"period_start": group[0]["date"], "period_end": group[-1]["date"],
            "status": "prices_pending" if any(r["pending_awarded_mw"] for r in group) else "settled",
            **totals(group, include_counts=include_counts), "pnl": round(math.fsum(r["pnl"] for r in group), 4),
            "mean_day_pnl": round(statistics.mean(r["pnl"] for r in group), 6),
            "worst_day_pnl": min(r["pnl"] for r in group)}) for group in groups.values()]
    start, end = daily[0]["date"], daily[-1]["date"]
    ranges = [("full_displayed_history", start, end)]
    for year in range(date.fromisoformat(start).year, date.fromisoformat(end).year + 1):
        ranges.append((str(year) + ("_to_date" if str(year) == end[:4] and end[5:] != "12-31" else ""),
                       max(start, f"{year}-01-01"), min(end, f"{year}-12-31")))
    year = end[:4]
    for suffix, first, last in (("_h1", f"{year}-01-01", f"{year}-06-30"),
                                ("_h2_to_date", f"{year}-07-01", end)):
        if last >= first and end >= first:
            ranges.append((year + suffix, max(start, first), min(end, last)))
    result["summary.csv"] = [summary(label, selected, include_counts=include_counts) for label, first, last in ranges
        if (selected := [r for r in daily if first <= r["date"] <= last])]
    return result


def check_daily(daily, end, *, cap=None, legacy=False):
    """Public daily arithmetic, exposure bounds and honest pending labels."""
    start, end = date.fromisoformat(START), date.fromisoformat(end)
    if [row["date"] for row in daily] != [(start + timedelta(days=i)).isoformat() for i in range((end-start).days+1)]:
        raise ValueError("paper daily calendar mismatch")
    equity = peak = 0.0
    for row in daily:
        if "evidence_basis" in row or "partially" in row["status"]:
            raise ValueError("retired public daily schema")
        if not 0 <= row["pending_awarded_mw"] <= row["awarded_mw"] <= row["placed_mw"] <= 2400:
            raise ValueError("paper exposure bounds violated")
        if legacy:
            if "path_count" in row and not 0 <= row["path_count"] <= row["placed_mw"]/3 + 1e-8:
                raise ValueError("paper submitted path count bounds violated")
        else:
            hours, pairs = row.get("pair_hours"), row.get("pairs")
            if "path_count" in row or type(hours) is not int or not 0 <= hours <= row["placed_mw"]/3 + 1e-8:
                raise ValueError("paper pair-hour count bounds violated")
            if pairs != "" or cap is not None:
                if type(pairs) is not int or not (pairs == hours == 0 or 1 <= pairs <= hours):
                    raise ValueError("paper distinct pair count bounds violated")
                if cap is not None and pairs > cap:
                    raise ValueError("pair cap exceeded")
        if row["status"] != ("prices_pending" if row["pending_awarded_mw"] else "settled"):
            raise ValueError("paper settlement status hides pending prices")
        if row["signal_date"] != (date.fromisoformat(row["date"]) - timedelta(days=1)).isoformat():
            raise ValueError("paper signal date mismatch")
        equity += row["pnl"]
        peak = max(peak, equity)
        if (abs(row["pnl"] - (row["gross_pnl"] - 0.4 * row["placed_mw"])) > 0.001
                or abs(row["cumulative_pnl"] - equity) > 0.001
                or abs(row["pnl_drawdown"] - (equity-peak)) > 0.001
                or abs(row["fill_rate"] - (row["awarded_mw"] / row["placed_mw"] if row["placed_mw"] else 0)) > 1e-6):
            raise ValueError("paper daily arithmetic mismatch")


def check_receipt(receipt, end):
    missing = (date.fromisoformat(receipt["checked_through"]) - date.fromisoformat(end)).days
    if (missing < 0 or receipt.get("missing_result_days") != missing
            or receipt.get("status") != ("current" if missing == 0 else "stale")
            or receipt.get("state") not in ("verified_source", "retained_verified_source")):
        raise ValueError("paper publication freshness mismatch")


def check_pairs_folder(root, folder, record_end):
    name = folder.split("/", 1)[1]
    cap = int(name.split("-", 1)[1])
    anchor = json.loads((root / folder / "source_anchor.json").read_bytes())
    receipt = json.loads((root / folder / "publication.json").read_bytes())
    package = str(anchor.get("source_package_sha256", ""))
    if (anchor.get("schema") != "ptp-pairs-anchor-v1" or anchor.get("series") != name
            or anchor.get("pair_cap") != cap or anchor.get("record_start") != START
            or anchor.get("quantity_multiplier") != 3 or anchor.get("public_cost_per_placed_mwh") != 0.4
            or anchor.get("evidence_basis") != "retrospective_scaled_reconstruction"
            or anchor.get("development_only") is not True
            or anchor.get("parent_specification_sha256") != E24_SPEC
            or str(anchor.get("record_end", "")) > record_end
            or receipt.get("record_start") != START or receipt.get("record_end") != anchor.get("record_end")
            or len(package) != 64 or any(c not in "0123456789abcdef" for c in package)
            or receipt.get("source_package_sha256") != package):
        raise ValueError("pairs provenance contract mismatch: " + name)
    hashes = {n: digest((root / folder / n).read_bytes()) for n in NAMES if n.endswith(".csv")}
    if anchor.get("files_sha256") != hashes:
        raise ValueError("pairs file binding mismatch: " + name)
    data = {n: read_rows((root / folder / n).read_bytes()) for n in hashes}
    daily = data["daily.csv"]
    if any(list(row) != list(PAIRS_DAILY[:-1]) + ["source_proof_id", "proof_id"] for row in daily):
        raise ValueError("pairs daily schema mismatch: " + name)
    if any(len(row["eligibility_snapshot_id"]) != 64 for row in daily):
        raise ValueError("pairs eligibility binding missing: " + name)
    check_daily(daily, anchor["record_end"], cap=cap)
    expected = tables(daily)
    if any(data[n] != expected[n] for n in ("weekly.csv", "monthly.csv", "summary.csv")):
        raise ValueError("pairs aggregate arithmetic mismatch: " + name)
    check_receipt(receipt, anchor["record_end"])


def verify(root):
    """Standalone public checks: hashes, calendar, arithmetic and honest exposure."""
    root = Path(root)
    try:
        identity = json.loads((root / "proof/private_anchor.json").read_bytes())
        projection = identity.get("paper_projection")
        legacy = projection in tuple({"schema": schema, "record_start": START,
                "folder": FOLDER, "quantity_multiplier": 3}
                for schema in ("ptp-paper-projection-v1", "ptp-paper-projection-v2"))
        if legacy:
            folders = [FOLDER]
        elif (isinstance(projection, dict) and projection.get("schema") == "ptp-paper-projection-v3"
                and set(projection) == {"schema", "record_start", "folders", "quantity_multiplier"}
                and projection["record_start"] == START and projection["quantity_multiplier"] == 3
                and projection["folders"] in ([FOLDER], [FOLDER, *("data/" + p for p in PAIRS)])):
            folders = projection["folders"]
        else:
            raise ValueError("unsupported paper projection")
        manifest = (root / "proof/records.sha256").read_bytes()
        if digest(manifest) != identity.get("records_sha256"):
            raise ValueError("paper manifest hash mismatch")
        entries = [line.split("  ", 1) for line in manifest.decode().splitlines()]
        published = {folder + "/" + name for folder in folders for name in NAMES}
        required = {"README.md", "STATUS.md", "scripts/verify.py", ".gitattributes", *published}
        if len(entries) != len(required) or {entry[1] for entry in entries} != required:
            raise ValueError("paper manifest inventory mismatch")
        for expected, relative in entries:
            if digest((root / relative).read_bytes()) != expected:
                raise ValueError("paper file hash mismatch: " + relative)
        for directory, expected in (("data", published), ("scripts", {"scripts/verify.py"})):
            if {p.relative_to(root).as_posix() for p in (root / directory).rglob("*") if p.is_file()} != expected:
                raise ValueError("paper folder inventory mismatch: " + directory)
        anchor = json.loads((root / FOLDER / "source_anchor.json").read_bytes())
        receipt = json.loads((root / FOLDER / "publication.json").read_bytes())
        if (anchor.get("schema") != "ptp-paper-anchor-v1" or anchor.get("record_start") != START
                or anchor.get("quantity_multiplier") != 3
                or anchor.get("evidence_basis") != "retrospective_scaled_reconstruction"
                or anchor.get("public_cost_per_placed_mwh") != 0.4
                or anchor.get("source_frozen_specification_sha256") != E24_SPEC
                or anchor.get("record_end") != identity.get("record_end")
                or receipt.get("record_start") != START or receipt.get("record_end") != anchor["record_end"]):
            raise ValueError("paper provenance contract mismatch")
        package = anchor.get("source_package_sha256", "")
        if (len(package) != 64 or any(c not in "0123456789abcdef" for c in package)
                or receipt.get("source_package_sha256") != package):
            raise ValueError("paper source package binding mismatch")
        hashes = {name: digest((root / FOLDER / name).read_bytes()) for name in NAMES if name.endswith(".csv")}
        if anchor.get("files_sha256") != hashes:
            raise ValueError("paper source file binding mismatch")
        data = {name: read_rows((root / FOLDER / name).read_bytes()) for name in hashes}
        daily = data["daily.csv"]
        if (projection["schema"] in ("ptp-paper-projection-v2", "ptp-paper-projection-v3")
                and any({"settled_days", "pending_price_days"} & row.keys() for row in daily)):
            raise ValueError("retired paper count columns")
        check_daily(daily, anchor["record_end"], legacy=legacy)
        # Retained v1 packages remain verifiable during recovery; new v2 output
        # omits only the two count columns, never pending exposure or its status.
        expected = tables(daily, include_counts=projection["schema"] == "ptp-paper-projection-v1")
        if any(data[name] != expected[name] for name in ("weekly.csv", "monthly.csv", "summary.csv")):
            raise ValueError("paper aggregate arithmetic/counts mismatch")
        check_receipt(receipt, anchor["record_end"])
        for folder in folders[1:]:
            check_pairs_folder(root, folder, anchor["record_end"])
        return []
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as exc:
        return [str(exc)]


def main():
    import argparse
    from zoneinfo import ZoneInfo
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-current", action="store_true")
    parser.add_argument("--timezone", default="America/Chicago")
    parser.add_argument("--not-before", default="08:30")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    errors = verify(root)
    if args.require_current and not errors:
        now = datetime.now(ZoneInfo(args.timezone))
        if now.strftime("%H:%M") >= args.not_before:
            end = json.loads((root / FOLDER / "source_anchor.json").read_bytes())["record_end"]
            if end < (now.date() - timedelta(days=1)).isoformat():
                errors.append("stale display-through date: " + end)
    print(json.dumps({"status": "failed" if errors else "verified", "errors": errors}))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
