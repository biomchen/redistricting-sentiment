import re
import csv
import glob
import os
import json
import pandas as pd
import numpy as np
from json import dumps
import shapefile
from pyproj import Proj, transform
from geopy.geocoders import Nominatim
from pandas.io.json import json_normalize
import vincent
import folium


class SchoolComments(object):
    '''
    Object to get comments from parents from different
    elementary, middle, and high school districts.

    Attributes:
    -----------
    old_names: school names in comments file

    '''
    def __init__(self, old_names):
        self.old_names = old_names
        self.make_dict()

    def make_dict(self):
        new_names = []
        elementary_schs = []
        middle_schs = []
        high_schs = []
        for name in self.old_names:
            sch_type = name.split(' ')[-1]
            if sch_type == 'ES':
                new_name = re.sub('ES', 'Elementary', name)
                elementary_schs.append(new_name)
                new_names.append(new_name)
            elif sch_type == 'MS':
                new_name = re.sub('MS', 'Middle', name)
                middle_schs.append(new_name)
                new_names.append(new_name)
            elif sch_type == 'HS':
                new_name = re.sub('HS', 'High', name)
                high_schs.append(new_name)
                new_names.append(new_name)

        names_dict = {old_name: new_name for (old_name, new_name)
                      in zip(self.old_names, new_names)}

        return (names_dict,
                new_names,
                elementary_schs, middle_schs, high_schs)

    def write_comments(self, fname, sheet, options=['A', 'B', 'AB']):
        df = pd.read_excel(fname, sheet_name=sheet)
        names_dict = self.make_dict()[0]
        for key in names_dict.keys():
            df['School'] = df['School'].replace(key, names_dict[key])

        new_names = self.make_dict()[1]
        for sch in new_names:
            for opt in options:
                txt = open('results/comments_{0}_{1}.txt'.format(sch, opt),
                           'w')
                comments = df[df.School == sch][df.Option == opt].Comments
                for comment in comments:
                    comment = str(comment)
                    txt.write(comment)
            txt.close()


class SentimentAnalysis(object):
    """
    A class to analyze sentiments of the comments from
    LOU redistricting survey.

    Attributes
    --------
    base: SentiWordNet 3.0 dataset

    """

    def __init__(self, base='SentiWordNet.txt'):
        self.base = base
        self.swn_all_words = {}
        self.build_swn(base)

    def build_swn(self, base):
        records = [line.split('\t') for line in open(self.base)]
        for rec in records:
            word = rec[4].split('#')[0]
            true_score = float(rec[2]) - float(rec[3])
            if word not in self.swn_all_words:
                self.swn_all_words[word] = {}
                self.swn_all_words[word]['score'] = true_score

    def weighting(self, method, scores_list):
        if method == 'arithmetic':
            scores = 0
            for score in scores_list:
                scores += score
            weighted_sum = scores/len(scores_list)
        elif method == 'geometric':
            weighted_sum = 0
            num = 1
            for score in scores_list:
                weighted_sum += (score * (1/2**num))
                num += 1
        elif method == 'harmonic':
            weighted_sum = 0
            num = 2
            for score in scores_list:
                weighted_sum += (score * (1/num))
                num += 1
        return weighted_sum

    def clean_text(self, filename):
        if '.txt' in filename or '.csv' in filename:
            texts_clean_all = []
            data = open(filename, encoding='utf8')
            texts = [line.rsplit() for line in data]
            try:
                for line in texts:
                    for text in line:
                        text_clean = text.lower()
                        text_clean = re.sub(
                            r'[.?!;:@#$%^&*()-_+={}[]|\>/’"]', '', text_clean)
                        texts_clean_all.append(text_clean)
                return texts_clean_all
            except Exception:
                return "name error"
        else:
            try:
                text_clean = filename.lower()
                text_clean = re.sub(
                    r'[.?!;:@#$%^&*()-_+={}[]|\>/’"]', '', text_clean).split()
                return text_clean
            except Exception:
                return "name error"

    def score_text(self, text):
        scores_all = []
        scores = 0
        total_count = 0
        positive_count = 0
        negative_count = 0
        final_score = {}
        methods = ['arithmetic', 'geometric', 'harmonic']
        text_set = set(self.clean_text(text))
        key_set = set(self.swn_all_words.keys())

        for word in text_set.intersection(key_set):
            single_score = self.swn_all_words[word]['score']
            if single_score > 0:
                positive_count += 1
            elif single_score < 0:
                negative_count += 1
            total_count += 1
            scores_all.append(single_score)

        if total_count >= 1:
            for method in methods:
                score = self.weighting(method, scores_all)
                final_score[method] = round(score, 3)
            positive = round(positive_count/total_count, 3)
            negative = round(negative_count/total_count, 3)
            neutral = 1 - positive - negative
            return (list(final_score.values()),
                    positive,
                    negative,
                    neutral,
                    scores_all)
        else:
            return 0


