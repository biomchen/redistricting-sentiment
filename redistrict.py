#!/usr/bin/env python

import re
import json
import pandas as pd
import numpy as np
import sqlite3
import vincent
import folium
import camelot
from json import dumps
import shapefile
from pyproj import Proj, transform
from geopy.geocoders import Nominatim
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from itertools import chain
from wordcloud import WordCloud
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import matplotlib.pyplot as plt


class SentiComments(object):
    ''' a class to calculate the sentiment score of each comments

        Parameters:
        file: pdf file has data in the tables
        pages: different pages corresponding to different tables
        columns: column names
        sch_names: school names
        option: 'A', 'B', 'AB'

        Methods:
        get_pdf_data: extracting the data from tables in the pdf file
        plot_words: making word cloud plots
        senti_results: produce the sentiment scores
    '''

    def __init__(self, file, pages, columns, sch_names, option):
        self.file = file
        self.pages = pages
        self.columns = columns
        self.sch_names = sch_names
        self.option = option
        self.get_pdf_data()

    def get_pdf_data(self):
        dat = camelot.read_pdf(self.file, pages=self.pages)
        dat = [(tb.df[1], tb.df[2]) for tb in dat]
        df = pd.DataFrame()
        for tb in dat:
            rows = len(tb)
            df_tb = pd.DataFrame(tb).T
            df = pd.concat([df, df_tb], axis=0)
        df.columns = self.columns
        df = df[df[self.columns[1]] != 'N/A']
        df = df[df[self.columns[1]] != 'n/a']
        schools = df[self.columns[0]]
        df = df.loc[schools.isin(self.sch_names)]
        df['Option'] = self.option
        return df

    def plot_words(self):
        tokenizer = RegexpTokenizer(r'\w+')
        stop_words = stopwords.words('english')
        data = self.get_pdf_data()
        words = [tokenizer.tokenize(row[1]) for _, row in data.iterrows()]
        words_clean =[word.lower() for word in list(chain(*words))
                      if word.lower() not in stop_words]
        comments_wc = WordCloud(
            background_color='white',
            max_words=2000,
            stopwords=stop_words
        )
        comments_wc.generate(str(words_clean))
        fig = plt.figure()
        fig.set_figwidth(14)
        fig.set_figheight(18)
        plt.imshow(comments_wc, interpolation='bilinear')
        plt.axis('off')
        plt.show()

    def senti_score(self):
        # Vader (Valence Aware Dictionary and sEntiment Reasoner)
        SentiAnalyzer = SentimentIntensityAnalyzer()
        schools = []
        scores = []
        results = {}
        data = self.get_pdf_data()
        for _, comment in data.iterrows():
            schools.append(comment[0])
            score = SentiAnalyzer.polarity_scores(str(comment[1]))
            scores.append(score['compound'])
        df_scores = pd.DataFrame([schools, scores]).T
        df_scores.columns = ['School', 'Score']
        for school in df_scores['School'].unique():
            sch_score = df_scores[df_scores['School'] == school]
            sch_score = sch_score['Score'].astype(float)
            score_mean = round(np.mean(sch_score), 3)
            num_scores = len(sch_score)
            # positive sentiment
            results_pos = len(sch_score[sch_score >= 0.05])
            results_pos = round(results_pos/num_scores, 3)
            # negative sentiment
            results_neg = len(sch_score[sch_score <= -0.05])
            results_neg = round(results_neg/num_scores, 3)
            # neutural sentiment
            results_neu = len(sch_score[sch_score <= 0.05][sch_score >= -0.05])
            results_neu = round(results_neu/num_scores, 3)
            results.update(
                {
                school:{
                    self.option:{
                        'Positive':results_pos,
                        'Negative':results_neg,
                        'Neutral':results_neu}}}
            )                             #'Mean': score_mean}}})
        return results

def df2sql(name, db, df):
    '''dumps the df into the SQL database'''
    conn = sqlite3.connect(db)
    df.to_sql(name, conn, if_exists='replace')

def merge_dfs(file, tb_pages, columns, sch_names, options):
    '''merge the comments of different options into one dataframe'''
    dfs = pd.DataFrame()
    for pages, option in zip(tb_pages, options):
        df = SentiComments(
            file,
            pages,
            columns,
            sch_names,
            option).get_pdf_data()
        dfs = pd.concat([dfs, df], axis=0)
    return dfs

def change_names(sch_names_old):
    new_names = []
    elementary_schs = []
    middle_schs = []
    high_schs = []
    for name in sch_names_old:
        sch_type = name.split(' ')[-1]
        if sch_type == 'ES':
            new_name = re.sub('ES', 'Elementary', name)
            elementary_schs.append(new_name)
        elif sch_type == 'MS':
            new_name = re.sub('MS', 'Middle', name)
            middle_schs.append(new_name)
        elif sch_type == 'HS':
            new_name = re.sub('HS', 'High', name)
            high_schs.append(new_name)
    return (elementary_schs, middle_schs, high_schs)

