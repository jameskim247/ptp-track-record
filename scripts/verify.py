#!/usr/bin/env python3
import csv,hashlib,io,json,math,statistics
from datetime import date,datetime,timedelta
from pathlib import Path
AUXILIARY_FILES = {'.gitignore': '862263fa1f46c20f0d1e4dac5ffcc75abd55c08211b2c3864c5f8764b9d87793'}
START = '2024-01-01'
PUBLIC_SERIES = ('pairs-100', 'pairs-50')
PUBLIC_DAILY = ('date', 'signal_date', 'status', 'pnl', 'cumulative_pnl', 'pnl_drawdown', 'placed_mw', 'awarded_mw', 'fill_rate', 'pending_awarded_mw', 'pairs', 'pair_hours', 'submission_credit', 'eligibility_snapshot_id', 'decision_proof_id', 'settlement_proof_id', 'source_proof_id', 'proof_id')
NAMES = ('daily.csv', 'weekly.csv', 'monthly.csv', 'summary.csv', 'source_anchor.json', 'publication.json')
RISK = 'data/risk'
PUBLIC_DOCS = ('data/docs/submission-credit.md', 'data/docs/stress.md')
STORM_RISK_NAMES = ('stress.csv', 'stress_daily.csv', 'source_anchor.json', 'publication.json')
RULE_CONTINUATION = '9999-12-31'
RULE_PROTOCOL = '4be885cef92eae12e0a867b2ecc99d5e625068392a1d8f898d8ef04a7778a9e0'
RULE = {'protocol_sha256': '4be885cef92eae12e0a867b2ecc99d5e625068392a1d8f898d8ef04a7778a9e0', 'frozen_at': '2026-11-10T17:55:00.286390+00:00', 'first_prospective_cutoff': ''}
EVIDENCE = {'development': 'Retrospective development reconstruction; historical publication vintages and tradability are not fully certified.', 'prospective': 'Paper continuation; no executed-trade or independent-validation claim.'}
ANCHOR_FIELDS = ['development_through', 'evidence_basis', 'files_sha256', 'kill_rule_breach', 'pair_cap', 'prospective_from', 'protocol_sha256', 'public_cost_per_placed_mwh', 'record_end', 'record_start', 'rule', 'schema', 'series', 'source_files_sha256', 'source_package_sha256']
ROOT_FIELDS = ['canonical_record_end', 'canonical_record_set_sha256', 'canonical_record_start', 'generation', 'paper_parent', 'paper_projection', 'record_end', 'record_start', 'records_sha256', 'registry_sha256', 'schema', 'series_ids']
PROJECTION_FIELDS = ['archive', 'documents', 'folders', 'prospective_from', 'record_start', 'schema']
PARENT_FIELDS = ['record_end', 'schema', 'source_files_sha256', 'source_package_sha256']
ARCHIVE_CONTRACT = {'files_sha256': {'archive/pairs-100/daily.csv': '7b4fc57dd7f5cb651da415364f553555f8d46dcb8aa995831b9bbaf8aed0279f', 'archive/pairs-100/monthly.csv': '9f7d23d1b1e46f9a3acade90b4c62b1440aaad70351103cce126ec854741ca57', 'archive/pairs-100/publication.json': 'de1e70eeffd2dc052b9bb043790356eaac3c152d9f754459705a2c7f434b363e', 'archive/pairs-100/source_anchor.json': 'e5b1bfab1637d8edd64db599cc303883d126a2d6b16643850a0a4053d24b2fd8', 'archive/pairs-100/summary.csv': '57be47b75171a9c39b3e395651f4d07e9a5be555fc08ba91c75e7b3f974d3a7c', 'archive/pairs-100/weekly.csv': 'e13c63f1dc7945c9c01c9ffb5b864879ee0e2b6d9fd8b8c9d1ae93903a35fde2', 'archive/pairs-50/daily.csv': '95dc55a06da519c43e2fb1b1a7ec1d3c725238bbff88fc534b3e3e9920fd64e7', 'archive/pairs-50/monthly.csv': '7d4d758a1e14bda7c579a7d034693a4e20c175d10b3321eb22d0a38741ba03a8', 'archive/pairs-50/publication.json': 'de1e70eeffd2dc052b9bb043790356eaac3c152d9f754459705a2c7f434b363e', 'archive/pairs-50/source_anchor.json': '94e3fdd0bb74bf13d4b7476f5982303c1399394c083821b6874d8a0978dc26e7', 'archive/pairs-50/summary.csv': '7cac5abba2de4fa9edb05e30f64ae710c8bc9b459f25a4b6987615398a216faa', 'archive/pairs-50/weekly.csv': 'a5366af3630175cb116bdcfdcbcbc0bdca8a813df5fdad2dc7d2fa131e8d2dc0', 'archive/pairs-500/daily.csv': '44a39472351463ae2c67efc79e5bc8f8d986d4bd9b4fcfa2d0b52b47cdbee7b8', 'archive/pairs-500/monthly.csv': '42dff4e6efac7bb2d8bf7c26ad2acb3fb7e571cbf0cf98d7b4cf6867c3b9a794', 'archive/pairs-500/publication.json': 'de1e70eeffd2dc052b9bb043790356eaac3c152d9f754459705a2c7f434b363e', 'archive/pairs-500/source_anchor.json': '1ea6be5c5ed8ccc1c39962f78a6f5634901ca63fbe0d886d6df66ceecc77d399', 'archive/pairs-500/summary.csv': '436575f82ceb2281b00455965a0dfbe497997f511424fd5583a217919201aff4', 'archive/pairs-500/weekly.csv': '2a4ce3bc5e52975b678aded7726006f366eaa343dc5b7545848d9f330776e488', 'archive/ptp-paper/daily.csv': 'c8b379aabc7d4fd5eaa4d0a7339686ed3fab66008272e0c1ffe080f61079b04c', 'archive/ptp-paper/monthly.csv': '6f557e6262e12ea728f125c1be56ad965b39f9eb428ae2b282243bc21695ddbd', 'archive/ptp-paper/publication.json': '81767aab27d0848dcb430a42032a06d07105a4fb3c7a970e2d6f15460571f608', 'archive/ptp-paper/source_anchor.json': 'afff003aaf3f4d82625c450f3613217e059a62d8ddbb0a3847236bb0539e16cd', 'archive/ptp-paper/summary.csv': 'a29e7c6b083c38f8d2bb04b3e2a4266ad71f6ac59853fe739833d77225630381', 'archive/ptp-paper/weekly.csv': 'e7f82a1a58204e06564a25cc80f4f9581ee7650390ba4bd1a7802dd671c6777a'}, 'last_published_day': '2026-10-17', 'retired_series': ['ptp-paper', 'pairs-500', 'pairs-100', 'pairs-50']}
STORM_CONTRACT = {'assumptions': {'coverage': 'Price coverage divides fully priced modeled awarded MWh by modeled awarded MWh. Award-node evidence requires both node/hour endpoints in actual market PTP awards; it is not actual awards to this strategy or exact directed-pair award coverage.', 'deenergized_lists': 'Frozen S1 outcome-only restriction; not reused as pre-deadline node-selection information.', 'grid': 'S1 causal monthly empirical DA ridge and frozen connected-basket cash model; not a physical network simulation.', 'nodes': 'Frozen S1 incumbent plus capped C/G additions. Historical operating-day eligibility is not fully certified; endpoint evidence is not proof of strategy execution.', 'prices': 'Frozen S1 pda/prt quote-bank contract; individual historical publication vintages remain incompletely certified.', 'settlement': 'Round-six-decimal price-taking DA spread <= bid; explicit outcome-only restriction. Unvalued awarded exposure is retained.', 'sizing': 'Continuous S1 history from 2021-01-01; no event-start reset. RAW_FULL cash and uniform-warning histories remain separate.'}, 'cost_basis': 'before costs; no market-impact model; current published quantities', 'development_only': True, 'events': {'uri': ['2021-02-14', '2021-02-19'], 'elliott': ['2022-12-22', '2022-12-25']}, 'evidence_basis': 'retrospective diagnostic; not executed trades or independent validation', 'method': 'historical_strategy_replay', 'run_date': '2026-11-10', 'schema': 'ptp-historical-storm-anchor-v1', 'source_bindings': {'audit_results_sha256': 'bffb7ccba5bad94a9ba9eb67f8bae4770e19e854ee5f1ba60c8fef34b0103635', 'elliott_order_records_sha256': 'b742afc6d57de69a017554d42532c1e3fd1ade136b01b2ca1c60f0a46b46b5d5', 'frozen_plan_sha256': '37f9a2a94b77511f826419beb926884edbd781284350fa053a3d8fef7d7ca749', 'replay_code_sha256': 'a1e990705f512cdfd8d6d444e38c2fba414cb3382c13ed53b19209c21983d01f', 'uri_order_records_sha256': 'c65b04e3476e3b7a22afc94672729ce37cc3d2e655b6a5892f58bcc8c5467354'}}
STORM_SNAPSHOT_SHA256 = '0fd627c116f149b9bac78fbecc9a43af3be18f2b4dc2546721ee8ea432e4bad4'
STORM_FILE_HASHES = {'stress.csv': 'bb6709e818220b6280cf55431218a837da1b634a87c68e657627fb16abe76c47', 'stress_daily.csv': '824b572cc81db323ccda7704d5a4622fddad6eba88cecde034dd4d80ce153c86'}
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
    # v6 public rows carry no gross column: P&L has no fees or costs, so there is nothing to split.
    split = ({"gross_pnl": round(math.fsum(r["gross_pnl"] for r in rows), 4),
              "costs": round(math.fsum(r["gross_pnl"] for r in rows) - total, 4)} if "gross_pnl" in rows[0] else {})
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


