# Submission credit

`submission_credit` in each series' `daily.csv` (USD) is ERCOT's Day-Ahead Market
credit exposure for that day's PTP Obligation bids, computed as in ERCOT Nodal Protocols
4.4.10(6)(d):

- bid price above zero: MW x bid price + MW x P
- bid price zero or below: MW x P

P is the 90th percentile (parameter u, Protocols 4.4.10(10)) of the hourly positive price difference
between the source and sink Real-Time Settlement Point Prices over the previous 30 days. The day's
figure is the sum over every hourly bid.

Where the rule leaves a choice:

- Window: operating days D-31 to D-2, the last complete Real-Time days at the bid deadline on D-1.
- Hours: all 720 hours of the window. The rule names no hour, unlike the energy-bid and
  Ancillary Service rules beside it (4.4.10(6)(a), (b), (f)). Using only the same hour of day gives
  roughly a quarter more.
- Prices: hourly averages of the record's first-published Real-Time prices. A path without price
  history counts zero; that is under 0.5% of the exposure.

What it is not:

- Not collateral. ERCOT accepts DAM bids while their exposure fits the Counter-Party's DAM credit
  limit, ACLD = Financial Security - 110% x TPES - 110% x TPEA (Protocols 16.11.4.6(1)(b)). Without
  CRRs, TPES is the $200,000 Independent Amount (16.16.1), so the posting would need at least the
  day's submission credit + $220,000 + 110% of TPEA. TPEA, the exposure of awarded positions until
  they settle, is not modelled here.
- No expiring-CRR offsets (4.4.10(6)(d)(iii)-(iv)); the programme holds no CRRs.
- Parameters are those in the Protocols in force on 2026-10-16; ERCOT may change them.

`weekly.csv` and `monthly.csv` add the period's maximum; `summary.csv` the median and maximum.
