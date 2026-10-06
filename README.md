# series-2: Hypothetical Backtest Record

Range: **2023-10-01 through 2026-09-29**.

**Daily publication:** a scheduled GitHub job runs at 14:17 and 22:17 UTC (with manual retry available).
Its current coverage and calculation readiness are published in [proof/publication.json](proof/publication.json).
The original package was a one-time export. A restored, hash-pinned E24 producer supports daily continuation on GCP,
with immutable reconstructed books and sizing references, and retries for unpriced settlements.
The publication job consumes verified result packages through a keyless, read-only GCS identity.
Its coverage receipt and freshness check expose missing result dates; unavailable prices remain unvalued.
It does not run the older GCP `series-02` lane or substitute that lane's results for E24.

- **Hypothetical backtest, development evidence only.** Every row is `retrospective_reconstruction`: a backtest computed after the fact by a rule whose components, weights and size were chosen while this same history was being inspected. Never traded and not paper-traded forward. Not realized performance, returns on capital, or evidence of capacity. No out-of-sample claim.
- **The rule.** An ensemble of 24 ERCOT PTP-obligation books that rank node pairs on persistent real-time minus day-ahead carry, with a volatility target computed from the book's own P&L through two days before each decision. Limits: at most 800 placed MWh a day, a 1-MW minimum on a 0.1-MW grid, and bids floored to $0.01. An order is awarded when the day-ahead spread is strictly below its bid. The full specification was frozen on 2026-10-02 and is published here only as a SHA-256 commitment (`proof/anchor.json`).
- **P&L** is USD per day, net of an estimated all-in cost of $0.40 per placed MWh, the same convention as series-01 (ERCOT charges no per-MWh fee on PTP obligations). `gross_pnl` is before that cost. Market impact is not modeled. `placed_mw` and `awarded_mw` are physical MWh; the column names follow series-01.
- **Prices.**
  - Original history through 2026-09-29: decisions use the restored first-published price seed, and settlement uses the restored final-price seed (zones/hubs from NP4-180-ER and NP6-785-ER; resource nodes as first published).
  - From 2026-09-30: the same frozen rule and reconciled sizing state continue using qualified ERCOT prices observed on GCP. The original price seeds and decision books are unchanged. Reconstructed books are frozen when generated; later settlement data can resolve pending orders or restate values.
  - On 2026-10-06, 155 missing historical node-hour prices were recovered from a disclosed Modo public secondary copy of ERCOT's interval quotes. Exact cent quotes were decoded from float32 storage and checked against retained official intervals, with no conflicting overlap. Existing prices, orders, awards, weights and sizing were not changed. Settlement-only restatement resolved 82 partial days, adding $1,543.4450 to historical P&L; the superseded manifest and private evidence digest are recorded in `proof/anchor.json`. This is retrospective evidence, not a prospective validation.
  - These later reconstructions are also development/backtest evidence. Their inputs were not captured before the original operating-day cutoff, and settlement prices are the latest observed quotes, not a guarantee that ERCOT will never correct them.
  - Final resource-node prices were not available for 97 hours with location-specific ERCOT corrections, including January 24–26, 2026.
  - Zone and hub prices for 2026-09-27 to 09-29 are not yet in ERCOT's annual reports.
- **`partially_settled` rows after the 2026-10-06 recovery: 4 days, 150.2 awarded MWh in total.** Dates: 2025-12-04, 2026-01-08, 2026-06-04 and 2026-07-09. Some awarded orders still lack a quarter-hour real-time price in both the checked feed and official archive listing. A three-interval average is not substituted for a complete hour.
  - P&L on these rows covers the priced orders and deducts the cost of every placed MWh.
  - `pending_awarded_mw` shows the awarded volume left unvalued; its outcome is unknown and not estimated.
  - These rows count in the cumulative and period statistics. All other rows are `settled`.
- **Proofs.** `decision_proof_id` and `settlement_proof_id` are SHA-256 digests of each day's order book and per-order settlement. Both are kept privately and are available on request. `proof_id` is the digest of the row itself.
- **Ratios** use daily USD P&L, sample SD and the square root of 365, as in series-01. `pnl_es10` is the mean of the worst tenth of days. Every summary row restarts drawdown at zero.
- **Known weaknesses (research measurements before the 2026-10-06 settlement recovery, not revalidated acceptance results):**
  - Against acceptance criteria fixed before this replay, the 2026 window fails one: second-half to first-half P&L with the best three days removed is 1.436, against a limit of 1.43.
  - October–December 2023 includes a −$69K day and a $72K drawdown.
  - Daily correlation with series-01's published 2026 record is 0.38. Against a replica of the series-01 rule it was 0.58 in both 2024 and 2025.
  - Descriptive only; no promotion claim.

Verify: `python3 scripts/verify.py` (see VERIFY.md). Coverage: STATUS.md.
