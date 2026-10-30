import pathlib
import sys
import unittest
from decimal import Decimal

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from fx.fees import transfer_fee  # noqa: E402


class TransferFee(unittest.TestCase):
    def test_small_amount_hits_minimum(self):
        self.assertEqual(transfer_fee(Decimal("50")), Decimal("2.00"))

    def test_mid_tier(self):
        self.assertEqual(transfer_fee(Decimal("5000")), Decimal("25.00"))

    def test_high_tier(self):
        self.assertEqual(transfer_fee(Decimal("20000")), Decimal("50.00"))

    def test_rejects_non_positive(self):
        with self.assertRaises(ValueError):
            transfer_fee(Decimal("0"))


if __name__ == "__main__":
    unittest.main()
