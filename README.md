# Two-Series Hypothetical Paper Record

Range: **2026-01-01 through 2026-09-25**.

- **Hypothetical.** Frozen books paper-settled against published ERCOT prices; never traded. Not realized performance, returns on capital, or evidence of capacity.
- **P&L** is USD per series-day, net of modeled fees (currently zero); market impact and financing are excluded. Unsettled values are blank, never zero.
- **Two kinds of row** (`evidence_basis`): `retrospective_reconstruction` is a backtest computed after the fact; `prospective_shadow` (from 2026-09-22) was decided before each day's cutoff. Decision timestamps are kept privately.
- **Selection bias.** series-02 was chosen on 2026-09-19 from 19 candidate rules scored on these 2026 dates, so its reconstructed rows illustrate the rule and cannot evidence that it works; its edge over series-01 is not statistically established. series-01 continues an unchanged earlier rule.
- The series are correlated, not independent sources of alpha. Descriptive only; no promotion claim.
- The four-series programme of 2026-09-10 to 09-20 was retired. Its records are retained privately and unchanged, and are available on request; two of its series had research predecessors that failed their historical acceptance gates.
- **History revised** (universe timing correction, 2026-01-01 to 2026-09-19); superseded digest `244b3a63f8828a6a85e2cfd1b3255b7764752d31014861011ce9abd856ecc2f9`. Still development-only evidence. It removed hindsight: the superseded node universe used coverage from after some decision dates.
- Rows through 2026-09-19 use 1,007 nodes; later rows keep the 1,069-node operational universe.
- **History revised** (input recovery, 2026-01-01 to 2026-09-19); superseded digest `b4a31d27b20afec3089adb2fba87e925d8a23692f67dbae9d56b14292b0987aa`. Still development-only evidence.
- **Ratios** use daily USD P&L, sample SD and square root of 365. `pnl_es10` is the mean of the worst tenth of settled days. Half-year rows restart drawdown at zero.
- Columns were renamed on 2026-09-25 (`modeled_pnl` became `pnl`, and so on); values did not change.

Verify: `python3 scripts/verify.py` (see VERIFY.md). Coverage: STATUS.md.