def unavailable_row(row, first):
    """A SEVU day published as unavailable: from `first` on, no orders, zero P&L and no eligibility snapshot."""
    return (row["status"] == "unavailable" and first is not None and row["date"] >= first
            and row["eligibility_snapshot_id"] == "" and row["pnl"] == row.get("gross_pnl", 0) == 0
            and row["placed_mw"] == row["awarded_mw"] == row["pending_awarded_mw"] == 0
            and row["pairs"] == row["pair_hours"] == 0 and row["submission_credit"] == 0)


def check_receipt(receipt, end):
    missing = (date.fromisoformat(receipt["checked_through"]) - date.fromisoformat(end)).days
    if (missing < 0 or receipt.get("missing_result_days") != missing
            or receipt.get("status") != ("current" if missing == 0 else "stale")
            or receipt.get("state") not in ("verified_source", "retained_verified_source")):
        raise ValueError("paper publication freshness mismatch")


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


def evidence_tables(daily):
    result=tables(daily)
    result['summary.csv']=[summary('development_backtest',daily)]+result['summary.csv']
    return result


def check_folder(root,folder,end):
    name=folder.split('/')[1];cap=int(name.split('-')[1]);anchor=json.loads((root/folder/'source_anchor.json').read_bytes());receipt=json.loads((root/folder/'publication.json').read_bytes())
    if set(anchor)!=set(ANCHOR_FIELDS) or anchor['schema']!='ptp-series-anchor-s1-v1' or anchor['series']!=name or anchor['pair_cap']!=cap:raise ValueError('Series schema mismatch')
    if anchor['record_start']!=START or anchor['record_end']!=end or anchor['development_through']!=end or anchor['prospective_from']!='':raise ValueError('Series evidence calendar mismatch')
    if anchor['protocol_sha256']!=RULE_PROTOCOL or anchor['rule']!=RULE or anchor['evidence_basis']!=EVIDENCE or anchor['public_cost_per_placed_mwh']!=0:raise ValueError('Series rule binding mismatch')
    package=anchor['source_package_sha256']
    if len(package)!=64 or any(c not in '0123456789abcdef' for c in package) or receipt['source_package_sha256']!=package:raise ValueError('Series source package mismatch')
    if set(anchor['source_files_sha256'])!={'daily.csv'} or len(anchor['source_files_sha256']['daily.csv'])!=64:raise ValueError('Source daily binding missing')
    hashes={n:digest((root/folder/n).read_bytes()) for n in NAMES if n.endswith('.csv')}
    if hashes!=anchor['files_sha256']:raise ValueError('Series file hash mismatch')
    data={n:read_rows((root/folder/n).read_bytes()) for n in hashes};check_public_daily(data['daily.csv'],end,cap);expected=evidence_tables(data['daily.csv'])
    if any(data[n]!=expected[n] for n in ['weekly.csv','monthly.csv','summary.csv']):raise ValueError('Series aggregate arithmetic mismatch')
    if receipt['record_start']!=START or receipt['record_end']!=end:raise ValueError('Series receipt calendar mismatch')
    check_receipt(receipt,end)


