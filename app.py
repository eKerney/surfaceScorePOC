import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import pydeck as pdk
from scoring import surfaceScore

st.set_page_config(layout="wide")
st.markdown(""" <style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> """, unsafe_allow_html=True)


def runScore(df, fields, centerPoint):
    st.write(st.session_state.surfaceName)
    scoringDict = {'LOW':[], 'MED':[], 'HIGH':[]}
    for f in fields:
        cat = st.session_state[f]
        scoringDict[cat].append(f)
        # st.write((f'{f} - '), st.session_state[f])
    st.write(scoringDict)
    
    surfScor = surfaceScore(df, {'LOW': 5, 'MED': 50, 'HIGH': 200}, renameIndex=True)
    surfScor.runSurfaceScoring(scoringDict)

    st.pydeck_chart(pdk.Deck(
        map_style=None,
        height=1000,
        initial_view_state=pdk.ViewState(
            latitude=centerPoint[1],
            longitude=centerPoint[0],
            zoom=12,
            pitch=40,
        ),
        tooltip = {
            "html": "<b>SCORE:</b> {SCORE}",
            "style": {"backgroundColor": "steelblue","color": "white"}
        },
        layers=[
            pdk.Layer(
                "H3HexagonLayer",
                surfScor.expSurf,
                pickable=True,
                stroked=False,
                filled=True,
                extruded=True,
                get_elevation='SCORE',
                get_hexagon="h3_index",
                get_fill_color=[
                    ('SCORE == 5 ? 255 : SCORE == 50 ? 255 : SCORE == 200 ? 255 : 56 '),
                    ('SCORE == 5 ? 255 : SCORE == 50 ? 170 : SCORE == 200 ? 0   : 168'),
                    ('SCORE == 5 ? 0   : SCORE == 50 ? 0   : SCORE == 200 ? 0   : 0  '),
                    80
                ]
            )
        ],
    ))

def scoreFields(df, centerPoint):
    st.write(st.session_state.surfaceName)
    st.write(df)
    fields = st.session_state.fields
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form(key='score_field_select'):
            submitScore = st.form_submit_button(label='SUBMIT', on_click=runScore, args=(df, fields, centerPoint,))
            for f in fields:
                score = st.selectbox((f'{f}'), ('LOW','MED','HIGH'), key=(f'{f}'))
                

def selectFields(df, centerPoint):
    cols = df.columns
    col1, col2 = st.columns([1,1])
    data = 'info'
    with col1:
        with st.form(key='simple_field_select'):
            fields = st.multiselect('SELECT FIELDS', (cols), key='fields')
            submitted = st.form_submit_button(label='SUBMIT', on_click=scoreFields, args=(df, centerPoint,))

def loadSurface():
    st.session_state.active = True
    gpkg = {'AUGUSTA TOWNSHIP': 'AUGUSTA TOWNSHIPSURFMETA2.gpkg', 
            'SYCAMORE MEADOWS': 'SYCAMORE MEADOWSSURFMETA2.gpkg', 
            'WEST WILLOW': 'WEST WILLOWSURFMETA2.gpkg', 
            'WHITMORE LAKE': 'WHITMORE LAKESURFMETA2.gpkg', 
            'YPSILANTI': 'YPSILANTISURFMETA2.gpkg'}
    st.title("SURFACE SCORING PROTOTYPE")
    surface = gpd.read_file(f'data/{gpkg[st.session_state.surfaceName]}')
    df = surface.drop(['geometry'], axis=1)
    st.write(f'LOADED SURFACE {gpkg[st.session_state.surfaceName]}')
    coords = surface.total_bounds
    centerPoint = [((coords[0]+coords[2])/2), ((coords[1]+coords[3])/2)]
    st.write(df)
    cols = df.columns
    
    selectFields(df, centerPoint)
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

