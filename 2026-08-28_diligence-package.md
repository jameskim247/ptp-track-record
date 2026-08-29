# PTP Modeled Shadow Record — Buyer Diligence Package

**Package date:** 2026-08-28

**Public series:** `cc3-s4r-v2-fixed-path-2x-g1600-r80-k020`

**Evidence class:** retrospective diagnostic / development-only
**Repository:** https://github.com/jameskim247/ptp-track-record

> **This repository contains a retrospective, fixed-composition quantity-scaling
> diagnostic. It is a modeled shadow record, not a brokerage statement or evidence of
> live realized trading performance. It does not, by itself, establish executable
> returns, capacity, slippage, or allocator-level performance.**

## 1. Executive note

The repository publishes a calendar-contiguous modeled shadow series from 2026-02-01.
The current public series doubles the quantities of a selected 800 MW fixed-path model;
it is not a 1,600 MW allocator re-solve. The model family and published arm were selected
after outcomes in 2025 H1, 2025 H2, and 2026 H1 were inspected. Consequently the entire
published series is development evidence, not out-of-sample confirmation or promotion
evidence. There is no brokerage, clearing-account, or third-party execution evidence in
this package.

The largest modeled loss was **July 22 modeled P&L of −$102,171.13**. July 23 modeled
P&L was **−$50,212.64**, for **−$152,383.77 two-day modeled P&L**. Those outcomes
remain in the original series. The package does not wait for recovery and does not replace
them with a revised backtest.

What can be verified publicly: exact repository bytes, daily proof identifiers, calendar
continuity, statuses, and deterministic daily-to-weekly/monthly/summary derivations. The
private anchor binds the public aggregate files to the hash of the private canonical
manifest. Position-level parquet evidence and canonical daily records can be made available
under NDA, but are not independently attested by a broker or administrator.

## 2. Ready-to-send buyer message

Subject: PTP modeled shadow record and diligence package

> I am sharing the complete repository and diligence note for the PTP modeled shadow
> record: https://github.com/jameskim247/ptp-track-record
>
> This repository contains a retrospective, fixed-composition quantity-scaling diagnostic.
> It is a modeled shadow record, not a brokerage statement or evidence of live realized
> trading performance. It does not, by itself, establish executable returns, capacity,
> slippage, or allocator-level performance. Every dollar figure is modeled P&L. The package
> includes the full current drawdown, the July 22–23 incident analysis, methodology and
> change history, verification steps, and unresolved limitations.

## 3. Verification on Windows and Linux

From a fresh checkout with Python 3.11 or later:

```text
git clone https://github.com/jameskim247/ptp-track-record.git
cd ptp-track-record
python scripts/verify.py
```

On Linux, `python3 scripts/verify.py` is equivalent. `.gitattributes` forces LF for every
hashed CSV, JSON, Markdown, Python, and YAML file, including ordinary Windows checkouts.
The GitHub Actions verification job runs on both `ubuntu-latest` and `windows-latest`.
The optional freshness command is documented in `VERIFY.md`; it is time-dependent.

## 4. Capital, exposure, and sizing methodology

### Capital base and return measures

No defensible capital base was frozen before the outcomes were inspected. Starting capital,
available capital, deployed cash, collateral, reinvestment, compounding, and loss beyond a
stated capital base were not defined for this non-executable diagnostic. A denominator has
therefore not been reverse-engineered. Total/monthly modeled return, percentage drawdown,
return volatility, conventional Sharpe/Sortino, worst-day percentage of capital, and
capital-utilization ratios are **not available**. Dollar modeled-P&L dispersion statistics
are diagnostics only and must not be described as return statistics.

### Position-sizing rule

The public version is `cc3-s4r-v2-fixed-path-2x-g1600-r80-k020`. It takes the frozen paths
and quantities from selected arm `s4r_g800_r40_k020` and applies a 2.0 quantity multiplier.
The declared modeled gross is 1,600 MW, replacement ceiling 80 MW, and load scale 0.2.
Composition is fixed; the allocator is not rerun at 1,600 MW. Orders may contain multiple
tranches and modeled fills depend on the stored day-ahead price versus the tranche limit.
The underlying arm uses the `cc3-s4r-within-day-rank-overlay-v2` replacement mechanism;
its full private order and decision artifacts are required to reproduce each quantity.