def get_score(sch_names, options=['A', 'B', 'AB'], path='results/'):
    '''
    A function to get the sentiment scores of each school district

    '''
    # make dictionaries to store the results
    scores_mean = {}
    scores_per = {}
    scores_raw = {}

    for sch in sch_names:
        scores_mean[sch] = {}
        scores_per[sch] = {}
        scores_raw[sch] = {}
        for option in options:
            scores_mean[sch][option] = {}
            scores_per[sch][option] = {}
            scores_raw[sch][option] = {}
            senti_analysis = SentimentAnalysis()
            new_path = os.path.join(path,
                                    'comments_{}_{}.txt'.format(sch, option))
            files = glob.glob(new_path)
            for file in files:
                comment = open(file, 'r')
                if len(comment.read()) == 0:
                    scores_mean[sch][option] = 'NA'
                    scores_per[sch][option] = 'NA'
                    scores_raw[sch][option] = 'NA'
                else:
                    score = senti_analysis.score_text(file)
                    scores_mean[sch][option] = score[0]
                    scores_per[sch][option]['Positive'] = score[1]
                    scores_per[sch][option]['Negaitive'] = score[2]
                    scores_per[sch][option]['Neutral'] = score[3]
                    scores_raw[sch][option] = score[-1]

    return (scores_mean, scores_per, scores_raw)


class Shape2Json(object):
    """
    Object to convert shapefile to json file.

    Attributes
    ----------
    fname : input file name
    output1: output file of json without conversion of EPSG reference
    output2: output file of json with after EPSG conversion
    school_param: field values in shapefile; 'SCHOOL' or 'SCHOOL_1'
    school_list: a list of school names
    addresses: school addresses
    coordinates: coordinates of schools

    """
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
                features.append(dict(type='Feature',
                                geometry=geo_records,
                                properties=attributes))
            else:
                continue

        json_file = open(self.output1, 'w')
        json_file.write(dumps({'type': 'FeatureCollection',
                               'features': features},
                              indent=2) + '\n')
        json_file.close()

    def convert_epsg(self):
        in_proj = Proj(init='epsg:2248')  # pyproj.Proj API parameters
        out_proj = Proj(init='epsg:4326')

        print("coverting its coordinates ...")

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
                        coordinate_new = transform(in_proj,
                                                   out_proj,
                                                   coordinate[0],
                                                   coordinate[1])
                        coordinates.append([coordinate_new[0],
                                            coordinate_new[1]])
                elif type == 'MultiPolygon':
                    for record in records:
                        for coordinate in record:
                            coordinate_new = transform(in_proj,
                                                       out_proj,
                                                       coordinate[0],
                                                       coordinate[1])
                            coordinates.append([coordinate_new[0],
                                                coordinate_new[1]])
                attributes = feature['properties']
                school = attributes[self.school_param]
                address = attributes['ADDRESS']
                city = attributes['CITY']
                self.addresses.update({school: (address + ' ' + city)})
                geo_new = {'type': type, 'coordinates': [coordinates]}
                features_new.append(dict(type='Feature',
                                         geometry=geo_new,
                                         properties=attributes))

        json_file = open(self.output2, 'w')
        json_file.write(dumps({'type': 'FeatureCollection',
                               'features': features_new},
                              indent=2) + '\n')
        json_file.close()

    def get_coordinates(self):
        self.coordinates = {}

        print("getting GPS coordinates ...")

        for school in self.addresses.keys():
            address = self.addresses[school]
            nominatim = Nominatim(user_agent='my-application')
            coordinate = nominatim.geocode(address)
            if coordinate is None:
                self.coordinates.update({school: ('NA', 'NA')})
            else:
                self.coordinates.update({school: (coordinate.latitude,
                                                  coordinate.longitude)})


class MapVisualization(object):
    """
    Object to visualize the sentiments in an interactive map.
    """
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

    def folium_visual(self, col, file_name):
        nominatim = Nominatim(user_agent='my-application')
        location_center = nominatim.geocode(self.location)
        map = folium.Map(location=[location_center.latitude,
                                   location_center.longitude],
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
        map.save(file_name)

        return map


def map_plot(sch_coords, score, option, polygon,
             distr_type): # distr_type: es, ms, hs
    """
    Plot the results.

    Attributes
    ----------
    sch_coordinates: school coordinates
    score: sentiment score as you choose
    option: 'A', 'B'
    polygon: district json file
    distr_type: elementary, middle, or high school

    """
    plot = MapVisualization(sch_coords, score, option,
                            'Frederick', polygon)
    plot_visual = plot.folium_visual('blue',
                                     'results/{}_{}.html'.
                                     format(distr_type, option))

    return plot_visual
