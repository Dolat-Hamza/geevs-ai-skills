# FX fee practice project

A tiny fee calculator for trying the agent team safely. It works out the fee on a money transfer from the price list below.

- `fx/fees.py`: the fee calculation
- `tests/`: automatic checks (run with `python3 -m unittest discover -s tests`)

## Pricing table
| Amount (GBP) | Fee |
|---|---|
| under 1,000 | 1.0% |
| 1,000 to under 10,000 | 0.5% |
| 10,000 and above | 0.25% |
Minimum fee 2.00 GBP. Fees round half-up to 2 decimals.
