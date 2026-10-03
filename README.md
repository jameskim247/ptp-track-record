# series-2: Hypothetical Backtest Record

Range: **2023-10-01 through 2026-09-29**.

- **Hypothetical backtest, development evidence only.** Every row is `retrospective_reconstruction`: a backtest computed after the fact by a rule whose components, weights and size were chosen while this same history was being inspected. Never traded and not paper-traded forward. Not realized performance, returns on capital, or evidence of capacity. No out-of-sample claim.
- **The rule.** An ensemble of 24 ERCOT PTP-obligation books that rank node pairs on persistent real-time minus day-ahead carry, with a volatility target computed from the book's own P&L through two days before each decision. Limits: at most 800 placed MWh a day, a 1-MW minimum on a 0.1-MW grid, and bids floored to $0.01. An order is awarded when the day-ahead spread is strictly below its bid. The full specification was frozen on 2026-10-02 and is published here only as a SHA-256 commitment (`proof/anchor.json`).
- **P&L** is USD per day, net of an estimated all-in cost of $0.40 per placed MWh, the same convention as series-01 (ERCOT charges no per-MWh fee on PTP obligations). `gross_pnl` is before that cost. Market impact is not modeled. `placed_mw` and `awarded_mw` are physical MWh; the column names follow series-01.
- **Prices.**
  - Decisions use prices as first published, so later ERCOT price corrections are invisible to them.
  - Settlement uses final prices: load zones and hubs from ERCOT reports NP4-180-ER and NP6-785-ER, resource nodes as first published.
  - Final resource-node prices were not available for 97 hours with location-specific ERCOT corrections, including January 24–26, 2026.
  - Zone and hub prices for 2026-09-27 to 09-29 are not yet in ERCOT's annual reports.
- **`partially_settled` rows: 86 days, 421.8 awarded MWh in total (82 days in 2025, 4 in 2026).** On these days some awarded orders have no real-time price in our data for a resource node or a DC tie.
  - P&L on these rows covers the priced orders and deducts the cost of every placed MWh.
  - `pending_awarded_mw` shows the awarded volume left unvalued; its outcome is unknown and not estimated.
  - These rows count in the cumulative and period statistics. All other rows are `settled`.
- **Proofs.** `decision_proof_id` and `settlement_proof_id` are SHA-256 digests of each day's order book and per-order settlement. Both are kept privately and are available on request. `proof_id` is the digest of the row itself.
- **Ratios** use daily USD P&L, sample SD and the square root of 365, as in series-01. `pnl_es10` is the mean of the worst tenth of days. Every summary row restarts drawdown at zero.
- **Known weaknesses:**
  - Against acceptance criteria fixed before this replay, the 2026 window fails one: second-half to first-half P&L with the best three days removed is 1.436, against a limit of 1.43.
  - October–December 2023 includes a −$69K day and a $72K drawdown.
  - Daily correlation with series-01's published 2026 record is 0.38. Against a replica of the series-01 rule it was 0.58 in both 2024 and 2025.
  - Descriptive only; no promotion claim.

Verify: `python3 scripts/verify.py` (see VERIFY.md). Coverage: STATUS.md.
