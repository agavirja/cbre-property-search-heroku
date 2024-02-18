import streamlit as st
import streamlit.components.v1 as components

from _duedilligence_formato   import main as reporte


def main(inputvar):
    
    if inputvar is not None and inputvar!={}:
        reporte(inputvar)
    else:
        formato = {
                   'reporte_duedilligence':False,
                   'inputvar_duedilligence':{}
                   }
        for key,value in formato.items():
            if key not in st.session_state: 
                st.session_state[key] = value
    
        chip,matricula,direccion,barmanpre,nombrepropiedad = '','','','',''

        if not st.session_state.reporte_duedilligence:
            col1,col2 = st.columns(2)
            with col1:
                seleccion = st.selectbox('Busqueda por:', options=['Chip','Matrícula','Dirección','Nombre de edificio'])
            
            if 'Chip' in seleccion:
                with col1:
                    chip = st.text_input('Chip',value='')
                    if not chip=='':
                        chip = chip.strip()
                        chip = chip.upper()
            
            if 'Matrícula' in seleccion:
                #with col2:
                #    oficina = st.selectbox('Oficina',options=['','50N','50C','50S'])
                with col1:
                    matricula = st.text_input('Matrícula',value='')
                    if not matricula=='':
                        matricula = matricula.strip()
                        
            if 'Dirección' in seleccion:   
                with col1:
                    direccion = st.text_input('Dirección',value='')
                    if not direccion=='':
                        direccion = direccion.strip()
        
            if 'Nombre de edificio' in seleccion:   
                with col1:
                    nombrepropiedad = st.selectbox('Nombre del edificio',options=['A','B','C'])
                    if not nombrepropiedad=='':
                        nombrepropiedad = nombrepropiedad.strip()
                         
            with col2:
                st.image('https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/imagenes_app/duedilligenceproperty.png')
    
            tiporeporte = None
            if chip!='' or matricula!='':
                tiporeporte = 'predio'
            elif direccion!='' or barmanpre!='' or nombrepropiedad!='':
                tiporeporte = 'building'
            st.session_state.inputvar_duedilligence = {'chip':chip,'matricula':matricula,'direccion':direccion,'barmanpre':barmanpre,'nombrepropiedad':nombrepropiedad,'tiporeporte':tiporeporte}
            
            with col1:
                st.write('')
                st.write('')
                if st.button('Buscar'):
                    st.session_state.reporte_duedilligence = True
                    st.rerun()
    
        if st.session_state.reporte_duedilligence:
            with st.spinner('Buscando información'):
                reporte(st.session_state.inputvar_duedilligence)
    
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
