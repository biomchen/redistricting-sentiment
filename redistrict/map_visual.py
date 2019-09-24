"""
A class using the folium module to visualize the sentiments after new proposal
has been presented to residents in LOU area.
"""
from geopy.geocoders import Nominatim
from pandas.io.json import json_normalize
import folium
import json
import vincent


class MapVisualization:

    def __init__(self, coordinates, score, option, location, polygon):
        self.coordinates = coordinates
        self.score = score
        self.option = option
        self.location = location
        self.polygon = polygon

    def get_json(self, data, school_name):
        pie_chart = vincent.Pie(data,
                                height=100,
                                width=100,
                                inner_radius=25)
        pie_chart.colors(brew='Set2')
        pie_chart.legend(school_name[:-10])  # -10 ES, -6 MS, -4 HS
        pie_json = pie_chart.to_json()

        return pie_json

    def folium_visual(self, col):
        nominatim = Nominatim(user_agent='my-application')
        locationCenter = nominatim.geocode(self.location)
        map = folium.Map(location=[locationCenter.latitude,
                                   locationCenter.longitude],
                         zoom_start=11)

        for school in self.coordinates.keys():
            lat = self.coordinates[school][0]
            lon = self.coordinates[school][1]

            if lat == 'NA' or lon == 'NA':
                continue
            else:
                school_json = self.score[school][self.option]
                chart_json = self.get_json(school_json, school)
                vega = folium.Vega(chart_json, width=200, height=100)
                pop_up = folium.Popup(max_width=400).add_child(vega)
                icon = folium.Icon(color=col, icon='info-sign')
                folium.Marker(location=[lat, lon],
                              popup=pop_up,
                              icon=icon
                              ).add_to(map)

        geojson = self.polygon
        folium.GeoJson(geojson, name='geojson').add_to(map)

        return map
