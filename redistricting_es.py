#!/usr/bin/env python

# I developed a redistrict module
# it is in the same directory of the github link
from redistrict import *

def main():
    # old school names
    sch_names_old = ['Centerville ES', 'Deer Crossing ES', 'Green Valley ES',
                     'Kemptown ES','Liberty ES', 'New Market ES',
                     'Oakdale ES', 'Spring Ridge ES', 'Twin Ridge ES']
    # column names for the table of comments
    columns = ['Live-in School', 'Comments']
    # school categories
    names = ['Elementary','Middle', 'High']
    # pages for school districts with three different options
    es_pages = ['4-26', '27-47', '48-96']
    ms_pages = ['97-109', '110-122', '123-144']
    hs_pages = ['145-160', '161-176', '177-213']
    # three different options
    options = ['A', 'B', 'AB']
    # pdf file name
    file = 'data/comments/LOU_SurveyResultsJune.pdf'
    # building a sql database and storing data into the database
    # comments on elementary
    es_comments = merge_dfs(file, es_pages, columns, sch_names_old, options)
    # comments on middle
    ms_comments = merge_dfs(file, ms_pages, columns, sch_names_old, options)
    # comments on high
    hs_comments = merge_dfs(file, hs_pages, columns, sch_names_old, options)
    for name, comments in zip(names, [es_comments, ms_comments, hs_comments]):
        df2sql(name, db, comments)
    # visualize the data in a Word Cloud
    senti_es_a = SentiComments(file, '4-26', columns, sch_names_old, 'A')
    senti_es_a.plot_words()
    plt.show()
    # Calculate sentiment score
    es_a_score = senti_es_a.senti_score()
    # replace 'ES' with 'Elementary'
    for key in es_a_score.keys():
        new_key = re.sub('ES', 'Elementary', key)
        es_a_score[new_key] = es_a_score.pop(key)
    # convert shapefiles
    # for elementary schools
    elementary_schs = change_names(sch_names_old)[0]
    json_es = Shape2Json('data/shapefiles/Elementary_School_Districts.shp',
                         'results/json_es.json',
                         'results/json_es_converted.json',
                         'SCHOOL_1',
                         elementary_schs)
    json_es.convert_json()
    json_es.convert_epsg()
    json_es.get_coordinates()
    coordinates_es = json_es.coordinates
    # Fixing the missing coordinates based on info at MapQuest Developer website:
    # elementary schools
    coordinates_es['Deer Crossing Elementary'] = (39.4038, -77.2913)
    coordinates_es['Kemptown Elementary'] = (39.3297, -77.2341)
    coordinates_es['Oakdale Elementary'] = (39.3955, -77.3189)
    coordinates_es['Green Valley Elementary'] = (39.3434, -77.2657)
    # plot the results
    map_plot(coordinates_es, es_a_score, 'A',
            'results/json_es_converted.json',
            'elementary')

if __name__ == '__main__':
    main()
