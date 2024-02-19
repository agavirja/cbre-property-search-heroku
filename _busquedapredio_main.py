import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw

from shapely.geometry import Polygon,mapping,shape

from _busquedapredio_formato import main as reporte

from modulos.stylefunctions import style_function

def main():
    
    formato = {
               'polygon_busquedapredio':None,
               'geojson_data':None,
               'zoom_start':12,
               'latitud':4.652652, 
               'longitud':-74.077899,
               'reporte_busquedapredio':False,
               'inputvar_busquedapredio':{}
               }
    
    for key,value in formato.items():
        if key not in st.session_state: 
            st.session_state[key] = value

    habitacionesmin = 0
    habitacionesmax = 0
    
    if not st.session_state.reporte_busquedapredio:
        col1,col2,col3 = st.columns([1,1,2])
        with col1:
            seleccion = st.selectbox('Tipo de inmueble', options=['Todos','Apartamento', 'Bodega', 'Casa', 'Consultorio', 'Edificio', 'Hotel', 'Local', 'Oficina', 'Parqueadero'])
        
        with col2:
            st.text_input('',disabled=True)

        with col1:
            areamin = st.number_input('Área mínima',value=0,min_value=0)
            
        with col2:
            areamax = st.number_input('Área máxima',value=0,min_value=0)
            
        if any([x for x in ['Apartamento','Casa'] if x in seleccion]):
            with col1:
                habitacionesmin = st.selectbox('Habitaciones mínimas',options=[1,2,3,4,5,6],index=0)
            with col2:
                habitacionesmax = st.selectbox('Habitaciones máximas',options=[1,2,3,4,5,6],index=5)
                 
        with col1:
            tipoubicacion = st.radio("Ubicación",["***Toda la ciudad***", "***Poligono***"],horizontal=True)
            if 'Toda la ciudad' in tipoubicacion:
                st.markdown("***<sup>se mostrará un máiximo de 1,000 predios</sup>***", unsafe_allow_html=True)

        with col3:
            if 'Poligono' in tipoubicacion:
                m    = folium.Map(location=[st.session_state.latitud, st.session_state.longitud], zoom_start=st.session_state.zoom_start,tiles="cartodbpositron")
                draw = Draw(
                            draw_options={"polyline": False,"marker": False,"circlemarker":False,"rectangle":False,"circle":False},
                            edit_options={"poly": {"allowIntersection": False}}
                            )
                draw.add_to(m)
                
                if st.session_state.geojson_data is not None:
                    folium.GeoJson(st.session_state.geojson_data, style_function=style_function).add_to(m)

                st_map = st_folium(m,width=800,height=600)
                
                polygonType = ''
                if 'all_drawings' in st_map and st_map['all_drawings'] is not None:
                    if st_map['all_drawings']!=[]:
                        if 'geometry' in st_map['all_drawings'][0] and 'type' in st_map['all_drawings'][0]['geometry']:
                            polygonType = st_map['all_drawings'][0]['geometry']['type']
                    
                if 'polygon' in polygonType.lower():
                    coordenadas                             = st_map['all_drawings'][0]['geometry']['coordinates']
                    st.session_state.polygon_busquedapredio = Polygon(coordenadas[0])
                    st.session_state.geojson_data           = mapping(st.session_state.polygon_busquedapredio)
                    polygon_shape                           = shape(st.session_state.geojson_data)
                    centroid                                = polygon_shape.centroid
                    st.session_state.latitud                = centroid.y
                    st.session_state.longitud               = centroid.x
                    st.session_state.zoom_start             = 16
                    st.rerun()
            else:
                st.image('https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/imagenes_app/buildings.png')

        if 'Toda la ciudad' in tipoubicacion:
            polygon = None
        elif 'Poligono' in tipoubicacion:
            polygon = str(st.session_state.polygon_busquedapredio)
            
        st.session_state.inputvar_busquedapredio = {
            'tipoinmueble':seleccion,
            'areamin':areamin,
            'areamax':areamax,
            'habitacionesmin':habitacionesmin,
            'habitacionesmax':habitacionesmax,
            'polygon':polygon,
            }

        with col2:
            st.write('')
            st.write('')
            if st.button('Buscar'):
                st.session_state.reporte_busquedapredio = True
                st.rerun()
                
    if st.session_state.reporte_busquedapredio:
        with st.spinner('Buscando información'):
            reporte(st.session_state.inputvar_busquedapredio)
                
    components.html(
        """
    <script>
    const elements = window.parent.document.querySelectorAll('.stButton button')
    elements[0].style.backgroundColor = '#68c8ed';
    elements[0].style.fontWeight = 'bold';
    elements[0].style.color = 'white';
    elements[0].style.width = '100%';
    elements[1].style.backgroundColor = '#68c8ed';
    elements[1].style.fontWeight = 'bold';
    elements[1].style.color = 'white';
    elements[1].style.width = '100%';
    </script>
    """
    )
