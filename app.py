import streamlit as st
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime as dt
from urllib import request
import json

# define scraper and formatting function

def get_esgdata(base_url, ticker):
    
    print("getting data for", ticker, "...")
    
    # open url and get json data
    url = base_url + ticker
    connection = request.urlopen(url)
    jsondata = connection.read()

    # decode json to Python objects
    data = json.loads(jsondata)
    
    # extract and format data (including the timestamp column)
    try:
        peer_group = data["esgChart"]["result"][0]["peerGroup"]
    except:
        print("\tno sustainability data!")
        no_data.append(ticker)
        return

    peer_series = pd.DataFrame(data["esgChart"]["result"][0]["peerSeries"])
    peer_series["ticker"] = ticker
    peer_series["peer_group"] = peer_group
    list_peer_series.append(peer_series)

    symbol_series = pd.DataFrame(data["esgChart"]["result"][0]["symbolSeries"])
    symbol_series["ticker"] = ticker
    symbol_series["peer_group"] = peer_group
    list_symbol_series.append(symbol_series)
    
    print("data for", ticker, "retrieved")

    return

# get data for each url in list of urls

list_peer_series = []
list_symbol_series = []
no_data = []

tickers = ["PEP", "AMT"] # sample tickers (NOVN should have no data)
base_url = "https://query2.finance.yahoo.com/v1/finance/esgChart?symbol="

for ticker in tickers:
    get_esgdata(base_url, ticker)
    
print("\ndata extraction complete!")
    
peer_data = pd.concat(list_peer_series)
symbol_data = pd.concat(list_symbol_series)

peer_data["timestamp"] = pd.to_datetime(peer_data["timestamp"], unit="s")
symbol_data["timestamp"] = pd.to_datetime(symbol_data["timestamp"], unit="s")

peer_data = peer_data.reset_index(drop=True)
symbol_data = symbol_data.reset_index(drop=True)

st.write("ESG Rating per Company")
st.write(symbol_data)

st.write("ESG Rating per Peer Group")
st.write(peer_data)

# For visualisation, drop the scores before 1 Jan 2020

symbol_after2020 = symbol_data[symbol_data.timestamp >= "2020-01-01"]
peer_after2020 = peer_data[peer_data.timestamp >= "2020-01-01"]

# Join datasets together

symbol_after2020["series_type"] = "company"
peer_after2020["series_type"] = "peer group"
after2020 = pd.concat([symbol_after2020, peer_after2020])

# Unpivot score columns

aft2020 = pd.melt(
    after2020, id_vars=["timestamp", "ticker", "series_type"], 
    value_vars=["esgScore", "governanceScore", "environmentScore", "socialScore"],
    var_name="score_dimension",
    value_name="score"
)

# Draw charts

mapping = peer_after2020[["ticker", "peer_group"]].value_counts().reset_index(name="count")

def plot_esgratings(ticker):
    ticker_aft2020 = aft2020[aft2020.ticker == ticker]

    ax = sns.relplot(
        data=ticker_aft2020, x="timestamp", y="score",
        hue="series_type", col="score_dimension",
        kind="line", style="series_type", markers=True
    )
    
    peer_group = mapping[mapping.ticker == ticker].reset_index().loc[0, "peer_group"]
    title = "ESG Risk Rating from 2020 to 2022, for " + ticker + " and its peer group, " + peer_group
    
    ax.set_xticklabels(rotation=40)
    ax.fig.suptitle(title) # add overall title
    plt.subplots_adjust(top=0.85) # adjust the subplots lower, so it doesn't overlap with the title
    plt.show()

plot_esgratings("PEP")