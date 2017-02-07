#!/usr/bin/env python2

from mpt import *
import plotly.plotly as py
import plotly.graph_objs as go
import matplotlib.pyplot as plt


def plot_rr(rets, frontier=False):

    ret = rets.mean()*252
    vol = rets.std()*np.sqrt(252)
    for s in ret.index:
        plt.scatter(x=vol[s], y=ret[s], label=s, marker='^')
        plt.annotate(s, (vol[s], ret[s]))

    if not frontier:
        plt.savefig('scatter.png')
        return

    weights, points = compute_frontier(rets)
    ret, vol, sha = zip(*points)

    plt.scatter(vol, ret, c=sha)
    plt.colorbar()
    plt.savefig('scatter.png')


def plotly_rr(rets, frontier=False):
    ret = rets.mean()*252
    vol = rets.std()*np.sqrt(252)

    data = []
    for s in ret.index:
        data.append(
            go.Scatter(x=vol[s], y=ret[s], text=s,
                       mode='markers+text', textposition='top'))

    if frontier:
        weights, points = compute_frontier(rets)
        ret, vol, sha = zip(*points)
        symbols = rets.columns

        disptxt = ["Ret/Vol: %0.3f\n\n" % s for s in sha]
        for i, x in enumerate(weights):
            for j, s in enumerate(symbols):
                disptxt[i] += '%s: %0.3f\n' % (s, x[j])
        #disptxt = ["".join(['%s: %0.3f\n' % (s, x[i]) for i, s in enumerate(symbols)]) for x in weights]

        tr = go.Scatter(
            x = vol,
            y = ret,
            mode='markers',
            marker = dict(
                color = sha,
                showscale = True,
            ),
            text=disptxt
        )
        data.append(tr)

    layout = go.Layout(
        showlegend = False,
        xaxis = dict(title="Risk"),
        yaxis = dict(title="Return"),
    )
    fig = go.Figure(data=data, layout=layout)
    url = py.plot(fig, filename='testmpt') 

    return url


if __name__ == "__main__":
    stocks = ['MSFT', 'AAPL', 'JNJ', 'JPM', 'GOOG']
    df  = get_pct(stocks, '01/01/2014', '31/12/2016')
    plotly_rr(df, True)
