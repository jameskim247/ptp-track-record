# Two-Series Modeled Paper Record

This repository contains two separately frozen, neutral modeled paper series.
It is not a brokerage statement, realized trading performance, or evidence of executable
capacity. Every dollar figure is modeled P&L.

Public range: **2026-01-01 through 2026-09-20**.

The primary result for each series uses its frozen limit prices. The same-book
always-clear result is a counterfactual used only to measure limit-price contribution.
Historical reconstruction and prospective shadow observations are labeled separately in
every daily file.

These numbered series belong to a new programme and do not continue the previous series performance. Research-only hypothetical observations; no promotion claim.

Evaluation policy: this launch is descriptive-only. No series is a preregistered promotion candidate; selecting a later winner cannot establish confirmation. Any future promotion study requires a separately frozen protocol and untouched cohort. Missing decisions and unsettled dates remain explicit; no backdated decisions, replacement dates or silently omitted losses are permitted.

These books share substantial signal lineage and are not independent sources of alpha. Their daily P&Ls are correlated; two series do not imply two diversified bets.

Read the two parts of this record differently. Rows before the prospective start are a **reconstruction**: they were computed after the fact from pinned inputs, and every daily file marks them `retrospective_reconstruction`. Rows from the prospective start are decisions committed to before their own gate. Only the second kind is a record of anything; the first is a backtest, and this one is worse than an ordinary backtest for the second series, because the research that chose it inspected these very dates.

Concretely: the second series was selected from nineteen candidate rules scored on 2026-H1 and the available 2026-H2. Its reconstructed 2026 rows are the window that selection ran on. They cannot evidence that it works, and a reader should treat that part of its curve as an illustration of the rule's shape rather than as performance. The first series was not selected that way: it continues an unchanged rule.

How these two were chosen, in full: the first series continues the identical frozen rule and execution adapter that the retired programme published as its series-02, so it is not a new strategy. Its earlier record is retained privately. The second is a separately identified challenger selected on September 19, 2026 from a search over nineteen candidate rules scored on the same already-inspected 2026 windows. Its apparent advantage over the first series is not statistically established, and the search that produced it cannot establish one.

Verification checks internal consistency across the files published here. Each day's decision is committed to, and hashed, before its gate, but those commitment receipts are retained privately rather than published, so a public reader sees the resulting ledgers and cannot confirm that timing from this repository alone. Private acknowledgements retain GitHub response times; they are not independently signed timestamp certificates. Public readers cannot independently reconstruct undisclosed trades or authenticate those private observations.

Cutover history: the September 10 merge also made six previously unpushed local legacy update commits reachable publicly. Preserving both histories did not mean both histories had previously been public. They are retained without rewriting Git history.

Retirement: the four-series programme that ran from September 10 to September 20, 2026 was closed in favour of this one. Nothing it published was deleted or restated. Its daily records and its commitment receipts are retained in full and privately, against the digest they were sealed with, and are available on request; they are no longer published here so that a closed programme is not displayed beside a live one. Two of its series had research predecessors that failed their historical acceptance gates; retirement does not reverse, and publication never reversed, those rejections.

Summary ratios use settled daily dollar P&L, not return on capital. Mean-to-standard-deviation uses sample SD and annualization by square root of 365. Sortino uses a zero-dollar daily target and downside squared deviations averaged over every settled day, also annualized by square root of 365. Win rate counts strictly positive days; profit factor divides positive P&L by absolute negative P&L. Undefined ratios are blank. Concentration fractions use positive total net P&L and may exceed one. Top-five exclusion removes the five largest daily P&Ls only for the explicitly labeled diagnostic; it never changes the published equity path.

Half-year rows are descriptive cuts of the inspected calendar. Their drawdown restarts equity at zero at the cut; the daily file retains continuous equity. Summary statistics exclude unsettled dates and disclose settled coverage. Comparison statistics use only dates settled in every series. A latest settled date does not imply earlier gaps are settled; STATUS shows the contiguous cutoff.

Explicit physical-MWh columns identify placed and awarded energy; the legacy `placed_mw` and `awarded_mw` columns are compatibility aliases in this programme. Modeled net P&L equals gross P&L less modeled fees. Fees are currently zero; impact and financing are omitted, unvalidated operating assumptions. Limit clearing is modeled, with no award at equality; these are not executed fills.