This version was made the publication default on 2026-08-15, after all currently published
outcomes through that date were available or reconstructable. It was therefore not frozen
before the evaluated outcomes. The public repository alone does not disclose minimum order
size, every upstream confidence/liquidity input, or a complete dated history of upstream
signal-rule changes. Those are unresolved diligence items, not assumed facts.

### Exposure definitions and availability

- **Intended gross MW:** sum of absolute submitted path MW across all tranches and hours.
- **Modeled-filled gross MW:** sum of absolute MW for tranches whose modeled fill flag is true.
- **Maximum concurrent gross MW:** maximum intended gross MW in any delivery hour.
- **Peak single-tranche MW:** maximum absolute MW in one order tranche.
- **Net nodal MW:** signed injections minus withdrawals by settlement point; not published for
  the full record. Path MW must not be mistaken for dollars of capital at risk.
- **Market/component exposure:** ERCOT point-to-point congestion paths; baseline and S4R
  replacement components are separately retained in private evidence.
- **Capital utilization, leverage, contingent liability, collateral:** unavailable because
  no capital/collateral model was specified.

The public daily ledger does not contain daily exposure fields. The private incident evidence
supports the July values in section 6. A complete daily exposure schedule for the full series
remains required before any capital-efficiency or capacity claim.

## 5. Capacity and execution assumptions

The record uses modeled fills. It has no audited order submission, award, fee, collateral,
latency, or settlement evidence. The canonical records explicitly label fill audit status
`unavailable_modeled_replay`. No participation-rate study, market-depth model, price-impact
curve, commission schedule, latency distribution, position-limit review, collateral model,
or settlement-credit analysis has been frozen for the 1,600 MW notional diagnostic.

| Scenario | Assumption | Defensible capacity conclusion |
|---|---|---|
| Conservative | No unverified modeled fill is treated as executable | 0 MW established capacity |
| Base | Stored modeled fills, but no impact/slippage/collateral model | Capacity not estimable |
| Optimistic | All stored modeled fills at modeled prices | Arithmetic upper diagnostic only; not executable capacity |

These are evidence bounds, not promises or forecasts. Numeric executable capacity requires
market-depth data, frozen participation limits, fees, slippage/impact, fill probability,
latency, limits, and collateral constraints evaluated without outcome reuse.

## 6. July 22–23 incident memo

### Facts and reconciliation

Both days are `retrospective_causal_replay`, `promotion_evidence_eligible=false`, with modeled
fills and no fill audit. The rule ran as documented: fixed-path 2× quantities, modeled
day-ahead fill logic, and realized market prices used in retrospective settlement. Private
decision and settlement manifests are immutable and hash-linked to the canonical records.

| Date | Modeled tranches | Intended gross MW | Modeled-filled gross MW | Max concurrent gross MW | Peak tranche MW | Published modeled P&L |
|---|---:|---:|---:|---:|---:|---:|
| 2026-07-22 | 784 | 1,600 | 1,574 | 276 | 6 | −$102,171.13 |
| 2026-07-23 | 796 | 1,600 | 1,598 | 222 | 4 | −$50,212.64 |
| **Two days** | **1,580** | — | — | — | — | **−$152,383.77** |

Position-row sums before currency rounding are −$102,171.128 and −$50,212.638.
The two half-cent values round to the published daily cents and reconcile exactly. The full
position evidence is stored privately as each day's `s4r_settlement.parquet`; its SHA-256 is
`ee5656ebbb9f2a19b401cb12c06c55ffa21c72bd43110a38c8f75bb19d4547ff`
for July 22 and `6249e50a20faac8a2e0a9ded9a930efe61e8b69064faeedc492ae51d654013ee`
for July 23.

| Date / contribution group | Modeled P&L |
|---|---:|
| Jul 22 HE22 | −$32,210.83 |
| Jul 22 HE23 | −$53,018.84 |
| Jul 22 all other hours | −$16,941.46 |
| **Jul 22 total** | **−$102,171.13** |
| Jul 23 HE3–8 | −$47,201.57 |
| Jul 23 all other hours | −$3,011.07 |
| **Jul 23 total** | **−$50,212.64** |

