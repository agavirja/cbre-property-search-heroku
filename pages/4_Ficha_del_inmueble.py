import streamlit as st

from _ficha_main import main

st.set_page_config(layout="wide",initial_sidebar_state="auto")

formato = {
           'code':None,
           'tiponegocio':None,
           'tipoinmueble':None
           }

for key,value in formato.items():
    if key not in st.session_state: 
        st.session_state[key] = value
 
# obtener los argumentos de la url
args = st.experimental_get_query_params()
if 'code' in args: 
    st.session_state.code = args['code'][0]
if 'tiponegocio' in args:
    st.session_state.tiponegocio = args['tiponegocio'][0]
if 'tipoinmueble' in args:
    st.session_state.tipoinmueble = args['tipoinmueble'][0]

if st.session_state.code is not None and st.session_state.tiponegocio is not None and st.session_state.tipoinmueble is not None:
    inputvar = {'code':st.session_state.code,'tiponegocio':st.session_state.tiponegocio,'tipoinmueble':st.session_state.tipoinmueble}
else: inputvar = {}

main(inputvar)
