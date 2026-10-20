#!/usr/bin/env python3
import csv
from datetime import date, datetime, timedelta
import hashlib, io, json, math, statistics
from pathlib import Path
START = '2024-01-01'
NAMES = ('daily.csv', 'weekly.csv', 'monthly.csv', 'summary.csv', 'source_anchor.json', 'publication.json')
PUBLIC_SERIES = ('pairs-100', 'pairs-50')
PUBLIC_DAILY = ('date', 'signal_date', 'status', 'pnl', 'cumulative_pnl', 'pnl_drawdown', 'placed_mw', 'awarded_mw', 'fill_rate', 'pending_awarded_mw', 'pairs', 'pair_hours', 'submission_credit', 'eligibility_snapshot_id', 'decision_proof_id', 'settlement_proof_id', 'source_proof_id', 'proof_id')
RISK = 'data/risk'
PUBLIC_RISK_NAMES = ('stress.csv', 'source_anchor.json', 'publication.json')
STORM_RISK_NAMES = ('stress.csv', 'stress_daily.csv', 'source_anchor.json', 'publication.json')
STORM_CONTRACT = {'schema': 'ptp-historical-storm-anchor-v1', 'run_date': '2026-10-19', 'method': 'historical_strategy_replay', 'development_only': True, 'events': {'uri': ['2021-02-14', '2021-02-19'], 'elliott': ['2022-12-22', '2022-12-25']}, 'evidence_basis': 'retrospective diagnostic; not executed trades or independent validation', 'cost_basis': 'before costs; no market-impact model; current published quantities', 'assumptions': {'sizing': 'Cold start at the frozen risk prior at each event start; D-2 reference updates within the event. Not a continuous pre-storm sizing history.', 'nodes': 'Then-observed price universe and the latest 30 DAM disclosures published before D-1 09:55 America/Chicago; fixed logical-node exclusions.', 'grid': 'Same grid-score formula, causally refitted from archives beginning 2018; no modern topology peer map; unavailable node fits retain the existing zero fallback.', 'deenergized_lists': "Original operating-day lists unavailable. Existing in-money/no-awards restriction reconstructed from market bids and awards for auction outcomes only, not that day's order selection.", 'prices': 'First-published vintages for decisions and original DA clearing for awards. Final corrections affect settlement, never earlier decisions. Correction search ends 181 days after each event start.', 'settlement': 'Strict DA sink-minus-source spread < bid. P&L = MWh times (RT spread minus DA settlement spread). Four paired 15-minute RT intervals required; missing payouts are not zero.', 'coverage': 'Price coverage divides fully priced modeled awarded MWh by modeled awarded MWh. Award-node evidence requires both node/hour endpoints in actual market PTP awards; it is not actual awards to this strategy or exact directed-pair award coverage.'}, 'source_bindings': {'frozen_plan_sha256': '7227acf4478dc00d8677f0849e48639bc2983d51f390f90b6d4170563121b70b', 'replay_code_sha256': '5e843a2c066c042e2b659914fd8a182bc5b7f294e917642979102fd03595aba2', 'audit_results_sha256': 'b05a1538696cb957b76df5bea68f9835184c0e77f45e84c7ca3a63298105aeb0', 'uri_order_records_sha256': '10263e2036c3d29fece16847f6801d5f6d953d92bdaf740bf4e949e825de6927', 'elliott_order_records_sha256': '5ea809889e1068b9566a271bd4d8cc92226d47cfa2c35a052374516327e8b9c0'}}
STORM_SNAPSHOT_SHA256 = '43e7d9fe086c2c2702c24b69c6c292d31a65358d644ee4010d212144d7093078'
STORM_FILE_HASHES = {'stress.csv': 'ee767a49018a09992b6703b6da3d073dff2b9d1469c3cf3a94dacf5841e23c8c', 'stress_daily.csv': '2ce416b123a5fbc05a7562fca00ecdffa675d236affce23c240c3ff4deb479e2'}
STRESS = ('series', 'book_date', 'scenario', 'scenario_date', 'method', 'pnl', 'covered_share')
SCENARIOS = ('uri_2021', 'elliott_2022')
PUBLIC_DOCS = ('data/docs/submission-credit.md', 'data/docs/stress.md')
PUBLIC_PROJECTION = 'ptp-paper-projection-v6'
RULE_PROSPECTIVE = '2026-10-20'
RULE_CONTINUATION = '2026-09-30'
RULE_CUTOFF = '2026-10-19T09:55:00-05:00'
RULE_PROTOCOL_SHA256 = '8d89c954b9210d6078537b0dbac2881bdc6fa9ee8b76259b9158419def61898a'
RULE_FROZEN_AT = '2026-10-18T12:00:14-05:00'
ARCHIVE = 'archive'
RETIRED = ('ptp-paper', 'pairs-500', 'pairs-100', 'pairs-50', 'risk')

