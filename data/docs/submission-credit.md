# Modeled submission credit

`submission_credit` estimates the credit used by submitted PTP Obligation bids, before awards. For each hourly order it adds MW × positive bid price and MW × the 90th percentile of positive source-minus-sink RT prices over D−31 through D−2, with physical-hour duration. The estimate uses the declared S1 hourly price observations and admitted corrections. Repeated-hour prices are represented by the record’s hourly average.

Missing path history contributes zero to this model and can understate credit usage. These are paper estimates, not ERCOT acceptance checks, total collateral, funding needs or a capital denominator. A desk must validate the current ERCOT parameters, its own awarded exposure and portfolio offsets. No expiring-CRR offsets are modeled.

Weekly and monthly tables report the period maximum; summary tables include median and maximum.
