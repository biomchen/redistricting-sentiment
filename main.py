import csv
import glob
import os
import re
import pandas as pd
import numpy as np
from redistrict.senti import SentimentAnalysis
from redistrict.shp_json import Shape2Json
from redistrict.map_visual import MapVisualization


'''
Preprocessing data
'''
# old school names
school_names_old = ['Centerville ES', 'Deer Crossing ES', 'Green Valley ES',
                    'Kemptown ES', 'Liberty ES', 'New Market ES',
                    'Oakdale ES', 'Spring Ridge ES', 'Twin Ridge ES',
                    'Urbana ES', 'Gov. T.J. MS', 'New Market MS',
                    'Oakdale MS', 'Urbana MS', 'Windsor Knolls MS',
                    'Linganore HS', 'Oakdale HS', 'Urbana HS']

# repalce ES, MS, and HS with Elementary, Middle, and High
# in corresponding school names in shapefile
school_names_new = []
elementary_schs = []
middle_schs = []
high_schs = []

for name in school_names_old:
    school_type = name.split(' ')[-1]
    if school_type == 'ES':
        new_name = re.sub('ES', 'Elementary', name)
        elementary_schs.append(new_name)
        school_names_new.append(new_name)
    elif school_type == 'MS':
        new_name = re.sub('MS', 'Middle', name)
        middle_schs.append(new_name)
        school_names_new.append(new_name)
    elif school_type == 'HS':
        new_name = re.sub('HS', 'High', name)
        high_schs.append(new_name)
        school_names_new.append(new_name)

# make dictionary based old and new school names
school_names_dict = {old_name: new_name for (old_name, new_name)
                     in zip(school_names_old, school_names_new)}
# comments based on proposal A, B, and other thoughts on AB
options = ['A', 'B', 'AB']
# Reading all comments from the excel file.
df = pd.read_excel('data/LOU_results.xlsx', sheet_name='All_data')
# replace school names so they are consistent with the names in shapefile.
for key in school_names_dict.keys():
    df['School'] = df['School'].replace(key, school_names_dict[key])
# generate the file for each category,
# such as comments_Centerville Elementary_A
for school in school_names_new:
    for option in options:
        text = open('results/comments_{0}_{1}.txt'.format(school, option), 'w')
        school_comments = df[df.School == school][df.Option == option].Comments
        for comment in school_comments:
            comment = str(comment)
            text.write(comment)
    text.close()

'''
Sentiment Analysis
a. Calculate the scores based on different weighting;
b. Calculate the proportions of the positive, negative, and neutral words;
c. Attain raw scores of words in the data.
'''
path = 'results/'
# make dictionaries to store the results
scores_mean = {}
scores_per = {}
scores_raw = {}

for school in school_names_new:
    scores_mean[school] = {}
    scores_per[school] = {}
    scores_raw[school] = {}
    for option in options:
        scores_mean[school][option] = {}
        scores_per[school][option] = {}
        scores_raw[school][option] = {}
        senti_analysis = SentimentAnalysis()
        new_path = os.path.join(path,
                                'comments_{}_{}.txt'.format(school, option))
        files = glob.glob(new_path)
        for file in files:
            comment = open(file, 'r')
            if len(comment.read()) == 0:
                scores_mean[school][option] = 'NA'
                scores_per[school][option] = 'NA'
                scores_raw[school][option] = 'NA'
            else:
                score = senti_analysis.score_text(file)
                scores_mean[school][option] = score[0]
                scores_per[school][option]['Positive'] = score[1]
                scores_per[school][option]['Negaitive'] = score[2]
                scores_per[school][option]['Neutral'] = score[3]
                scores_raw[school][option] = score[-1]

'''
Convert shapfile to Geojson
'''
# for elementary schools
json_es = Shape2Json('shapefiles/Elementary_School_Districts.shp',
                     'results/jsonES.json',
                     'results/jsonESConverted.json',
                     'SCHOOL_1',
                     elementary_schs)
json_es.convert_json()
json_es.convert_epsg()
json_es.get_coordinates()
coordinates_es = json_es.coordinates
# for middle schools
json_ms = Shape2Json('shapefiles/Middle_School_Districts.shp',
                     'Results/jsonMS.json',
                     'Results/jsonMSConverted.json',
                     'SCHOOL',
                     middle_schs)
json_ms.convert_json()
json_ms.convert_epsg()
json_ms.get_coordinates()
coordinates_ms = json_ms.coordinates
# for high schools
json_hs = Shape2Json('shapefiles/High_School_Districts.shp',
                     'results/jsonHS.json',
                     'results/jsonHSConverted.json',
                     'SCHOOL',
                     high_schs)
json_hs.convert_json()
json_hs.convert_epsg()
json_hs.get_coordinates()
coordinates_hs = json_hs.coordinates

'''
Fix the coordinates missing from previous analyses by manual enter them
'''
coordinates_es['Deer Crossing Elementary'] = (39.4038, -77.2913)
coordinates_es['Kemptown Elementary'] = (39.3297, -77.2341)
coordinates_es['Oakdale Elementary'] = (39.3955, -77.3189)
coordinates_es['Green Valley Elementary'] = (39.3434, -77.2657)

coordinates_ms['Urbana Middle'] = (39.330684, -77.336379)
coordinates_ms['Windsor Knolls Middle'] = (39.322002, -77.278516)
coordinates_ms['Oakdale Middle'] = (39.337555, -77.305634)

coordinates_hs['Oakdale High'] = (39.394418, -77.309328)
coordinates_hs['Urbana High'] = (39.324881, -77.339102)

'''
Visulization using Folium
Basic inputs for the visualization:
coordinates: coordinates_es, coordinates_ms, coordinates_hs
option: 'A', 'B', 'AB'
JSON file: json_es_converted.json, json_ms_converted.json,
           json_hs_converted.json
sentiment score: scores_per
'''

es_A = MapVisualization(coordinates_es,
                        scores_per,
                        'A',
                        'Frederick, MD',
                        'results/json_es_converted.json')
es_a.foliumVisual('blue')