def digest(body):
    return hashlib.sha256(body).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def proved(row):
    return {**row, "proof_id": digest(encoded(row))}


def read_rows(body):
    integers = {"calendar_days", "settled_days", "pending_price_days", "ex_top_five_days_count", "path_count",
                "pairs", "pair_hours", "nodes", "peak_hour"}
    strings = {"date", "signal_date", "status", "basis", "start_date", "end_date",
               "period_start", "period_end", "latest_settled_date", "series", "book_date", "scenario",
               "scenario_date", "method", "storm", "worst_date"}
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


def credit_stats(rows, *names):
    """Submission credit aggregates; empty when no day of the period has one."""
    values = [r["submission_credit"] for r in rows if r.get("submission_credit", "") != ""]
    stats = {"median_submission_credit": round(statistics.median(values), 4) if values else "",
             "max_submission_credit": round(max(values), 4) if values else ""}
    return {name: stats[name] for name in names}


def ratio(values):
    sd = statistics.stdev(values) if len(values) > 1 else 0
    return round(statistics.mean(values) / sd * math.sqrt(365), 6) if sd else ""


def summary(basis, rows, *, include_counts=False):
    pnl = [r["pnl"] for r in rows]
    total = math.fsum(pnl)
    split = {}
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
        **totals(rows, include_counts=include_counts), "total_pnl": round(total, 4), **split,
        "mean_day_pnl": round(statistics.mean(pnl), 6),
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
        "latest_settled_date": settled[-1] if settled else "",
        **(credit_stats(rows, "median_submission_credit", "max_submission_credit")
           if "submission_credit" in rows[0] else {})})


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
            "worst_day_pnl": min(r["pnl"] for r in group),
            **(credit_stats(group, "max_submission_credit") if "submission_credit" in group[0] else {})})
            for group in groups.values()]
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


def evidence_tables(daily):
    """tables() with the evidence split: summary rows for the development backtest (to the day before
    RULE_PROSPECTIVE) and the prospective record (from it); calendar rows spanning both are marked _incl_development."""
    result = tables(daily)
    rows = []
    for row in result["summary.csv"]:
        body = {k: v for k, v in row.items() if k != "proof_id"}
        if body["start_date"] < RULE_PROSPECTIVE <= body["end_date"]:
            body["basis"] += "_incl_development"
        rows.append(proved(body))
    development = [r for r in daily if r["date"] < RULE_PROSPECTIVE]
    prospective = [r for r in daily if r["date"] >= RULE_PROSPECTIVE]
    evidence = [summary("development_backtest", development)] if development else []
    evidence += [summary("prospective_record", prospective)] if prospective else []
    result["summary.csv"] = evidence + rows
    return result


def unavailable_row(row, first):
    """A day published as unavailable: from `first` on, no orders, zero P&L and no eligibility snapshot."""
    return (row["status"] == "unavailable" and first is not None and row["date"] >= first
            and row["eligibility_snapshot_id"] == "" and row["pnl"] == 0
            and row["placed_mw"] == row["awarded_mw"] == row["pending_awarded_mw"] == 0
            and row["pairs"] == row["pair_hours"] == 0 and row["submission_credit"] == 0)


def check_receipt(receipt, end):
    missing = (date.fromisoformat(receipt["checked_through"]) - date.fromisoformat(end)).days
    if (missing < 0 or receipt.get("missing_result_days") != missing
            or receipt.get("status") != ("current" if missing == 0 else "stale")
            or receipt.get("state") not in ("verified_source", "retained_verified_source")):
        raise ValueError("paper publication freshness mismatch")