def verify_record(root):
    root=Path(root);identity=json.loads((root/'proof/private_anchor.json').read_bytes());projection=identity['paper_projection']
    if set(identity)!=set(ROOT_FIELDS) or set(projection)!=set(PROJECTION_FIELDS) or projection['schema']!='ptp-paper-projection-s1-v1':raise ValueError('Public root schema mismatch')
    if identity['series_ids']!=list(PUBLIC_SERIES) or identity['record_start']!=START or projection['record_start']!=START or projection['prospective_from']!='':raise ValueError('Public record identity mismatch')
    if projection['folders']!=['data/'+b for b in PUBLIC_SERIES]+[RISK] or projection['documents']!=list(PUBLIC_DOCS):raise ValueError('Public folder structure mismatch')
    if projection['archive']!=ARCHIVE_CONTRACT:raise ValueError('Original archive binding changed')
    parent=identity['paper_parent'];end=identity['record_end']
    if set(parent)!=set(PARENT_FIELDS) or parent['schema']!='ptp-paper-parent-v1' or parent['record_end']!=end or len(parent['source_package_sha256'])!=64:raise ValueError('Source parent mismatch')
    manifest=(root/'proof/records.sha256').read_bytes()
    if digest(manifest)!=identity['records_sha256']:raise ValueError('Manifest hash mismatch')
    entries=[line.split('  ',1) for line in manifest.decode().splitlines()];paths=[r[1] for r in entries]
    required={'README.md','STATUS.md','scripts/verify.py','.gitattributes',*ARCHIVE_CONTRACT['files_sha256'],*PUBLIC_DOCS,*('data/'+b+'/'+n for b in PUBLIC_SERIES for n in NAMES),*(RISK+'/'+n for n in STORM_RISK_NAMES)}
    required|=set(AUXILIARY_FILES)
    if len(paths)!=len(required) or set(paths)!=required:raise ValueError('Public inventory mismatch')
    for expected,path in entries:
        if digest((root/path).read_bytes())!=expected:raise ValueError('Public file hash mismatch: '+path)
        if path in AUXILIARY_FILES and expected!=AUXILIARY_FILES[path]:raise ValueError('Preserved root file changed')
        if path in ARCHIVE_CONTRACT['files_sha256'] and expected!=ARCHIVE_CONTRACT['files_sha256'][path]:raise ValueError('Original archive bytes changed')
    for directory in ['data','scripts','archive']:
        actual={p.relative_to(root).as_posix() for p in (root/directory).rglob('*') if p.is_file()}
        if actual!={p for p in required if p.startswith(directory+'/')}:raise ValueError('Extra/missing public files: '+directory)
    for b in PUBLIC_SERIES:
        check_folder(root,'data/'+b,end)
        if json.loads((root/'data'/b/'source_anchor.json').read_bytes())['source_package_sha256']!=parent['source_package_sha256']:raise ValueError('Book/source parent binding differs')
    check_historical_storm_risk(root)
    return identity


def main():
    import argparse
    from zoneinfo import ZoneInfo
    parser=argparse.ArgumentParser();parser.add_argument('--require-current',action='store_true');parser.add_argument('--timezone',default='America/Chicago');parser.add_argument('--not-before',default='08:30');args=parser.parse_args()
    try:
        identity=verify_record(Path(__file__).resolve().parents[1]);now=datetime.now(ZoneInfo(args.timezone))
        if args.require_current and now.strftime('%H:%M')>=args.not_before and identity['record_end']<(now.date()-timedelta(days=1)).isoformat():raise ValueError('Stale display-through date: '+identity['record_end'])
        result={'status':'verified','errors':[]}
    except (OSError,ValueError,KeyError,TypeError,csv.Error) as exc:result={'status':'failed','errors':[str(exc)]}
    print(json.dumps(result));return int(bool(result['errors']))

if __name__=='__main__':raise SystemExit(main())