The ten largest individual Jul 22 losses sum to −$7,215.62; all are filled 2 MW HE22
tranches into memo-local alias `Sink S1`, each contributing between −$717.99 and
−$731.17. The ten largest Jul 23 losses sum to −$3,376.56; the two largest are filled
4 MW HE21 tranches on memo-local alias `Path P1`, each −$502.90. These top-position
summaries plus the residual reconcile to the position-row sums. The aliases are stable
across both incident days and resolve to exact settlement-point identities in the ranked
position rows; those identities and every position row remain in the hash-bound NDA
evidence rather than the public repository.

### Cause classification

**Verified:** intended model behavior; correlated temporal exposure; retrospective modeling
artifact. July 22 HE22–23 produced −$85,229.67, 83.42% of the day, with adverse modeled
real-time congestion relative to day-ahead prices. The result followed the stored modeled
rules. Calling it a statistical tail event, regime change, liquidity failure, or excessive
sizing would require a frozen ex-ante reference distribution or risk budget that does not
exist. No external market event has been independently linked as a cause.

**Not established:** data-quality defect, implementation defect, operational error, live
liquidity/slippage failure, or brokerage loss. Hash reconciliation shows artifact integrity;
it does not prove the absence of a modeling bug. No software or data anomaly specific to
either day is documented in the reviewed evidence.

### Controls in force

| Control | Pre-incident status | Assessment |
|---|---|---|
| Declared gross target | 1,600 MW fixed-composition notional | Applied; not a capital-derived risk limit |
| Replacement ceiling | 80 MW | Applied at policy level; did not prevent temporal concentration |
| Per-tranche cap | No separately frozen capital-based cap found | Did not exist as a documented risk control |
| Correlation/temporal cap | None documented | Did not exist |
| Daily loss/drawdown limit | None documented for retrospective replay | Could not trigger retrospectively |
| Stop/de-risk/kill switch | None applicable to non-executable replay | Could not trigger |
| Liquidity filter | No frozen executable-liquidity control found | Did not exist for capacity validation |
| Manual intervention | None applicable to immutable historical replay | Could not trigger |

### Subsequent changes

No economic mitigation was applied to or used to rewrite the published history. On
2026-08-17, candidate hour exclusions, node exclusions, weekend scaling, MW caps, volatility
targeting, and other loss-day mitigations were evaluated after inspecting outcomes. They are
development-only and cannot confirm themselves. The only subsequent changes represented in
this public package are reporting, verification, and disclosure controls dated 2026-08-28;
they do not change modeled P&L. Owner: James Kim / repository owner. Expected effect: lower
diligence and verification risk, with no modeled performance effect.

## 7. Model and methodology change log

| Version / commit | Decision / effective date | Owner | Category and reason | Data available | Recomputed history? | First prospective observation |
|---|---|---|---|---|---|---|
| `cc3-s4r-v2` / `30b80de1` | 2026-08-13 | James Kim | Signal/reporting: build verified retrospective S4R-v2 record | Outcomes through 2026-08-12 | Yes | None established |
| `cc3-s4r-v2` / `847e5156` | 2026-08-13 | James Kim | Reporting: homogeneous replay rebuild | Historical outcomes inspected | Yes | None established |
| fixed-path 2× / `41336809` | 2026-08-15 | James Kim | Position sizing: make 2× quantity diagnostic publication default | Outcomes through 2026-08-14 available | Yes | None established |
| fixed-path 2× / `3ae3faae` | 2026-08-15 | James Kim | Sizing/lineage: bind history to frozen paths | Historical outcomes inspected | Yes | None established |
| diligence-remediation / this worktree | 2026-08-28 | James Kim / preparer | Reporting and verification only: LF policy, cross-OS CI, buyer framing | Full public record through 2026-08-28 | No economic recomputation; proof IDs/hashes regenerated for labeling/bytes | Not applicable |

The methodology responsible for the current public series is labeled
`cc3-s4r-v2-fixed-path-2x-g1600-r80-k020`; its publication choice was frozen on 2026-08-15,
after outcome inspection. There is no genuinely prospective, untouched promotion segment in
this series. Later calendar observations are still shadow/development evidence because no
complete prospective protocol and multiplicity rule were preregistered. Prior adverse
outcomes remain accessible in the daily ledger. Any revised economic model must receive a
new version and separately labeled prospective/shadow record; it must not overwrite this one.