def frozen_before_cutoff():
    try:
        return datetime.fromisoformat(RULE_FROZEN_AT) < datetime.fromisoformat(RULE_CUTOFF)
    except ValueError:
        return False


def evidence_basis():
    development = (date.fromisoformat(RULE_PROSPECTIVE) - timedelta(days=1)).isoformat()
    return {"development": START + " to " + development + ": retrospective development backtest; the rule was "
                           "designed after these outcomes were seen, so they are not validation",
            "prospective": "from " + RULE_PROSPECTIVE + ": prospective record of the rule frozen at " + RULE_FROZEN_AT
                           + ", rebuilt from the inputs each base decision recorded (recorded vintage)"}


def public_rule():
    return {"protocol_sha256": RULE_PROTOCOL_SHA256, "frozen_at": RULE_FROZEN_AT,
            "first_prospective_cutoff": RULE_CUTOFF}


def check_public_daily(daily, end, cap):
    """Projection v6 daily rows: calendar, schema, bounds, honest pending labels and arithmetic."""
    start, last = date.fromisoformat(START), date.fromisoformat(end)
    if [row["date"] for row in daily] != [(start + timedelta(days=i)).isoformat() for i in range((last - start).days + 1)]:
        raise ValueError("paper daily calendar mismatch")
    equity = peak = 0.0
    for row in daily:
        if list(row) != list(PUBLIC_DAILY):
            raise ValueError("public daily schema mismatch")
        hours, pairs, credit = row["pair_hours"], row["pairs"], row["submission_credit"]
        unavailable = unavailable_row(row, RULE_CONTINUATION)
        if (not 0 <= row["pending_awarded_mw"] <= row["awarded_mw"] <= row["placed_mw"] <= 2400
                or type(hours) is not int or type(pairs) is not int or hours > row["placed_mw"] + 1e-8
                or not (pairs == hours == 0 or 1 <= pairs <= hours) or pairs > cap
                or not isinstance(credit, float) or credit < 0
                or (len(row["eligibility_snapshot_id"]) != 64 and not unavailable)):
            raise ValueError("public daily bounds violated: " + row["date"])
        if row["status"] != ("prices_pending" if row["pending_awarded_mw"] else "settled") and not unavailable:
            raise ValueError("paper settlement status hides pending prices")
        if row["signal_date"] != (date.fromisoformat(row["date"]) - timedelta(days=1)).isoformat():
            raise ValueError("paper signal date mismatch")
        equity += row["pnl"]
        peak = max(peak, equity)
        if (abs(row["cumulative_pnl"] - equity) > 0.001 or abs(row["pnl_drawdown"] - (equity - peak)) > 0.001
                or abs(row["fill_rate"] - (row["awarded_mw"] / row["placed_mw"] if row["placed_mw"] else 0)) > 1e-6):
            raise ValueError("paper daily arithmetic mismatch")


def check_public_folder(root, folder, record_end):
    """One projection v6 series: provenance, binding, calendar, arithmetic and freshness."""
    name = folder.split("/", 1)[1]
    cap = int(name.split("-", 1)[1])
    anchor = json.loads((root / folder / "source_anchor.json").read_bytes())
    receipt = json.loads((root / folder / "publication.json").read_bytes())
    package = str(anchor.get("source_package_sha256", ""))
    development = (date.fromisoformat(RULE_PROSPECTIVE) - timedelta(days=1)).isoformat()
    if (set(anchor) != {"schema", "series", "pair_cap", "record_start", "record_end", "development_through",
                        "prospective_from", "evidence_basis", "public_cost_per_placed_mwh", "source_package_sha256",
                        "source_files_sha256", "protocol_sha256", "rule", "kill_rule_breach", "files_sha256"}
            or anchor.get("schema") != "ptp-series-anchor-v6" or anchor.get("series") != name
            or anchor.get("protocol_sha256") != RULE_PROTOCOL_SHA256
            or anchor.get("pair_cap") != cap or anchor.get("record_start") != START
            or str(anchor.get("record_end", "")) != record_end or anchor.get("development_through") != development
            or anchor.get("prospective_from") != RULE_PROSPECTIVE or anchor.get("evidence_basis") != evidence_basis()
            or anchor.get("rule") != public_rule() or anchor.get("public_cost_per_placed_mwh") != 0
            or receipt.get("record_start") != START or receipt.get("record_end") != record_end
            or len(package) != 64 or any(c not in "0123456789abcdef" for c in package)
            or receipt.get("source_package_sha256") != package):
        raise ValueError("series provenance contract mismatch: " + name)
    hashes = {n: digest((root / folder / n).read_bytes()) for n in NAMES if n.endswith(".csv")}
    if anchor.get("files_sha256") != hashes:
        raise ValueError("series file binding mismatch: " + name)
    data = {n: read_rows((root / folder / n).read_bytes()) for n in hashes}
    check_public_daily(data["daily.csv"], record_end, cap)
    expected = evidence_tables(data["daily.csv"])
    if any(data[n] != expected[n] for n in ("weekly.csv", "monthly.csv", "summary.csv")):
        raise ValueError("series aggregate arithmetic mismatch: " + name)
    check_receipt(receipt, record_end)


