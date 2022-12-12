import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from urllib import request
import json

# Backend

base_url = "https://query2.finance.yahoo.com/v1/finance/esgChart?symbol="

@st.cache(allow_output_mutation=True)
def get_esgdata(ticker:str):
    """Get ESG scores from Yahoo Finance's endpoint, given a company's ticker symbol"""

    # open url and get json data
    url = base_url + ticker
    connection = request.urlopen(url)
    jsondata = connection.read()

    # decode json to Python objects
    data = json.loads(jsondata)
    
    # extract and format data (including the timestamp column)
    try:
        # get the company's peer group
        peergroup = data["esgChart"]["result"][0]["peerGroup"] 
    except:
        print("\tuh oh, no sustainability data!")
        st.write("Data doesn't exist for", ticker)    
        return None
    
    # get the company's ESG scores
    company_data = pd.DataFrame(data["esgChart"]["result"][0]["symbolSeries"])
    company_data["timestamp"] = pd.to_datetime(company_data["timestamp"], unit="s")
    company_data = company_data.reset_index(drop=True)

    # get the company's peer group's ESG scores
    peergroup_data = pd.DataFrame(data["esgChart"]["result"][0]["peerSeries"])
    peergroup_data["timestamp"] = pd.to_datetime(peergroup_data["timestamp"], unit="s")
    peergroup_data = peergroup_data.reset_index(drop=True)

    return peergroup, company_data, peergroup_data

def display_tables(ticker:str, peergroup:str, company_data, peergroup_data, all=True):
    """Display tables of ESG ratings data"""

    ticker_header = "ESG Ratings for " + ticker
    peergroup_header = "ESG Ratings for " + peergroup

    if all:
        st.header(ticker_header)
        st.write(company_data)

        st.header(peergroup_header)
        st.write(peergroup_data)
    else:
        company_after2020 = company_data[company_data.timestamp >= "2020-01-01"]
        st.header(ticker_header)
        st.write(company_after2020)

        peergroup_after2020 = peergroup_data[peergroup_data.timestamp >= "2020-01-01"]
        st.header(peergroup_header)
        st.write(peergroup_after2020)

### Front end! ###

# design sidebar
with st.sidebar:

    # description
    st.title("About QuickESG")
    st.write("Quickly look up a firm's Sustainalytics ESG Rating")

    # user input
    ticker = st.text_input("Ticker:", "AAPL")
    show_truncated_data = st.selectbox("Show only data from 1 Jan 2020 onwards?", ["Yes", "No, show me data of all time"]) == "Yes"

    # get ESG data
    peergroup, company_data, peergroup_data = get_esgdata(ticker)
    st.write(ticker, "is in", peergroup)


# create tabs
company_tab, industry_tab, data_tab = st.tabs(["Company View", "Industry View", "Download Data"])

with company_tab:
    st.write('yes')

with industry_tab:
    st.write('another yes')

with data_tab:
    if show_truncated_data:
        display_tables(ticker, peergroup, company_data, peergroup_data, all=False)
    else:
        display_tables(ticker, peergroup, company_data, peergroup_data)