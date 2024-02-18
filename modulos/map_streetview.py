import streamlit as st
import shapely.wkt as wkt
import folium
import streamlit.components.v1 as components
from streamlit_folium import st_folium


from modulos.stylefunctions import style_function

def map_streetview(polygon=None,latitud=None,longitud=None):
    
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

    if latitud and longitud:
        col1, col2 = st.columns([5,3])
        
        m  = folium.Map(location=[latitud, longitud], zoom_start=18,tiles="cartodbpositron")
        
        if polygon:
            try: folium.GeoJson(polygon, style_function=style_function).add_to(m)
            except:
                try: folium.GeoJson(wkt.loads(polygon) , style_function=style_function).add_to(m)
                except: pass
        else:
            try: folium.Marker(location=[latitud, longitud]).add_to(m)
            except: pass
                
        with col1:
            st_map  = st_folium(m,width=1000,height=400)

        style = """
        <style>
            #map-container {
                width: 100%;
                height: 450px;
            }
        </style>
        """
        streetview = """
        <script>
            function initMap() {
                var latitud = latitud_replace;
                var longitud = longitud_replace;
                var latLng = new google.maps.LatLng(latitud, longitud);
                var panoramaOptions = {
                    position: latLng,
                    pov: {
                        heading: 0, // Dirección inicial
                        pitch: 0 // Ángulo de inclinación inicial
                    },

                };
                var panorama = new google.maps.StreetViewPanorama(
                    document.getElementById('map-container'),
                    panoramaOptions
                );
                var map = new google.maps.Map(document.getElementById('map-container'), {
                    streetView: panorama
                });
            }
        </script>
        <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBEjvAMTg70W6oUvWc5HzYUS3O9rzEI9Jw&callback=initMap" async defer></script>                          
        """
        streetview = streetview.replace('latitud_replace',str(latitud)).replace('longitud_replace',str(longitud))
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-icons.css" rel="stylesheet">
          <link href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/nucleo-svg.css" rel="stylesheet">
          <link id="pagestyle" href="https://personal-data-bucket-online.s3.us-east-2.amazonaws.com/css/soft-ui-dashboard.css?v=1.0.7" rel="stylesheet">
          {style}
        </head>
        <body>
          <div class="container-fluid py-4" style="margin-bottom: -50px;margin-top: -50px;">
            <div class="row">
            
              <div class="col-xl-12 col-sm-6 mb-xl-0 mb-2">
                <div class="card h-100">
                  <div class="card-body p-3">             
                    <div class="container-fluid py-4">
                      <div class="row">
                        <div id="map-container"></div>
                        {streetview}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
            </div>
          </div>
        </body>
        </html>
        """
        with col2:
            st.components.v1.html(html, width=1000, height=420)
