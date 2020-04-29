#!/usr/bin/env python

import numpy as np
import pandas as pd
import geopandas as gpd
import camelot
import seaborn as sns
import sqlite3
import vincent
import folium
import streamlit as st
from itertools import chain
from geopy.geocoders import Nominatim
from nltk import tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import plotly.figure_factory as ff
import matplotlib.pyplot as plt


class PdfTable:
    ''' a class to get the data of the table from pdf file
    '''
    def __init__(self, pdFile, grade, schDict):
        self.pdFile = pdFile
        self.grade = grade
        self.schDict = schDict
        self.pageList()
        self.names()
        self.options()

    def pageList(self):
        return self.schDict[self.grade][4]

    def names(self):
        return self.schDict[self.grade][1]

    def options(self):
        return self.schDict[self.grade][5]

    def readPDF(self, pages):
        dat = camelot.read_pdf(self.pdFile, pages=pages)
        return [(tb.df[1], tb.df[2]) for tb in dat]

    def scrapeData(self):
        page_list = self.pageList()
        sch_names = self.names()
        options = self.options()
        dfs = pd.DataFrame()

        for pages, option in zip(page_list, options):
            dat = self.readPDF(pages=pages)
            df = pd.DataFrame()
            for tb in dat:
                df_tb = pd.DataFrame(tb).T
                df = pd.concat([df, df_tb], axis=0)
            df.columns = ['Live-in School', 'Comments']
            df = df[df['Comments'] != 'N/A']
            df = df[df['Comments'] != 'n/a']
            schools = df['Live-in School']
            df = df.loc[schools.isin(sch_names)]
            df['Option'] = option
            dfs = pd.concat([dfs, df], axis=0)

        if self.grade == 'Middle':
            new_name_list = []
            for v in dfs['Live-in School']:
                if v == 'Gov. T.J. MS':
                    new_name_list.append('Governor Thomas Jeffson MS')
                else:
                    new_name_list.append(v)
            dfs['Live-in School'] = new_name_list
            return dfs
        else:
            return dfs

def df2sql(name, db, df):
    '''dumps the df into the SQL database'''
    conn = sqlite3.connect(db)
    df.to_sql(name, conn, if_exists='replace')

class CommentSentiments:
    ''' a class to analyze the sentiments of comments from local
        communities with regrads the shcool redistricting proposal

        Parameters:
        db: sql database storing all comments
        grade: elementary, middle, or high school districts
        option: 'A', 'B', 'AB'

        Methods:
        getComments: reading the comments from sql database
        plotWords: making word cloud plots of each grade
        scoreSentiment: calculating the sentiments scores of each school
                        using Valence Aware Dictionary and sEntiment Reasoner;
                        the componud scores were chosen for analyses.
        scoreBySchool: produce all raw scores of each school
        analyzeScores: analyze the scores using by the cut of line +-0.05
        visualizeBySchools: show the distribution of the sentiment scores
        visualizeMean: show the mean sentiment scores
    '''

    def __init__(self, db, grade, option):
        self.db = db
        self.grade = grade
        self.option = option

    def getComments(self):
        conn = sqlite3.connect(self.db)
        df = pd.read_sql_query(
            "SELECT * FROM {0} WHERE Option='{1}'"
            .format(self.grade, self.option),
            conn)
        df.drop(['index'], axis=1, inplace=True)
        conn.close()
        return df

    def plotWords(self):
        tokenizer = RegexpTokenizer(r'\w+')
        stop_words = stopwords.words('english')
        data = self.getComments()
        words = [tokenizer.tokenize(row[1]) for _, row in data.iterrows()]
        words_clean =[word.lower() for word in list(chain(*words))
                      if word.lower() not in stop_words]
        comments_wc = WordCloud(
                        background_color='white',
                        max_words=2000,
                        stopwords=stop_words)
        comments_wc.generate(str(words_clean))
        fig = plt.figure(figsize=(20,10), facecolor='k')
        plt.imshow(comments_wc, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)

    def scoreSentiment(self):
        # Vader (Valence Aware Dictionary and sEntiment Reasoner)
        SentiAnalyzer = SentimentIntensityAnalyzer()
        schools = []
        scores = []
        results = {}
        data = self.getComments()
        for _, comment in data.iterrows():
            schools.append(comment[0])
            score = SentiAnalyzer.polarity_scores(str(comment[1]))
            scores.append(score['compound'])
        df_scores = pd.DataFrame([schools, scores]).T
        df_scores.columns = ['School', 'Score']
        return df_scores

    def scoreBySchool(self):
        df = self.scoreSentiment()
        scores = {}
        for school in df['School'].unique():
            score = df[df['School'] == school]
            score = score['Score'].astype(float)
            scores.update({school: score})
        return scores

    def analyzeScores(self):
        df = self.scoreBySchool()
        results = {}
        for school in df.keys():
            score = df[school]
            # mean sentiments
            score_mean = round(np.mean(score), 3)
            num_scores = len(score)
            # positive sentiment
            results_pos = len(score[score >= 0.05])
            results_pos = round(results_pos/num_scores, 3)
            # negative sentiment
            results_neg = len(score[score <= -0.05])
            results_neg = round(results_neg/num_scores, 3)
            # neutural sentiment
            results_neu = len(score[score <= 0.05][score >= -0.05])
            results_neu = round(results_neu/num_scores, 3)
            results.update(
                {school:
                    {self.option:
                        {'Positive':results_pos,
                         'Negative':results_neg,
                         'Neutral':results_neu,
                         'Mean': score_mean
                         }}})
        return results

    def visualizeBySchools(self):
        schoolScores = self.scoreBySchool()
        schooList = list(schoolScores.keys())
        scores = [score.values for _, score in schoolScores.items()]
        idxs = [idx for idx, val in enumerate(scores) if len(val) < 2]
        for idx in idxs:
            scores.pop(idx)
            schooList.pop(idx)
        fig = ff.create_distplot(scores, schooList, bin_size=0.05)
        fig.update_layout(
            autosize=False,
            width=750,
            height=600,
            margin=dict(l=0, r=30, t=15, b=10)
            )
        return fig

    def visualizeMean(self):
        averageScores = self.analyzeScores()
        schools = list(averageScores.keys())
        num = len(schools)
        a = num / 9 # largest number of the schools in district: ES
        meanValues = [list(v.values())[0]['Mean']
                       for v in averageScores.values()]
        df = pd.DataFrame([schools, meanValues]).T
        df.columns = ['School', 'Mean']
        fg, ax = plt.subplots(figsize=(13, 6*a+0.5))
        ax.tick_params(axis='y', which='major', labelsize=13)
        ax.barh(df['School'], df['Mean'], align='center', height=0.6)
        ax.axvline(0.05, ls='--', color='r')
        ax.axvline(-0.05, ls='--', color='r')
        ax.text(-0.15, num, 'Negative', fontsize=20, color='green')
        ax.text(-0.02, num, 'Neutural', fontsize=20, color='green')
        ax.text(0.10, num, 'Positive', fontsize=20, color='green')
        ax.set_xlabel('Sentiment score', fontsize=20)
        ax.set_xlim(-0.2, 0.2)

