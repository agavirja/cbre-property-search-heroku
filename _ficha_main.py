import streamlit as st
from _ficha_formato import main as reporte

def main(inputvar):
    
    code         = inputvar['code'] if 'code' in inputvar else None
    tipoinmueble = inputvar['tipoinmueble'] if 'tipoinmueble' in inputvar else None
    tiponegocio  = inputvar['tiponegocio'] if 'tiponegocio' in inputvar else None
    
    if code is not None and tipoinmueble is not None and tiponegocio is not None:
        reporte(code,tipoinmueble,tiponegocio)
        
    else:
        st.write('Formulario')
