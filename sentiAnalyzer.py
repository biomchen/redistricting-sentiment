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
st.title('Better or Worse?')
st.markdown('''<p style='text-align: left; color: teal; font-size: 22px'>\
    Sentiment Aanlyses on community feedbacks of the Linganore-Oakdale-Urbana \
    (LOU) Area of Frederick County, MD, regarding to School Redistricting \
    Proposals.</p3>''',
    unsafe_allow_html=True)
# seting up the sidebar and loading the data
st.sidebar.title('Make a selection')
st.sidebar.markdown('**School Districts**')
grade = st.sidebar.selectbox('Choose district',
    list(sch_dict.keys()))
st.sidebar.markdown('**Options**')
option = st.sidebar.selectbox('Choose option',
    list(sch_dict[grade])[5])
st.sidebar.markdown("* **Option AB** refers to related but unspecified comments \
    towards to either Option A or Option B.")

st.sidebar.markdown("**Project Description**")
st.sidebar.markdown('''**Problem**''')
st.sidebar.markdown(
    '''* School redistricting in Linganore-Oakdale-Urbana (LOU) area has \
    stirred outcry from the local communities in the social media. \
    In order to understand the concerns about local communities, Frederick \
    County Board of Education provided an online platform for community \
    members to express their opinions and conducted a basic statistics of \
    local community concerns. However, their analyses lack of \
    details about what sentiment of the local communities were and why the \
    communities show favor/disfavor to the school redistricting plans.'''
    )
st.sidebar.markdown('''**Approach**''')
st.sidebar.markdown(
    '''* Created a python module `redistrict` to help perform data extraction, \
    exploratory analyses, sentiment calculation, and result visualization \
    with regard to the community feedbacks for proposed school redistrict \
    plans. ''')

st.sidebar.markdown('''**Insights**''')
st.sidebar.markdown(
    '''* The positive feedbacks of LOU commmunities \
    towards the second-round-proposed school redistricting plans indicate \
    that the latest plans present merits that statisfy local communities.''')
st.sidebar.markdown(
    '''* Using interactive analyses on the sentiment, local education \
    adminstration could effectively identify where needs are and tailor its \
    resources to address those local community needs, which would save time \
    and money.''')
st.sidebar.markdown(
    '''* My web app could serve as a platform for general public \
    to understand their neighbours' feelings of the school redistricting \
    studies. For more details, please click [here]\
    (https://biomchen.github.io/redistricting.html).
    '''
    )

comSenti = CommentSentiments(db, grade, option)

st.markdown('''<h2 style='text-align: left; color: black;'>Wold Clouds of \
    LOU Feedbacks''',
    unsafe_allow_html=True
   )
st.markdown(
    '''The feedbacks were provided in a over-200-page pdf file. The \
    class `PdfTable` was developed to scrape and parse data from the table.''')
comSenti.plotWords()
st.pyplot()

st.markdown('''<h2 style='text-align: left; color: black;'>Interactive Plot of \
    Sentiment Scores</h2>''',
    unsafe_allow_html=True
    )
st.markdown(
    '''The sentiment score was calculated with Valence Aware Dictionary and \
    sEntiment Reasoner (`VADER`); the componud scores were used by the \
    developed class `CommentSentiments` for analyses.''')
fig = comSenti.visualizeBySchools()
st.plotly_chart(fig)

st.markdown(
    '''<h2 style='text-align: left; color: black;'>Mean Sentiment Score of \
    LOU School Districts</h2>''',
     unsafe_allow_html=True
    )
st.markdown(
    '''The average score of each school regarding to the selected option.''')
comSenti.visualizeMean()
plt.show()
st.pyplot()

st.markdown(
    '''<h2 style='text-align: left; color: black;'>Interactive Map for LOU \
    School Districts</h2>''',
     unsafe_allow_html=True
    )
st.markdown(
    '''Visualize the mean sentiment score of each school on US OpenStreetMap \
    (OSM) data using the developed class `VisualizeResults`.''')

def main():
    gdf = shape2PDF(folder, sch_dict, grade)
    score = comSenti.analyzeScores()
    map = VisualizeResults(gdf, score).visualMap()
    return st.markdown(map._repr_html_(), unsafe_allow_html=True)

main()

st.markdown('''The web app is created by [Meng Chen]\
    (https://biomchen.github.io). If you have any comments or suggestios, \
    please send email to meng.chen03(at)gmail.com.''')
