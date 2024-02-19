import streamlit as st
import streamlit.components.v1 as components

from _ficha_formato import main as reporte


def main(inputvar):
    
    formato = {
               'code':None,
               'tiponegocio':None,
               'tipoinmueble':None,
               'ficha_inputvar':inputvar
               }

    for key,value in formato.items():
        if key not in st.session_state: 
            st.session_state[key] = value
            
    code         = inputvar['code'] if 'code' in inputvar else None
    tipoinmueble = inputvar['tipoinmueble'] if 'tipoinmueble' in inputvar else None
    tiponegocio  = inputvar['tiponegocio'] if 'tiponegocio' in inputvar else None
    
    if code is not None and tipoinmueble is not None and tiponegocio is not None:
        reporte(code,tipoinmueble,tiponegocio)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.code         = st.text_input('Código',value=code)
            st.session_state.tipoinmueble = st.selectbox('Tipo de inmueble',options=['Apartamento','Bodega','Casa','Local','Oficina'])
            st.session_state.tiponegocio  = st.selectbox('Tipo de Negocio',options=['Venta','Arriendo'])
            if st.button('Buscar'):
                st.session_state.ficha_inputvar = {'code':st.session_state.code,'tiponegocio':st.session_state.tiponegocio,'tipoinmueble':st.session_state.tipoinmueble}
                st.rerun()
        with col2:
            st.image('https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/imagenes_app/buildings.png')

    components.html(
        """
    <script>
    const elements = window.parent.document.querySelectorAll('.stButton button')
    elements[0].style.backgroundColor = '#68c8ed';
    elements[0].style.fontWeight = 'bold';
    elements[0].style.color = 'white';
    elements[0].style.width = '100%';
    </script>
    """
    )