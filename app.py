import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from urllib import request
import json

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

def transform_data(company_data, peergroup_data):
    """Transform data into a format suitable for visualisation"""

    # join company and peer datasets
    company_data["series_type"] = "company"
    peergroup_data["series_type"] = "peer group"
    data = pd.concat([company_data, peergroup_data])

    # unpivot ESG score column
    data = pd.melt(
        data, id_vars=["timestamp", "series_type"],
        value_vars=["esgScore", "governanceScore", "environmentScore", "socialScore"],
        var_name="score_dimension",
        value_name="score"
    )

    # filter out NA values so that the non-NA values can be connected in line charts (for Altair)
    data = data.replace("<NA>", np.nan)
    data = data.dropna()

    return data

def display_charts(data, all=True):
    """Plot line charts of ESG scores, separated by company and industry average"""

    data = data[data.score_dimension == "esgScore"]
    if not all:
        data = data[data.timestamp >= "2020-01-01"]

    c = alt.Chart(data).mark_line(
        point=alt.OverlayMarkDef(color="red")
    ).encode(
        x="timestamp",
        y="score",
        color="series_type",
        strokeDash="series_type"
    )
    return c

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

# front end starts here
st.title("Quickly look up a firm's ESG rating")
ticker = st.text_input("Ticker:", "AAPL")
peergroup, company_data, peergroup_data = get_esgdata(ticker)

# do we want to visualise old ESG ratings before 1 Jan 2020?
if st.selectbox("Show only data from 1 Jan 2020 onwards?", ["Yes", "No, show me data of all time"]) == "Yes":
    display_tables(ticker, peergroup, company_data, peergroup_data, all=False)
else:
    display_tables(ticker, peergroup, company_data, peergroup_data)

# display joined dataset
st.header("Benchmark against peer group")
data = transform_data(company_data, peergroup_data)
st.write(data)
chart = display_charts(data, all=False)
st.altair_chart(chart, use_container_width=True)