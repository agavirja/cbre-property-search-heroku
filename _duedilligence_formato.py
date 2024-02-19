import streamlit as st
import webbrowser

from _duedilligence_formato_predio    import main as reporte_predio
from _duedilligence_formato_building  import main as reporte_building
from _duedilligence_formato_radio     import main as reporte_radio
from _duedilligence_formato_pot       import main as reporte_pot

def main(inputvar):
    
    formato = {
               'reporte_duedilligence':False,
               'inputvar_duedilligence':{}
               }
    for key,value in formato.items():
        if key not in st.session_state: 
            st.session_state[key] = value
                
    col1,col2,col3 = st.columns(3)
    with col3:
        if st.button('Nueva busqueda'):
            st.session_state.reporte_duedilligence = False
            st.session_state.inputvar_duedilligence = {}
            webbrowser.open("http://urbextestapp.streamlit.app/Due_dilligence_digital")
            st.rerun()
    
    if 'tiporeporte' in inputvar:
        if 'predio' in inputvar['tiporeporte'].lower():
            reporte_predio(inputvar)
        elif 'building' in inputvar['tiporeporte'].lower():
            reporte_building(inputvar)
        elif 'radio' in inputvar['tiporeporte'].lower():
            reporte_radio(inputvar)
        elif 'pot' in inputvar['tiporeporte'].lower():
            reporte_pot(inputvar)
