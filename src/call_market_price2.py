from enum import Enum
from operator import attrgetter



class OrderType(Enum):
    """
        Enumeration representing the order type BID/OFFER
    """
    BID = -1
    OFFER = 1


class Principle(Enum):
    """
    Enumeration for the market principle used to determine the market price.
    These are set forth according to:  Sun et al. (2010)
    https://www.researchgate.net/publication/241567616_Algorithm_of_Call_Auction_Price
    """
    VOLUME = 1
    RESIDUAL = 2
    PRESSURE = 3
    REFERENCE = 4
    NO_ORDERS = 5


def ensure_tuple(obj):
    if type(obj) == tuple:
        return obj
    else:
        return int(obj.price), obj.quantity



def ensure_tuples(bids, offers):
    # Ensure input data is in the form of price/quant tuples
    b = [ensure_tuple(o) for o in bids] if bids else []
    o = [ensure_tuple(o) for o in offers] if offers else []

    return b, o


class MarketPrice2:
    """
    Implementation of the Call Market price algorithm described by: Sun et al. (2010)
    https://www.researchgate.net/publication/241567616_Algorithm_of_Call_Auction_Price
   
    Usage:
       mp = MarketPrice(bids, offers)
       price, volume = mp.get_market_price()

       The bids and offers can be either lists of Orders or (price/quantity) tuples.

       Parameters:
       bids, offers:   The bids and offers passed into the constructed. They will be lists
                        of (price/quantity) tuples
        has_bids, has_offers:  True if the bids or offers (respectively) are non_null and
                            non-empty.
        price_df:  The pandas DataFrame that is used to process the price.  Accessing this
                    is useful for debugging since is contains a history of the algorithm's
                    progress
        final_principle:  The last Principle that the algorithm attempted to apply
    """

    def __init__(self, bids, offers):
        _bids, _offers = ensure_tuples(bids, offers)
        self.bids, self.offers = _bids, _offers

        self.has_bids =  len(_bids) > 0
        self.has_offers = len(_offers) > 0
        
        keyed_bids = [{'t': 'b', 'p': x[0], 'q': x[1]} for x in self.bids]
        keyed_offers = [{'t': 'o', 'p': x[0], 'q': x[1]} for x in self.offers]
        self.all_orders = sorted(keyed_bids+ keyed_offers, key=lambda x: x['p'])


        self.csq = None
        self.cbq = None



    def generate_cxq(self):
 
        # working_csq = 0
        # working_cbq = sum([x['q'] for x in keyed_bids])
        # working_price = -2
        # csq = {}
        # cbq = {}
        # for o in self.all_orders:
        #     _type = o['t']
        #     price = o['p']
        #     quant = o['q']
            
        #     if _type == 'o':
        #         working_csq = working_csq + quant
                
        #     if price > working_price:
        #         working_price = price
        #         cbq[price] =  working_cbq
        #         csq[price] = working_csq
                
        #     if _type == 'b':
        #         working_cbq = working_cbq - quant
        
        # return csq, cbq
        
        all_prices = sorted(set([o[0] for o in self.bids + self.offers]))
        
        # Calculate CSQ
        csq = {}
        for p in all_prices:
            relevant_offers = filter(lambda x: x[0] <= p, self.offers)
            csq_p = sum([o[1] for o in relevant_offers])
            csq[p] = csq_p
            
        cbq = {}
        for p in all_prices[::-1]:
            relevant_bids = filter(lambda x: x[0] >= p, self.bids)
            cbq_p = sum([o[1] for o in relevant_bids])
            cbq[p] = cbq_p
 
        return csq, cbq



    def get_market_price(self):
        """
        Implementation of the Call Market price algorithm described by: Sun et al. (2010)
        https://www.researchgate.net/publication/241567616_Algorithm_of_Call_Auction_Price
        
           Parameters: 

            
            Return:
                A tuple containing
                market_price (number): The resulting market price
                volume (number):  the Market Exchange Volume
        """


        # Begin no-trade
        #  Handle error cases where there are missing bids or offers       
        
        self.final_principle = Principle.NO_ORDERS
        if not (self.has_bids or self.has_offers):  # No orders of any kind
            return None, 0
        
        min_offer_price = None
        if self.has_offers:
            all_offer_price = [o[0] for o in self.offers]
            min_offer_price = min(all_offer_price)
            
        max_bid_price = None
        if self.has_bids:
            all_bid_price = [b[0] for b in self.bids]
            max_bid_price = max(all_bid_price)
       
        
        if not self.has_bids: # no buys
            # the price is the lowest offer (sell).  That is the lowest price 
            # at which a share may can be traded.
            return min_offer_price, 0
        
        if not self.has_offers: # no buys
            # the price is the highest bid (buy).  That is the highest price 
            # at which a share may can be traded.
            return max_bid_price, 0
        
        # If there is a bid-ask spread return the midpoint price
        if min_offer_price > max_bid_price:
            return (max(cand_resid) + min(cand_resid))/2


        
        # Determine volume and candidate prices based the Max Exchange Volume principle
        self.csq, self.cbq = self.generate_cxq()

        all_prices = sorted(set([o[0] for o in self.bids + self.offers]))
        cand_mev = [] # artifact of loop, the candidate prices
        mev = -1  # this is an artifact of the following loop and is the final volume
        for p in all_prices:
            csq_p = self.csq[p]
            cbq_p = self.cbq[p]
            vol = min(csq_p, cbq_p)
             
            if vol > mev:
                cand_mev = [p]
                mev = vol
            elif vol == mev:
                cand_mev.append(p)
                
        if len(cand_mev) == 1:
            return cand_mev[0], mev
        
            
        # calculate the residudal for all prices between the MEV candidates
        working_csq = 0
        working_cbq = 0
        full_csq = {}
        full_cbq = {}
        for p in range(min(cand_mev), max(cand_mev) + 1):
            if p in cand_mev:
                working_csq = self.csq[p]
            full_csq[p] = working_csq
            
        for p in range(max(cand_mev), min(cand_mev) -1, -1):
            if p in cand_mev:
                working_cbq = self.cbq[p]
            full_cbq[p] = working_cbq
        
        
        # determine candidate prices based on min resid
        cand_resid = []
        min_resid = 10000000
        for p in range(min(cand_mev), max(cand_mev) + 1):
            r = abs(full_csq[p] - full_cbq[p])
            if r < min_resid:
                min_resid = r
                cand_resid = [p]
            elif r == min_resid:
                cand_resid.append(p)
        
        
        price = (max(cand_resid) + min(cand_resid))/2
        
        return price, mev

