import streamlit as st
import pandas as pd
import numpy as np
import shapely.wkt as wkt
import plotly.express as px
import folium
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from bs4 import BeautifulSoup

from scripts.getinfopredialpolygon import getinfopredialpolygon
from scripts.getdatamarketcoddir import getdatamarketcoddir
from scripts.getrango import getrango
from scripts.inmuebleANDusosuelo import usosuelo2inmueble,inmueble2usosuelo

from modulos.map_streetview import map_streetview
from modulos.display_snr_proceso import display_snr_proceso
from modulos.display_transacciones_polygon import display_transacciones_polygon
from modulos.display_dane import display_dane
from modulos.display_listjson import display_listjson


from scripts.getconsolidacionlotes import getlotebycod

from modulos.display_lotespot import display_lotespot

def main(data):

    #-------------------------------------------------------------------------#
    # Mapa y streetview
    #-------------------------------------------------------------------------#
    polygon = None
    latitud, longitud, direccion = None, None, None
    if not data.empty:
        polygon = wkt.loads(data['geometry'].iloc[0]) 
        map_streetview(polygon)
        
    if not latitud and not longitud and polygon:
        try:
            polygonl = wkt.loads(polygon) 
            latitud  = polygonl.centroid.y
            longitud = polygonl.centroid.x
        except: 
            try:
                latitud  = polygon.centroid.y
                longitud = polygon.centroid.x
            except: pass
        
    if latitud and longitud and not polygon:
        map_streetview(polygon=None,latitud=latitud,longitud=longitud)