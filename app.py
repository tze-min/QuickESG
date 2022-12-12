import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from urllib import request
import json

### Backend! ###

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

def transform_data_for_company_tab(company_data, peergroup_data):
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

def create_esg_score_chart(data, all=True):
    """Plot timeline of ESG scores for the selected company, compared with peer group's average"""

    data = data[data.score_dimension == "esgScore"]
    if not all:
        data = data[data.timestamp >= "2020-01-01"]

    c = alt.Chart(data).mark_line(
        point=alt.OverlayMarkDef(color="red")
    ).encode(
        x="timestamp",
        y="score",
        color=alt.Color("series_type", legend=None),
        strokeDash="series_type"
    )

    return c

def create_env_score_chart(data, all=True):
    """Plot timeline of environmental scores for the selected company, compared with peer group's average"""

    data = data[data.score_dimension == "environmentScore"]
    if not all:
        data = data[data.timestamp >= "2020-01-01"]

    c = alt.Chart(data).mark_line(
        point=alt.OverlayMarkDef(color="red")
    ).encode(
        x="timestamp",
        y="score",
        color=alt.Color("series_type", legend=None),
        strokeDash="series_type"
    )

    return c

def create_social_score_chart(data, all=True):
    """Plot timeline of social scores for the selected company, compared with peer group's average"""

    data = data[data.score_dimension == "socialScore"]
    if not all:
        data = data[data.timestamp >= "2020-01-01"]

    c = alt.Chart(data).mark_line(
        point=alt.OverlayMarkDef(color="red")
    ).encode(
        x="timestamp",
        y="score",
        color=alt.Color("series_type", legend=None),
        strokeDash="series_type"
    )

    return c

def create_gov_score_chart(data, all=True):
    """Plot timeline of governance scores for the selected company, compared with peer group's average"""

    data = data[data.score_dimension == "governanceScore"]
    if not all:
        data = data[data.timestamp >= "2020-01-01"]

    c = alt.Chart(data).mark_line(
        point=alt.OverlayMarkDef(color="red")
    ).encode(
        x="timestamp",
        y="score",
        color=alt.Color("series_type", legend=None),
        strokeDash="series_type"
    )

    return c

def display_tables_for_data_tab(ticker:str, peergroup:str, company_data, peergroup_data, all=True):
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
    # create columns
    charts_col, news_col = st.columns(2)

    # transform and visualise ESG scores for selected company
    data = transform_data_for_company_tab(company_data, peergroup_data)

    # create Altair charts
    esg_chart = create_esg_score_chart(data, all=False)
    env_chart = create_env_score_chart(data, all=False)
    social_chart = create_social_score_chart(data, all=False)
    gov_chart = create_gov_score_chart(data, all=False)

    # pass the created charts to Streamlit
    charts_col.altair_chart(esg_chart, use_container_width=True)
    charts_col.altair_chart(env_chart, use_container_width=True)
    charts_col.altair_chart(social_chart, use_container_width=True)
    charts_col.altair_chart(gov_chart, use_container_width=True)
    
with industry_tab:
    st.write('another yes')

with data_tab:
    if show_truncated_data:
        display_tables_for_data_tab(ticker, peergroup, company_data, peergroup_data, all=False)
    else:
        display_tables_for_data_tab(ticker, peergroup, company_data, peergroup_data)