def storm_summary(daily):
    """Event totals recomputed from daily rows; coverage is MWh-weighted, not an average of rates."""
    result = []
    additive = ("pnl", "da_pnl", "rt_pnl", "placed_mwh", "awarded_mwh", "priced_awarded_mwh",
                "unpriced_mwh", "award_node_evidence_mwh", "exact_pair_award_mwh", "blocked_mwh")
    for storm, window in STORM_CONTRACT["events"].items():
        for series in PUBLIC_SERIES:
            rows = sorted((r for r in daily if r["storm"] == storm and r["series"] == series), key=lambda r: r["date"])
            days = [(date.fromisoformat(window[0]) + timedelta(days=k)).isoformat()
                    for k in range((date.fromisoformat(window[1]) - date.fromisoformat(window[0])).days + 1)]
            if [r["date"] for r in rows] != days:
                raise ValueError("storm calendar is incomplete or duplicated")
            values = {key: round(math.fsum(r[key] for r in rows), 6) for key in additive}
            equity = peak = drawdown = 0.0
            for row in rows:
                equity += row["pnl"]
                peak = max(peak, equity)
                drawdown = max(drawdown, peak - equity)
            worst = min(rows, key=lambda r: r["pnl"])
            awarded = values["awarded_mwh"]
            result.append(proved({"series": series, "storm": storm, "start_date": window[0], "end_date": window[1],
                "calendar_days": len(rows), "method": "historical_strategy_replay", **values,
                "max_drawdown": round(drawdown, 6), "worst_day": worst["pnl"], "worst_date": worst["date"],
                "price_coverage": values["priced_awarded_mwh"] / awarded if awarded else 0.0,
                "award_node_evidence_coverage": values["award_node_evidence_mwh"] / awarded if awarded else 0.0,
                "exact_pair_award_coverage": values["exact_pair_award_mwh"] / awarded if awarded else 0.0}))
    return result


def public_risk_names(root):
    anchor = json.loads((Path(root) / RISK / "source_anchor.json").read_bytes())
    return STORM_RISK_NAMES if anchor.get("schema") == STORM_CONTRACT["schema"] else PUBLIC_RISK_NAMES