class Shape2Json(object):
    '''
    a class to convert shapefile to json file.

    Parameters:
    fname : input file name
    output1: output file of json without conversion of EPSG reference
    output2: output file of json with after EPSG conversion
    school_param: field values in shapefile; 'SCHOOL' or 'SCHOOL_1'
    school_list: a list of school names
    addresses: school addresses
    coordinates: coordinates of schools

    Methods:
    convert_json: converting shapefile to json and save the data
    convert_epsg: convert the coordiantes to world reference maps from Maryland
                  reference
    get_coordinates: get gps coordinates of the schools
    '''
    def __init__(self, fname, output1, output2, school_param, school_list,
                 addresses=None, coordinates=None):
        self.fname = fname
        self.output1 = output1
        self.output2 = output2
        self.school_param = school_param
        self.school_list = school_list
        self.addresses = addresses
        self.coordinates = coordinates

    def convert_json(self):  # school_param: 'SCHOOL_1' or 'SCHOOL'
        reader = shapefile.Reader(self.fname)
        fields = reader.fields[1:]
        field_names = [field[0] for field in fields]
        features = []
        name = self.fname.split('_')[0]
        name = name.split('/')[-1]
        print("Converting the shapefile of {} school district to json ...".
              format(name.lower()))
        for record in reader.shapeRecords():
            attributes = dict(zip(field_names, record.record))
            if attributes[self.school_param] in self.school_list:
                geo_records = record.shape.__geo_interface__
                features.append(
                    dict(type='Feature',
                        geometry=geo_records,
                        properties=attributes
                    )
                )
            else:
                continue
        json_file = open(self.output1, 'w')
        json_file.write(
            dumps(
                {'type': 'FeatureCollection','features': features},
                indent=2)
                + '\n'
            )
        json_file.close()

    def convert_epsg(self):
        in_proj = Proj(init='epsg:2248')  # pyproj.Proj API parameters
        out_proj = Proj(init='epsg:4326')
        print("Converting Maryland spatial reference from EPSG 2248 to 4326...")
        with open(self.output1) as json_file:
            data = json.load(json_file)
            features_old = data['features']
            coordinates = []
            features_new = []
            self.addresses = {}
            for feature in features_old:
                records = feature['geometry']['coordinates'][0]
                type = feature['geometry']['type']
                if type == 'Polygon':
                    for coordinate in records:
                        coordinate_new = transform(
                            in_proj,
                            out_proj,
                            coordinate[0],
                            coordinate[1]
                        )
                        coordinates.append(
                            [coordinate_new[0], coordinate_new[1]]
                        )
                elif type == 'MultiPolygon':
                    for record in records:
                        for coordinate in record:
                            coordinate_new = transform(
                                in_proj,
                                out_proj,
                                coordinate[0],
                                coordinate[1]
                            )
                            coordinates.append(
                                [coordinate_new[0], coordinate_new[1]]
                            )
                attributes = feature['properties']
                school = attributes[self.school_param]
                address = attributes['ADDRESS']
                city = attributes['CITY']
                self.addresses.update({school: (address + ' ' + city)})
                geo_new = {'type': type, 'coordinates': [coordinates]}
                features_new.append(
                    dict(
                        type='Feature',
                        geometry=geo_new,
                        properties=attributes)
                    )
        json_file = open(self.output2, 'w')
        json_file.write(
            dumps(
                {'type': 'FeatureCollection', 'features': features_new},
                indent=2)
                + '\n'
            )
        json_file.close()

    def get_coordinates(self):
        self.coordinates = {}
        print("Getting GPS coordinates of schools ...")
        for school in self.addresses.keys():
            address = self.addresses[school]
            nominatim = Nominatim(user_agent='my-application')
            coordinate = nominatim.geocode(address)
            if coordinate is None:
                self.coordinates.update({school:('NA', 'NA')})
            else:
                self.coordinates.update(
                    {school:(coordinate.latitude, coordinate.longitude)}
                )

class MapVisualization(object):
    '''
    a class to visualize the sentiments in an interactive map.

    Parameters:
    coordinates: gps coordiantes of the schools
    score: sentiment score; mean score, proportion, or etc
    option: school district options
    location: centeral location of the school districts
    polygon: the polygon file of each school district

    Methods:
    get_json: converting data to json for donut plot using vincent
    folium_visual: using folium to visualize results
    '''
    def __init__(self, coordinates, score, option, location, polygon):
        self.coordinates = coordinates
        self.score = score
        self.option = option
        self.location = location
        self.polygon = polygon

    def get_json(self, data, school_name):
        pie_chart = vincent.Pie(
            data,
            height=100,
            width=100,
            inner_radius=25
        )
        pie_chart.colors(brew='Set2')
        pie_chart.legend(school_name[:-10])  # -10 ES, -6 MS, -4 HS
        pie_json = pie_chart.to_json()
        return pie_json

    def folium_visual(self, col, file_name):
        nominatim = Nominatim(user_agent='my-application')
        location_center = nominatim.geocode(self.location)
        map = folium.Map(
            location=[location_center.latitude, location_center.longitude],
            zoom_start=11
        )
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
                folium.Marker(
                    location=[lat, lon],
                    popup=pop_up,
                    icon=icon
                ).add_to(map)
        geojson = self.polygon
        folium.GeoJson(geojson, name='geojson').add_to(map)
        map.save(file_name)
        return map

def map_plot(sch_coords, score, option, polygon, distr_type): # distr_type: es, ms, hs
    '''use the class MapVisualization to visualize the results'''
    theme = 'Saving the interactive plot of {} school district'
    print(theme.format(d istr_type))
    plot = MapVisualization(sch_coords, score, option,
                            'Frederick', polygon)
    dir = 'results/{}_{}.html'
    plot_visual = plot.folium_visual(
        'blue',
        dir.format(distr_type, option)
    )
    return plot_visual
