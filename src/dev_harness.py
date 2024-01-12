from src.call_market_price2 import MarketPrice

# bids = [(25,1), (15, 2), (5,2)]
# offers = [(10,1), (20,1), (30, 2), (40, 2)]
# bids = [(15,1)]
# offers = [(10,2)]
# bids = [(1, 1), (2, 2)]
# offers = [(1, 1), (2, 2)]
bids = [(4, 2), (6, 1)]
offers = [(4, 1), (6, 1)]



import pandas as pd

orders = pd.read_csv('/Users/rossspoon/projects/spyder/short_squeeze_analysis/data_preproc/flat_order.csv').set_index('uid')
g = orders.groupby(['session', 'round'])
keys = list(g.groups.keys())


def run_market(bids, offers):
    cm = MarketPrice(bids, offers)
    p,v = cm.get_market_price()
    return p, v, cm


## plot it
def plot_it(_p, _v, _csq, _cbq):
    import matplotlib_inline
    import matplotlib.pyplot as plt
    plt.step(_cbq.values(), _cbq.keys(), where='pre')
    plt.step(_csq.values(), _csq.keys())
    plt.plot(_v, _p, color='g', marker='o')
    

# import random
# i = random.randint(0, len(keys))
# s, r = keys[i]
# s = 'qo2mugvy'
# r = 6


def do_it(g):
    sess = g
    bids = sess[sess.type=='BUY'][['price', 'quantity']].astype(int)
    bids = [(r.price, r.quantity) for _, r in bids.iterrows()]
    offers = sess[sess.type=='SELL'][['price', 'quantity']].astype(int)
    offers = [(r.price, r.quantity) for _, r in offers.iterrows()]

    p, v, cm = run_market(bids, offers)
    return pd.Series((p,v))

# pv = orders.groupby(['session', 'round']).apply(do_it)
# pv.reset_index().groupby('session')[[0]].plot()


p, v, cm = run_market(bids, offers)
plot_it(p, v, cm.csq, cm.cbq)


