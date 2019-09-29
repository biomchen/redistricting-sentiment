from redistrict import *

# old school names
sch_names_old = ['Centerville ES', 'Deer Crossing ES', 'Green Valley ES',
                 'Kemptown ES','Liberty ES', 'New Market ES',
                 'Oakdale ES', 'Spring Ridge ES', 'Twin Ridge ES',
                 'Urbana ES', 'Gov. T.J. MS', 'New Market MS',
                 'Oakdale MS', 'Urbana MS', 'Windsor Knolls MS',
                 'Linganore HS', 'Oakdale HS', 'Urbana HS']
# get school comments
sch_comments = SchoolComments(sch_names_old)

# get school new names
sch_names = sch_comments.make_dict()[1]
elementary_schs = sch_comments.make_dict()[2]
middle_schs = sch_comments.make_dict()[3]
high_schs = sch_comments.make_dict()[4]

# save the comments
fname = 'data/comments/LOU_results.xlsx'
sheet_name = 'All_data'
sch_comments.write_comments(fname, sheet_name)

# get sentiment scores
scores_mean = get_score(sch_names)[0] # mean scores
scores_per = get_score(sch_names)[1] # percentage score
scores_raw = get_score(sch_names)[2] # raw scores

# convert shapefiles
# for elementary schools
json_es = Shape2Json('data/shapefiles/Elementary_School_Districts.shp',
                     'results/json_es.json',
                     'results/json_es_converted.json',
                     'SCHOOL_1',
                     elementary_schs)
json_es.convert_json()
json_es.convert_epsg()
json_es.get_coordinates()
coordinates_es = json_es.coordinates

# Fixing the missing coordinates based on the search
# at MapQuest Developer website:
# elementary schools
coordinates_es['Deer Crossing Elementary'] = (39.4038, -77.2913)
coordinates_es['Kemptown Elementary'] = (39.3297, -77.2341)
coordinates_es['Oakdale Elementary'] = (39.3955, -77.3189)
coordinates_es['Green Valley Elementary'] = (39.3434, -77.2657)

# plot the results
map_plot(coordinates_es, scores_per, 'A',
        'results/json_es_converted.json', 'elementary')
