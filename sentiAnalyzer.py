import redistrict
from redistrict import *
import streamlit as st

db = 'LOU_School_Comments.sqlite'
folder = 'data/shapefiles/'
sch_dict = {
    'Elementary': [
        'ES', # short for elemenetary schools
        [
            'Centerville ES', 'Deer Crossing ES', 'Green Valley ES',  # all LOU ES
            'Kemptown ES', 'Liberty ES', 'New Market ES', 'Oakdale ES',
            'Spring Ridge ES', 'Twin Ridge ES'
        ],
        'Elementary_School_Districts.shp', # the ES shapefile
        'SCHOOL_1', # the column name of the school names in the ES shapefile
        ['4-26', '27-47', '48-96'], # comments on options A, B, and AB, respectively.
        ['A', 'B', 'AB'] # option: A, B, AB
    ],
    'Middle': [
        'MS', # short for middle schools
        [
            'Gov. T.J. MS', 'New Market MS', 'Oakdale MS', # all LOU MS
            'Urbana MS', 'Windsor Knolls MS'
        ],
        'Middle_School_Districts.shp', # the MS shapefile
        'SCHOOL', # the column name of the school names in the MS shapefile
        ['97-109', '110-122', '123-144'], # comments on options A, B, and AB, respectively.
        ['A', 'B', 'AB'] # option: A, B, AB
    ],
    'High': [
        'HS', # short for high schools
        [
            'Linganore HS', 'Oakdale HS', 'Urbana HS' # all LOU HS
        ],
        'High_School_Districts.shp', # the HS shapefile
        'SCHOOL', # the column name of the school names in the HS shapefile
        ['145-160', '161-176', '177-213'], # comments on options A, B, and AB, respectively.
        ['A', 'B', 'AB'] # option: A, B, AB
    ]
}


# set the title of web app
st.title('Feel Better or Feel Worse?')
st.markdown('''<p style='text-align: left; color: teal; font-size: 22px'>\
    Sentiment Aanlyses on community feedbacks of the Linganore-Oakdale-Urbana \
    (LOU) Area of Frederick County, MD, regarding to School Redistricting \
    Proposals.</p3>''',
    unsafe_allow_html=True)
# seting up the sidebar and loading the data
st.sidebar.title('Select School District and Option')
st.sidebar.markdown('**School Districts**')
grade = st.sidebar.selectbox('Choose your focus district',
    list(sch_dict.keys()))
st.sidebar.markdown('**Proposed Options**')
option = st.sidebar.selectbox('Choose your faverite option',
    list(sch_dict[grade])[5])

st.sidebar.markdown("**Project **")
st.sidebar.markdown(
    '''**Issue**: Sentiment plays an important role in modern society \
    as the success of the social media development around the globe. School \
    redistricting in Linganore-Oakdale-Urbana (LOU) area has stirred outcry \
    from the local communities in the social media. In order to understand \
    the concerns about local communities, Frederick County Board of Education \
    provided an online platform for community members to express their \
    opinions and conducted a basic statistics of local community concerns. \
    However, the statistical analyses lack of details about what sentiment of \
    the local communities were and why the communities show favor/disfavor to \
    the school redistricting plans.'''
    )
st.sidebar.markdown(
    '''**Approach**: In order to understand these, I created a python module \
    `redistrict` to help perform sentiment analyses on the feedbacks of local \
    communities for different proposed school redistrict plans. '''
    )
st.sidebar.markdown(
    '''**Insights**: It shows that local communities more strongly oppose \
    to any changes of the middle and high schools in comparison with that of \
    the elementary schools. Despite this general pattern, the sentiments of \
    different school districts vary and you can find more details by \
    clicking [here](https://biomchen.github.io/redistricting.html). '''
    )

comSenti = CommentSentiments(db, grade, option)

st.markdown('''<h2 style='text-align: left; color: black;'>Wold Clouds of \
    feedbacks''',
    unsafe_allow_html=True
   )
st.markdown(
    '''The feedbacks were provided in a more-than-200-page pdf file. The \
    `camelot` package was used to scrape table data from the file.''')
#comSenti.plotWords()
#st.pyplot()

st.markdown('''<h2 style='text-align: left; color: black;'>Senttiment Score \
    Distribution</h2>''',
    unsafe_allow_html=True
    )
st.markdown(
    '''The sentiment score was calculated with Valence Aware Dictionary and \
    sEntiment Reasoner (`VADER`) from `NLTK`; the componud scores were used \
    for analyses.''')
#fig = comSenti.visualizeBySchools()
#st.plotly_chart(fig)

st.markdown(
    '''<h2 style='text-align: left; color: black;'>Mean Sentiment Score\
    </h2>''',
     unsafe_allow_html=True
    )
st.markdown(
    '''The average score of each school with regard to the option.''')
#comSenti.visualizeMean()
#plt.show()
#st.pyplot()

st.markdown(
    '''<h2 style='text-align: left; color: black;'>Interactive Map for Each \
    School District
    </h2>''',
     unsafe_allow_html=True
    )
st.markdown(
    '''Visualize the Mean Sentiment Score of Each School on US OpenStreetMap \
    (OSM) data using `Folium`.''')

def main():
    gdf = shape2PDF(folder, sch_dict, grade)
    score = comSenti.analyzeScores()
    map = VisualizeResults(gdf, score).visualMap()
    return st.markdown(map._repr_html_(), unsafe_allow_html=True)

main()

st.markdown('''The web app is created by [Meng Chen](https://biomchen.github.io)\
 with `Streamlit`.''')