def shape2PDF(folder, schDict, grade):
    if grade == 'Middle':
        schDict[grade][1][0]='Governor Thomas Johnson MS'
    else:
        schDict = schDict
    directory = folder + schDict[grade][2]
    df = gpd.read_file(directory).to_crs({'init':'epsg:4326'})
    df.rename(columns={df.columns[1]: 'School'}, inplace=True)
    df['School'] = [
        row[1].replace(grade, schDict[grade][0])
        for _, row in df.iterrows()]
    df['ZIP_CODE'] = df['ZIP_CODE'].astype(int)
    df = df[df['School'].isin(schDict[grade][1])]
    return df

class VisualizeResults:
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
    def __init__(self, gdf, scores):
        self.gdf = gdf
        self.scores = scores
        self.nominatim()

    def nominatim(self):
        return Nominatim(user_agent='my-application')

    def getCoords(self):
        coords = {}
        print("Getting GPS coordinates of schools ...")
        for _, row in self.gdf.iterrows():
            add = row['ADDRESS'] + ', ' + str(row['ZIP_CODE'])
            school = row['School']
            coord = self.nominatim().geocode(add)
            if coord is None:
                coords.update({school:('NA', 'NA')})
            else:
                coords.update(
                    {school:(coord.latitude, coord.longitude)}
                )
        print(coords)
        return coords

    def json2PieChart(self, score, schName):
        pieChart = vincent.Pie(
            score,
            height=100,
            width=100,
            inner_radius=25
        )
        pieChart.colors(brew='Set2')
        pieChart.legend(schName)  # -10 ES, -6 MS, -4 HS
        pieJson = pieChart.to_json()
        return pieJson

    def score2Json(self):
        schools = self.scores.keys() # school list
        scores = self.scores.values() # results of analyzing scores
        coords = self.getCoords()
        for school in schools:
            lat = coords[school][0]
            lon = coords[school][1]
            if lat == 'NA' or lon == 'NA':
                continue
            else:
                score = list(scores)[0]
                keys = ['Positive', 'Negative', 'Neutral']
                score = {k:score[key] for key in keys}
            return score

    def visualMap(self):
        mdCoords = [39.38, -77.36] #  Frederick County MD GPS coordinates
        map = folium.Map(
            location=[
            mdCoords[0], mdCoords[1]],
            zoom_start=11,
            control_scale=True,
            prefer_canvas=True,
            disable_3d=True
        )
        schools = self.scores.keys() # school list
        scores = self.scores.values() # results of analyzing scores
        coords = self.getCoords()
        meanScores = []

        for school in schools:
            lat = coords[school][0]
            lon = coords[school][1]
            if lat == 'NA' or lon == 'NA':
                continue
            else:
                score = list(self.scores[school].values())[0]
                keys = ['Positive', 'Negative', 'Neutral']
                meanScore = score['Mean']
                meanScores.append(meanScore)
                score = {k:score[k] for k in keys}
                chart = self.json2PieChart(score, school)
                vega = folium.Vega(chart, width=200, height=100)
                pop_up = folium.Popup(max_width=400).add_child(vega)
                icon = folium.Icon(color='blue', icon='info-sign')
                folium.Marker(
                    location=[lat, lon],
                    popup=pop_up,
                    icon=icon
                ).add_to(map)

        dat = pd.DataFrame([schools, meanScores]).T
        dat.columns=['School','Mean Score']
        print(dat)

        folium.Choropleth(
            geo_data=self.gdf,
            name='choropleth',
            data=dat,
            columns=['School','Mean Score'],
            key_on='feature.properties.School',
            fill_color='YlGnBu',
            legend_name='Mean sentiment score',
            na_fill_color='white',
            na_fill_opacity=0.2,
            fill_opacity=0.7,
            line_weight=0.6,
            line_opacity=0.2).add_to(map)

        return map
