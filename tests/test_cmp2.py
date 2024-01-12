import unittest

import numpy as np
import pandas as pd

import os
print(os.getcwd())

from src.call_market_price2 import MarketPrice2, ensure_tuples
# from rounds.models import *

class TestOrder:
    def __init__(self):
        self.price = None
        self.quantity = None

def o(price=None, quantity=None):
    _o = TestOrder()
    _o.price = price
    _o.quantity = quantity
    return _o


# noinspection DuplicatedCode
class TestCallMarketPrice2(unittest.TestCase):


    def test_ensure_tuples(self):
        bids = [o(price=10, quantity=20),
                o(price=11, quantity=21)]
        offers = [o(price=5, quantity=15),
                  o(price=6, quantity=16)]

        b_tup = [(10, 20), (11, 21)]
        o_tup = [(5, 15), (6, 16)]

        # Test object
        MarketPrice2(None, None)

        # Test with lists of Orders
        b_actual, o_actual = ensure_tuples(bids, offers)
        self.assertEqual(b_actual, b_tup)
        self.assertEqual(o_actual, o_tup)

        # Test with lists of tuples
        b_actual, o_actual = ensure_tuples(b_tup, o_tup)
        self.assertEqual(b_actual, [(10, 20), (11, 21)])
        self.assertEqual(o_actual, [(5, 15), (6, 16)])

        # Test with lists of None
        b_actual, o_actual = ensure_tuples(None, None)
        self.assertEqual([], b_actual)
        self.assertEqual([], o_actual)



    def test_market_price_volume(self):
        # Set up
        b_vol = [(1, 1), (2, 2)]
        o_vol = [(1, 1), (2, 2)]
        mp = MarketPrice2(b_vol, o_vol)

        # Execute
        price, volume = mp.get_market_price()  

        # Assert
        self.assertEqual(price, 2)
        self.assertEqual(volume, 2)

    def test_market_price_resid(self):
        # Set up
        b_resid = [(4, 2), (6, 1)]
        o_resid = [(4, 1), (6, 1)]
        mp = MarketPrice2(b_resid, o_resid)

        # Execute
        price, volume = mp.get_market_price()  

        # Assert
        self.assertEqual(price, 5)
        self.assertEqual(volume, 1)

    def test_market_price_pressure(self):
        # Set up
        b_press = [(55, 4)]
        o_press = [(50, 10)]
        mp = MarketPrice2(b_press, o_press)

        # Execute
        price, volume = mp.get_market_price()  

        # Assert
        self.assertEqual(price, 52)
        self.assertEqual(volume, 4)

    def test_market_price_ref(self):
        # Set up
        b_ref = [(5, 10), (6, 10)]
        o_ref = [(5, 10), (6, 10)]
        mp = MarketPrice2(b_ref, o_ref)

        # Execute
        price, volume = mp.get_market_price()  

        # Assert
        self.assertEqual(price, 6)
        self.assertEqual(volume, 10)

    def test_market_price_no_trade(self):
        # Set up
        b_no_trade = [(1, 1)]
        o_no_trade = [(10, 1)]
        mp = MarketPrice2(b_no_trade, o_no_trade)

        # Execute
        price, volume = mp.get_market_price()  

        # Assert
        self.assertEqual(price, 6)
        self.assertEqual(volume, 0)

    # noinspection DuplicatedCode
    def test_get_market_price_no_orders(self):
        bids = [o(price=10, quantity=20),
                o(price=11, quantity=21)]
        offers = [o(price=5, quantity=15),
                  o(price=6, quantity=16)]

        # Offers None
        mp = MarketPrice2(bids, None)
        p, v = mp.get_market_price()
        self.assertEqual(p, 11)
        self.assertEqual(v, 0)
        self.assertTrue(mp.has_bids)
        self.assertFalse(mp.has_offers)

        # Offers Empty
        mp = MarketPrice2(bids, [])
        p, v = mp.get_market_price()
        self.assertEqual(p, 11)
        self.assertEqual(v, 0)
        self.assertTrue(mp.has_bids)
        self.assertFalse(mp.has_offers)

        # Bids None
        mp = MarketPrice2(None, offers)
        p, v = mp.get_market_price()
        self.assertEqual(p, 5)
        self.assertEqual(v, 0)
        self.assertFalse(mp.has_bids)
        self.assertTrue(mp.has_offers)

        # Bids Empty
        mp = MarketPrice2([], offers)
        p, v = mp.get_market_price()
        self.assertEqual(p, 5)
        self.assertEqual(v, 0)
        self.assertFalse(mp.has_bids)
        self.assertTrue(mp.has_offers)

        # Both None
        mp = MarketPrice2(None, None)
        p, v = mp.get_market_price()
        self.assertIsNone(p)
        self.assertEqual(v, 0)
        self.assertFalse(mp.has_bids)
        self.assertFalse(mp.has_offers)

        # Both Empty
        mp = MarketPrice2([], [])
        p, v = mp.get_market_price()
        self.assertIsNone(p)
        self.assertEqual(v, 0)
        self.assertFalse(mp.has_bids)
        self.assertFalse(mp.has_offers)


if __name__ == '__main__':
    unittest.main()