def check_historical_storm_risk(root):
    """Verify pinned historical evidence, its daily arithmetic and distinct coverage denominators."""
    folder = Path(root) / RISK
    anchor = json.loads((folder / "source_anchor.json").read_bytes())
    hashes = {name: digest((folder / name).read_bytes()) for name in ("stress.csv", "stress_daily.csv")}
    if anchor != {**STORM_CONTRACT, "study_sha256": STORM_SNAPSHOT_SHA256, "files_sha256": hashes}:
        raise ValueError("storm provenance or file binding mismatch")
    if hashes != STORM_FILE_HASHES:
        raise ValueError("storm reviewed evidence changed")
    receipt = json.loads((folder / "publication.json").read_bytes())
    if receipt != {"schema": "ptp-historical-storm-publication-v1", "run_date": STORM_CONTRACT["run_date"],
                   "study_sha256": STORM_SNAPSHOT_SHA256, "state": "verified_historical_diagnostic",
                   "status": "fixed_historical_study"}:
        raise ValueError("storm receipt mismatch")
    daily = read_rows((folder / "stress_daily.csv").read_bytes())
    if len(daily) != 20:
        raise ValueError("storm daily row count mismatch")
    for r in daily:
        aw, priced, missing = (r[k] for k in ("awarded_mwh", "priced_awarded_mwh", "unpriced_mwh"))
        if (r["series"] not in PUBLIC_SERIES or r["storm"] not in STORM_CONTRACT["events"]
                or r["method"] != "historical_strategy_replay" or not 0 <= aw <= r["placed_mwh"]
                or not 0 <= priced <= aw or not 0 <= missing <= aw or abs(priced + missing - aw) > 1e-6
                or abs(r["da_pnl"] + r["rt_pnl"] - r["pnl"]) > 1e-6
                or not 0 <= r["exact_pair_award_mwh"] <= r["award_node_evidence_mwh"] <= aw
                or not 0 <= r["pairs"] <= int(r["series"].split("-")[1]) or r["pair_hours"] < r["pairs"]):
            raise ValueError("storm daily arithmetic or bounds mismatch")
        for name, numerator in (("price_coverage", priced), ("award_node_evidence_coverage", r["award_node_evidence_mwh"]),
                                ("exact_pair_award_coverage", r["exact_pair_award_mwh"])):
            if abs(r[name] - (numerator / aw if aw else 0.0)) > 1e-10:
                raise ValueError("storm coverage mismatch")
        if any(len(r[k]) != 64 or any(c not in "0123456789abcdef" for c in r[k])
               for k in ("decision_proof_id", "settlement_proof_id")):
            raise ValueError("storm private evidence binding mismatch")
    if read_rows((folder / "stress.csv").read_bytes()) != storm_summary(daily):
        raise ValueError("storm event totals disagree with daily rows")


def check_public_risk(root, record_end):
    """Projection v6 stress table: binding, bounds and freshness."""
    anchor = json.loads((root / RISK / "source_anchor.json").read_bytes())
    if anchor.get("schema") == STORM_CONTRACT["schema"]:
        return check_historical_storm_risk(root)
    receipt = json.loads((root / RISK / "publication.json").read_bytes())
    package = str(anchor.get("source_package_sha256", ""))
    end = str(anchor.get("record_end", ""))
    if (set(anchor) != {"schema", "record_start", "record_end", "book_date", "development_only", "evidence_basis",
                        "source_package_sha256", "definitions", "files_sha256"}
            or anchor.get("schema") != "ptp-stress-anchor-v6" or anchor.get("record_start") != START
            or anchor.get("development_only") is not True or end > record_end or anchor.get("book_date") != end
            or receipt.get("record_start") != START or receipt.get("record_end") != end
            or len(package) != 64 or any(c not in "0123456789abcdef" for c in package)
            or receipt.get("source_package_sha256") != package):
        raise ValueError("stress provenance contract mismatch")
    if anchor.get("files_sha256") != {"stress.csv": digest((root / RISK / "stress.csv").read_bytes())}:
        raise ValueError("stress file binding mismatch")
    named = {s + suffix for s in SCENARIOS for suffix in ("", "_total")}
    ranked = {"in_sample_worst_" + str(k) for k in range(1, 6)} | {"in_sample_p01", "in_sample_p05", "in_sample_median"}
    for row in read_rows((root / RISK / "stress.csv").read_bytes()):
        if (list(row) != [*STRESS, "proof_id"] or row["series"] not in PUBLIC_SERIES or row["book_date"] != end
                or row["method"] not in ("rt_shock", "replay") or row["scenario"] not in named | ranked
                or not isinstance(row["pnl"], float) or not 0 <= row["covered_share"] <= 1
                or (row["scenario_date"] == "") != (row["scenario"].endswith("_total")
                                                    or row["scenario"].startswith("in_sample_p")
                                                    or row["scenario"] == "in_sample_median")):
            raise ValueError("stress row mismatch")
    check_receipt(receipt, end)


