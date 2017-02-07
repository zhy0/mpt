#!/usr/bin/env python2

import numpy as np
import pandas as pd
import pandas.io.data as web
from scipy.optimize import minimize


def get_pct(symbols, start, end, source='yahoo'):
    """
    Fetch daily assets' data from source and compute daily log returns.
    Outputs a Pandas DataFrame in which each column has the daily log
    returns of an asset over the period start to end.
    """
    data = [web.DataReader(s, source, start, end)['Adj Close'] for s in symbols]
    rets = pd.concat(data, axis=1).apply(lambda x: np.log(x/x.shift(1)))
    rets.columns = symbols
    return rets


def get_stats(weights, retvct, covmat):
    """
    Compute portfolio anualized returns, volatility and ret/vol.
    """
    ret = np.dot(retvct, weights)*252
    std = np.sqrt(np.dot(weights, np.dot(covmat*252, weights)))
    return [ret, std, ret/std]


def get_stats2(rets, weights):
    """
    Same as get_stats, but takes DataFrame with returns as input.
    """
    retvct = rets.mean().as_matrix()
    covmat = rets.cov().as_matrix()   

    return get_stats(weights, retvct, covmat)


def compute_frontier(rets, N=30):
    """
    Compute N points on the efficient frontier. 
    An added contraint is that each weight >= 0, i.e., no short selling.
    """
    assert N > 2

    retvct  = rets.mean().as_matrix()
    covmat  =  rets.cov().as_matrix()   

    max_ret = rets.mean().max()*252
    min_ret = get_stats(opt_vol(retvct, covmat), retvct, covmat)[0]

    tgt_rets = [min_ret + i*(max_ret-min_ret)/N for i in range(N)]
    weights  = [opt_ret(retvct, covmat, tgt) for tgt in tgt_rets]
    points   = [get_stats(x, retvct, covmat) for x in weights]

    return weights, points


def opt_ret(retvct, covmat, tgt):
    """
    Find the optimal weights for tgt expected return.
    """
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'ineq', 'fun': lambda x: x},
            {'type': 'eq', 'fun': lambda x: get_stats(x, retvct, covmat)[0] - tgt})

    func = lambda x: get_stats(x, retvct, covmat)[1]

    x0 = [1./len(retvct) for x in retvct]
    return minimize(func, x0, constraints=cons, method='SLSQP').x
    

def opt_vol(retvct, covmat):
    """
    Find the weights for the portfolio with least variance.
    """
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'ineq', 'fun': lambda x: x})

    func = lambda x: get_stats(x, retvct, covmat)[1]

    x0 = [1./len(retvct) for x in retvct]
    return minimize(func, x0, constraints=cons, method='SLSQP').x


def opt_sha(retvct, covmat):
    """
    Find the weights for the portfolio with maximized ret/vol (Sharpe Ratio).
    """
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'ineq', 'fun': lambda x: x})

    func = lambda x: -get_stats(x, retvct, covmat)[2]

    x0 = [1./len(retvct) for x in retvct]
    return minimize(func, x0, constraints=cons, method='SLSQP').x


def optimize(rets, opt_type, tgt=None):
    retvct  = rets.mean().as_matrix()
    covmat  =  rets.cov().as_matrix()   

    if opt_type == 'ret':
        return opt_ret(retvct, covmat, tgt)
    elif opt_type == 'vol':
        return opt_vol(retvct, covmat)
    elif opt_type == 'sha':
        return opt_sha(retvct, covmat)


if __name__ == "__main__":
    stocks = ['SPY', 'TLT', 'MSFT', 'AAPL', 'JNJ', 'JPM', 'GOOG']
    df  = get_pct(stocks, '01/01/2014', '31/12/2016')
    x = optimize(df, 'sha')
    plot_rr(df, True)
    #print df.corr()

    print x
    print get_stats2(df, x)