### Proof restatement of 2026-08-28

Before this date the public ledger used the column names `realized_pnl`,
`cumulative_pnl`, and `drawdown`, and two dispersion ratios were named
`sharpe_daily` and `sortino_daily`. Those names implied realized trading results and
return-based risk ratios, neither of which this record establishes. They were renamed to
`modeled_pnl`, `cumulative_modeled_pnl`, `modeled_pnl_drawdown`,
`modeled_pnl_mean_to_stdev`, and `modeled_pnl_mean_to_downside_deviation`.

A daily `proof_id` is the SHA-256 of the row's column names together with its values, so
renaming the columns necessarily changed every daily proof identifier. **209 of 209 daily
proof identifiers changed. 0 of 209 daily economic values changed.** No modeled P&L,
cumulative total, drawdown, date, or status was altered, added, or removed. The binding to
the private canonical manifest is also unchanged:
`canonical_manifest_sha256 = bd24caa50cc83e0fb0e0e169a24afac02ba8adf114a5ead70df44c042993fb29`
both before and after.

The pre-restatement public digests are published here so any earlier attestation stays
checkable. They are the contents of `proof/records.sha256` at commit `0f160e1`:

| Path | Pre-restatement SHA-256 |
|---|---|
| `data/daily.csv` | `fe5294ccc3aae0b4c7e9a96841236fc199b8c933df7c758347cbb29d4839a704` |
| `data/weekly.csv` | `67ca5c87f24eabd4b94a132bae27a5c0c42935d7ae5609b024488de45ca4db84` |
| `data/monthly.csv` | `8c0705a4de732d6f5d2e641f8973761985a3650aea981dc8b2f1619c72c3e95c` |
| `data/summary.csv` | `aaaa2c7d0b1758ca819ab8084ac886e4e71b6bcd5ab6ff89e596f2fb66203429` |
| `proof/private_anchor.json` | `f3ee89d08c26c7edc5968a960c2c0554e843f9f92b27e781d5dc2e62e3ef83cd` |

Any reviewer can confirm the equivalence claim directly from this repository's history:

```bash
git show 0f160e1:data/daily.csv > /tmp/daily_before.csv
python3 - <<'EOF'
import csv
old=list(csv.DictReader(open('/tmp/daily_before.csv',newline='',encoding='utf-8')))
new=list(csv.DictReader(open('data/daily.csv',newline='',encoding='utf-8')))
rename={'realized_pnl':'modeled_pnl','cumulative_pnl':'cumulative_modeled_pnl','drawdown':'modeled_pnl_drawdown'}
strip=lambda r,m: {m.get(k,k):v for k,v in r.items() if k!='proof_id'}
print('economic payload identical:', [strip(r,rename) for r in old]==[strip(r,{}) for r in new])
print('proof ids changed:', sum(a['proof_id']!=b['proof_id'] for a,b in zip(old,new)), 'of', len(old))
EOF
```

## 8. Independent evidence and remaining limitations

No independently verifiable live or third-party performance evidence was identified for
this package. Git commits, file hashes, and the private anchor verify repository lineage and
byte integrity, not market execution or economic truth.

Remaining unanswered items:

1. No defensible capital, collateral, leverage, or contingent-liability denominator.
2. No full-series public daily exposure schedule.
3. No audited orders, awards, fills, fees, commissions, slippage, latency, or settlements.
4. No executable capacity study or frozen market-liquidity assumptions.
5. No untouched prospective promotion cohort; the model family is outcome-inspected.
6. Position-level incident evidence remains private and is not third-party attested.
7. No verified external-event attribution for July 22–23.
8. No complete upstream model-change inventory predating the current publisher lineage.

## Reproduce

```text
# Public verification (fresh checkout; Python 3.11+; no third-party packages)
python scripts/verify.py
python scripts/verify.py --require-current --timezone America/Chicago --not-before 08:30
```

**Commit/Worktree:** base `0f160e1`; `.worktrees/track-record-buyer-diligence`

**Private incident artifacts:** `out/track-record/cc3-s4r-v2-fixed-path-2x/days/2026-07-22/evidence/s4r_settlement.parquet` and corresponding `2026-07-23` path

**Public verification artifacts:** `proof/records.sha256`, `proof/private_anchor.json`