# END MarketPrice

def count_filled_volume(orders):
    """
    Helper function to count the total volume of orders filled of a given list of Orders.
    Parameters:
        orders (list: Order):  The list of orders

    Returns:
        (number) the total filled volume of the list
    """
    return sum([o.quantity_final or 0 for o in orders])


def partial_fill(order_list, cap):
    """
    Given a list of Orders (ideally sorted by price), determine which orders to fill.
    Quantities of the orders will be adjusted so that the sum of the resulting list
    will be equal to the cap.   Orders are iterated through in the given order
    (this function will not sort the list). If the quantity of the current order
    does not cause the running total to exceed the cap then it is copied into the
    return list.   If the current order does cause the total quantity to exceed the
    cap, then the order is copied into the return list with a modified amount so
    that the total quantity of the return list equals the cap.

        Parameters:
            order_list (list-like: Order) The list of orders (should be pre-sorted)
                            prior to call.
            cap (number): The cap amount.  The total quantity of the returned order list
                                will match this amount

        Returns:
            A list of orders modified in such a way that the combined quantity equals the
            given cap.
    """
    ret_list = []
    # If there is a zero cap, then there is no need to do anything else
    if cap == 0 or order_list is None or not order_list:
        return ret_list

    # If we make it here, we still need to deal with partial orders
    # Accumulate volumes in the partial order list, until we have surpassed the mev
    accumulated_volume = 0
    idx = 0
    while accumulated_volume < cap:
        order = order_list[idx]
        order.quantity_final = order.quantity
        accumulated_volume += order.quantity
        idx += 1
        ret_list.append(order)

    # at this point, the last order added to the filled_order list should be
    #  "too much".   Adjust that order by the difference of accum - cap.
    last_order = ret_list[-1]
    last_order.quantity_final = last_order.quantity - (accumulated_volume - cap)

    return ret_list


def count_volume(orders):
    """
    Helper function to count the total volume of a given list of Orders.
    Parameters:

    Returns:
        (number, number) a tuple that contains the volumes of bids and offers
    """
    vol = sum([o.quantity for o in orders])

    return vol


class OrderFill2:
    SORT_KEY = attrgetter('price', 'quantity')

    def __init__(self, orders):
        """
        Split the given orders into bids and offers and sorts them by price and quantity
        """
        self.orders = orders

        self.bids = [o for o in orders if o.order_type == OrderType.BID.value]
        self.bids.sort(key=OrderFill2.SORT_KEY, reverse=True)

        self.offers = [o for o in orders if o.order_type == OrderType.OFFER.value]
        self.offers.sort(key=OrderFill2.SORT_KEY)

    def select_bids(self, thold_price):
        """
        Select orders with a price less than or equal to the threshold price.
        Parameters:
            thold_price (number):  The threshold price
        Returns:
            (list: Order): A list of orders with price less than or equal to the threshold price
        """

        return list(filter(lambda o: o.price >= thold_price, self.bids))

    def select_offers(self, thold_price):
        """
        Select offres with a price less than or equal to the threshold price.
        Parameters:
            thold_price (number):  The threshold price
            
        Returns:
            (list: Order): A list of offers with price less than or equal to the threshold price
        """
        return list(filter(lambda o: o.price <= thold_price, self.offers))

    def fill_orders(self, market_price):
        """
        Determine which orders to fill. Sets the 'quantity_final' on all transacted orders.
        Note most 'quantity_final's will be the same as the order quantity.
        A few orders might have different values for quantity_final and quantity to
        ensure the market volume is met.
        """

        # Sort and filter bids and offers
        bids_to_exchange = self.select_bids(market_price)
        offers_to_exchange = self.select_offers(market_price)

        total_volume_bid = count_volume(bids_to_exchange)
        total_volume_offer = count_volume(offers_to_exchange)
        mev = min(total_volume_bid, total_volume_offer)

        if total_volume_bid < total_volume_offer:
            # All bids will be traded - offers should be modified
            filled_bids = bids_to_exchange
            for o in filled_bids:
                o.quantity_final = o.quantity
            filled_offers = partial_fill(offers_to_exchange, mev)

        elif total_volume_bid > total_volume_offer:
            # All offers will be traded - bids are modified.
            filled_bids = partial_fill(bids_to_exchange, mev)
            filled_offers = offers_to_exchange
            for o in filled_offers:
                o.quantity_final = o.quantity

        else:
            # All orders are traded and we're done
            filled_bids = bids_to_exchange
            for o in filled_bids:
                o.quantity_final = o.quantity
            filled_offers = offers_to_exchange
            for o in filled_offers:
                o.quantity_final = o.quantity

        return filled_bids, filled_offers
