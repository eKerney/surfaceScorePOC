import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import pydeck as pdk
from scoring import surfaceScore

st.set_page_config(layout="wide")
st.markdown(""" <style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> """, unsafe_allow_html=True)


def runScore(df, fields):
    st.write(st.session_state.surfaceName)
    st.write(df)
    surfScor = surfaceScore(df, {'LOW': 5, 'MED': 50, 'HIGH': 200}, renameIndex=True)

    for f in fields:
        st.write((f'{f} - '), st.session_state[f])
    
    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=42.3,
            longitude=-83.6,
            zoom=10,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "H3HexagonLayer",
                df,
                pickable=True,
                stroked=True,
                filled=True,
                extruded=False,
                get_hexagon="index",
                get_fill_color=[100,100,100],
                get_line_color=[255, 255, 255],
                line_width_min_pixels=0.5,
            )
        ],
    ))

def scoreFields(df):
    st.write(st.session_state.surfaceName)
    st.write(df)
    fields = st.session_state.fields
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form(key='score_field_select'):
            submitScore = st.form_submit_button(label='SUBMIT', on_click=runScore, args=(df, fields))
            # st.write(fields)
            for f in fields:
                score = st.selectbox((f'{f}'), ('LOW','MED','HIGH'), key=(f'{f}'))
                

def selectFields(df):
    cols = df.columns
    col1, col2 = st.columns([1,1])
    data = 'info'
    with col1:
        with st.form(key='simple_field_select'):
            # st.write("SELECT FIELDS")
            fields = st.multiselect('SELECT FIELDS', (cols), key='fields')
            submitted = st.form_submit_button(label='SUBMIT', on_click=scoreFields, args=(df,))
        st.write("Outside the form")

def loadSurface():
    st.session_state.active = True
    gpkg = {'AUGUSTA TOWNSHIP': 'AUGUSTA TOWNSHIPSURFMETA2.gpkg', 
            'SYCAMORE MEADOWS': 'SYCAMORE MEADOWSSURFMETA2.gpkg', 
            'WEST WILLOW': 'WEST WILLOWSURFMETA2.gpkg', 
            'WHITMORE LAKE': 'WHITMORE LAKESURFMETA2.gpkg', 
            'YPSILANTI': 'YPSILANTISURFMETA2.gpkg'}
    # select = st.sidebar.selectbox(
    #     'SELECT SURFACE',
    #     ('AUGUSTA TOWNSHIP', 'SYCAMORE MEADOWS', 'WEST WILLOW', 'WHITMORE LAKE', 'YPSILANTI'),
    #     on_change=loadSurface, key='surfaceName')
    #
    # upload = st.sidebar.selectbox(
    #     'UPLOAD GeoPackage SURFACE',
    #     ('placeholder.gpkg', 'GeoPackage2.gpkg'),
    #     on_change=loadSurface, key='surfacePath')
    st.title("SURFACE SCORING PROTOTYPE")
    surface = gpd.read_file(f'data/{gpkg[st.session_state.surfaceName]}')
    df = surface.drop(['geometry'], axis=1)
    st.write(f'LOADED SURFACE {gpkg[st.session_state.surfaceName]}')
    st.write(df)
    st.write('loadSurface')
    cols = df.columns
    
    selectFields(df)
    # st.dataframe(surface)

if 'active' not in st.session_state:
    st.title("SURFACE SCORING PROTOTYPE")
    select = st.sidebar.selectbox(
        'SELECT SURFACE',
        ('AUGUSTA TOWNSHIP', 'SYCAMORE MEADOWS', 'WEST WILLOW', 'WHITMORE LAKE', 'YPSILANTI'),
        on_change=loadSurface, key='surfaceName')

    upload = st.sidebar.selectbox(
        'UPLOAD GeoPackage SURFACE',
        ('placeholder.gpkg', 'GeoPackage2.gpkg'),
        on_change=loadSurface, key='surfacePath')

if 'active' in st.session_state:
    # st.title("SURFACE SCORING PROTOTYPE")
    select = st.sidebar.selectbox(
        'SELECT SURFACE',
        ('AUGUSTA TOWNSHIP', 'SYCAMORE MEADOWS', 'WEST WILLOW', 'WHITMORE LAKE', 'YPSILANTI'),
        on_change=loadSurface, key='surfaceName')

    upload = st.sidebar.selectbox(
        'UPLOAD GeoPackage SURFACE',
        ('placeholder.gpkg', 'GeoPackage2.gpkg'),
        on_change=loadSurface, key='surfacePath')