def verify_public(root, identity, projection):
    """Projection v6: two series, the stress table, two notes and the unchanged archive (without its README)."""
    archive = projection.get("archive")
    folders = ["data/" + s for s in PUBLIC_SERIES]
    if (set(projection) != {"schema", "record_start", "folders", "documents", "prospective_from", "archive"}
            or projection["record_start"] != START or projection["prospective_from"] != RULE_PROSPECTIVE
            or projection["folders"] != [*folders, RISK] or projection["documents"] != list(PUBLIC_DOCS)
            or not isinstance(archive, dict) or set(archive) != {"retired_series", "last_published_day", "files_sha256"}
            or any(not path.startswith(ARCHIVE + "/") for path in archive["files_sha256"])
            or ARCHIVE + "/README.md" in archive["files_sha256"]
            or ARCHIVE + "/ptp-paper/daily.csv" not in archive["files_sha256"]
            or archive["retired_series"] != [s for s in RETIRED if any(
                path.startswith(ARCHIVE + "/" + s + "/") for path in archive["files_sha256"])]):
        raise ValueError("unsupported paper projection")
    if not frozen_before_cutoff():
        raise ValueError("protocol was not frozen before the first prospective bid deadline")
    parent = identity.get("paper_parent")
    if (not isinstance(parent, dict) or set(parent) != {"schema", "source_package_sha256", "record_end",
                                                         "source_files_sha256"}
            or parent["schema"] != "ptp-paper-parent-v1" or len(str(parent["source_package_sha256"])) != 64
            or str(parent["record_end"]) < str(identity.get("record_end"))):
        raise ValueError("paper parent binding mismatch")
    manifest = (root / "proof/records.sha256").read_bytes()
    if digest(manifest) != identity.get("records_sha256"):
        raise ValueError("paper manifest hash mismatch")
    entries = [line.split("  ", 1) for line in manifest.decode().splitlines()]
    published = {folder + "/" + name for folder in folders for name in NAMES}
    published |= {RISK + "/" + name for name in public_risk_names(root)} | set(PUBLIC_DOCS)
    archived = set(archive["files_sha256"])
    required = {"README.md", "STATUS.md", "scripts/verify.py", ".gitattributes", *published, *archived}
    if len(entries) != len(required) or {entry[1] for entry in entries} != required:
        raise ValueError("paper manifest inventory mismatch")
    for expected, relative in entries:
        if digest((root / relative).read_bytes()) != expected:
            raise ValueError("paper file hash mismatch: " + relative)
        if relative in archived and archive["files_sha256"][relative] != expected:
            raise ValueError("archived file changed: " + relative)
    for directory, expected in (("data", published), ("scripts", {"scripts/verify.py"}), (ARCHIVE, archived)):
        if {p.relative_to(root).as_posix() for p in (root / directory).rglob("*") if p.is_file()} != expected:
            raise ValueError("paper folder inventory mismatch: " + directory)
    if identity.get("series_ids") != list(PUBLIC_SERIES) or identity.get("record_start") != START:
        raise ValueError("public identity mismatch")
    status = (root / "STATUS.md").read_text(encoding="utf-8")
    for folder in folders:
        check_public_folder(root, folder, identity["record_end"])
        breach = json.loads((root / folder / "source_anchor.json").read_bytes()).get("kill_rule_breach")
        if breach is not None and "Kill rule breached for " + folder.split("/", 1)[1] + " on " + breach not in status:
            raise ValueError("kill-rule breach is not disclosed")
    check_public_risk(root, identity["record_end"])
    return []


def public_verify(root):
    """The public record's standalone check (scripts/verify.py of projection v6)."""
    root = Path(root)
    try:
        identity = json.loads((root / "proof/private_anchor.json").read_bytes())
        projection = identity.get("paper_projection")
        if not isinstance(projection, dict) or projection.get("schema") != PUBLIC_PROJECTION:
            raise ValueError("unsupported paper projection")
        return verify_public(root, identity, projection)
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as exc:
        return [str(exc)]


def public_main():
    import argparse
    from zoneinfo import ZoneInfo
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-current", action="store_true")
    parser.add_argument("--timezone", default="America/Chicago")
    parser.add_argument("--not-before", default="08:30")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    errors = public_verify(root)
    if args.require_current and not errors:
        now = datetime.now(ZoneInfo(args.timezone))
        end = json.loads((root / "proof/private_anchor.json").read_bytes())["record_end"]
        if now.strftime("%H:%M") >= args.not_before and end < (now.date() - timedelta(days=1)).isoformat():
            errors.append("stale display-through date: " + end)
    print(json.dumps({"status": "failed" if errors else "verified", "errors": errors}))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(public_main())
