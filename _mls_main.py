import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw

from shapely.geometry import Polygon,mapping,shape

from _mls_formato import main as reporte

from modulos.stylefunctions import style_function

def main():
    
    formato = {
               'polygon_mls':None,
               'geojson_data':None,
               'zoom_start':12,
               'latitud':4.652652, 
               'longitud':-74.077899,
               'reporte_mls':False,
               'inputvar_mls':{}
               }
    
    for key,value in formato.items():
        if key not in st.session_state: 
            st.session_state[key] = value

    if not st.session_state.reporte_mls:
        col1,col2,col3 = st.columns([1,1,3])
        with col1:
            tipoinmueble = st.selectbox('Tipo de inmueble', options=['Apartamento', 'Bodega', 'Casa', 'Consultorio', 'Edificio', 'Hotel', 'Local', 'Oficina'])
        with col2:
            tiponegocio = st.selectbox('Tipo de negocio',options=['Venta', 'Arriendo'])
        with col1:
            areamin = st.number_input('Área mínima',value=0,min_value=0)
        with col2:
            areamax = st.number_input('Área máxima',value=0,min_value=0)
        with col1:
            valormin = st.number_input('Valor mínimo',value=0,min_value=0)
        with col2:
            valormax = st.number_input('Valor máximo',value=0,min_value=0)
            
        habitacionesmin,habitacionesmax,banosmin,banosmax,garajesmin,garajesmax = [0]*6
        
        if any([x for x in ['Apartamento','Casa'] if x in tipoinmueble]):
            with col1:
                habitacionesmin = st.selectbox('Habitaciones mínimas',options=[1,2,3,4,5,6],index=0)
            with col2:
                habitacionesmax = st.selectbox('Habitaciones máximas',options=[1,2,3,4,5,6],index=5)
            with col1:
                banosmin = st.selectbox('Baños mínimos',options=[1,2,3,4,5,6],index=0)
            with col2:
                banosmax = st.selectbox('Baños máximos',options=[1,2,3,4,5,6],index=5)       
            with col1:
                garajesmin = st.selectbox('Garajes mínimos',options=[0,1,2,3,4],index=0)
            with col2:
                garajesmax = st.selectbox('Garajes máximos',options=[0,1,2,3,4,5,6],index=6)

        with col3:
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
                coordenadas                   = st_map['all_drawings'][0]['geometry']['coordinates']
                st.session_state.polygon_mls  = Polygon(coordenadas[0])
                st.session_state.geojson_data = mapping(st.session_state.polygon_mls)
                polygon_shape                 = shape(st.session_state.geojson_data)
                centroid                      = polygon_shape.centroid
                st.session_state.latitud      = centroid.y
                st.session_state.longitud     = centroid.x
                st.session_state.zoom_start   = 16
                st.rerun()

        st.session_state.inputvar_mls = {
            'tipoinmueble':tipoinmueble,
            'tiponegocio':tiponegocio,
            'areamin':areamin,
            'areamax':areamax,
            'valormin':valormin,
            'valormax':valormax,
            'habitacionesmin':habitacionesmin,
            'habitacionesmax':habitacionesmax,
            'banosmin':banosmin,
            'banosmax':banosmax,
            'garajesmin':garajesmin,
            'garajesmax':garajesmax,
            'polygon':str(st.session_state.polygon_mls),
            }

        with col1:
            st.write('')
            st.write('')
            if st.button('Buscar'):
                st.session_state.reporte_mls = True
                st.rerun()
                
    if st.session_state.reporte_mls:
        with st.spinner('Buscando información'):
            reporte(st.session_state.inputvar_mls)
                
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
