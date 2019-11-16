## Sentiment of Linganore-Oakdale-Urbana Area Redistricting

(**will be updated soon**)

**Meng Chen**                          
Centre for Research and Education on Biological Evolution and Environment          
School of Earth Sciences and Engineering                                                         
Nanjing University, Nanjing, China, 210093   

---
## 1. Introduction

Linganore-Oakdale-Urbana (LOU) Area is located in the southeastern area of the Frederick County of Maryland. During last ten years, the local communities have been transformed into popular suburban residency for people who work in the Washington-Maryland area. Many professionals, such as federal government employees or military personals chose to live in these neighborhoods, despite the distant transportation between their working places and homes. Even some government facilities have been established in this area. For an example, the Social Security Data Center is located next to the Park and Ride of the Exit 26 of Interstate-270 in the Urbana area. Recently, [Kite Pharma](https://www.kitepharma.com) is starting to build a pharmaceutical manufacturing facility here, and along its side, a hotel and associated restaurants will be built in two years. Urbana area has become the prime location for both business and residents.

These ongoing commercial developments bring prosperity to the local communities. So does anxiety. For an example, the workforce brought by Kite Pharma has been estimated about 200-300 employees initially to 700-900 by its capacity. Such huge workforce will need hundreds of homes to accommodate their housing needs in nearby communities. Thus, the estate projects have been steadfastly developed in this area. More and more housing projects start to show themselves off the landscape. In contrast, only two new elementary schools have been added to the entire area, which could not alleviate overcrowd situations in local communities. It becomes clear that, lacking of additional government funding, the Board of Education of Frederick County has an urgent need to conduct school redistricting on the basis of changing feeder patterns.

Starting in January, 2019, Frederick County has contracted with Cropper GIS Consulting to conduct the redistricting study and expected the study would be completed by the end of the 2019. This study primarily focuses on the attendance boundary and feeder patterns of local communities as two new schools have been added to the school district. Supposedly, this project can fully address the enrollment growth in LOU area and provide projections of the school enrollments in next five-eight years. Based on the message of the Board of Education, the redistricting roots in their core belief that all students are entitled equally to respect, opportunity, and excellence ([here for details](https://www.fcps.org/capital-program/linganore-oakdale-urbana-area-redistricting-study)). However, after the Public Engagement Session in March, 2019, the proposed attendance boundary stirred the outrage from local communities based on analyses of the parents' feedbacks provided by the Cropper GIS. Most of parents were extremely frustrated by the proposed new attendance boundaries. Some parents in Urbana area for example organized a local hearing to express their frustration to one of the Board of Education members. In attempt to alleviate the outrage raised from local communities, two entirely new options have been proposed in the Public Engagement Session in June, 2019 to replace the old ones. It is not clear that if those new options satisfying the needs of the local communities despite some positive sign in the parents' feedbacks.

This project is the quantitative assessment of the parents' feedbacks prior to the superintendent's recommendation in the October. It primarily focuses on the sentiment and preferences of parents for new proposed options after the Public Engagement Session in June, 2019. The parents' preferable options will be compared with the plan of the superintendent's recommendation to investigate whether Board of Education's choices are aligned with parents' preferences and seek potential explanation. These will provide the board members the basic understanding of parents preferences quantitatively and help them identify which communities have been mostly affected after June's proposal. In addition, the results will help parents recognize the educational needs of the majority of the their local communities.

It should be noted that this project will apply Natural Language Processing (NLP) techniques and can be broadly implemented in other similar projects.

---
## 2. Materials and Methods

## 2.1 Materials
### 2.1.1 Survey dataset
The survey results after Public Engagement Session in June, 2019 for LOU Redistricting Study can be found in the designed webpage by Frederick County Public Schools [website](https://www.fcps.org/capital-program/lou-meetings). The feedbacks are compiled and represented in numerous tables spreading among 209 pages of single PDF file. I used the `camelot` to extract the feedbacks from numerous tables. The feedbacks can be grouped based on the option and the school type. All feedbacks were saved in a SQL database.

##### **Original Survey Comments**

![](/examples/survey_example.png)

##### **Survey Comments in the SQL database**

![](/examples/survey_example_converted.png)

### 2.1.2 Shapefile
The shapefiles of Frederick County School District have been downloaded at Frederick County [website](https://www.frederickcountymd.gov/5969/Download-GIS-Data). The shapefile contains the basic information of school districts, including school names, school address, the types of schools, and the polygon data that separates school districts. The shapefile was created by ESRI ArcGIS under EPSG 2248. The EPSG was short for European Petroleum Survey Group but now known as the Geomatics Committee of the International Association of Oil and Gas Producers (OGP). 2248 is the EPSG spatial reference ID for Maryland. To project the Maryland to the world map, the original coordinates of Maryland were converted under the spatial reference ID EPSG 4326 of world map. See Methods for details.

---

## 2.2 Methods
I used Python programming language to develop a package `redistrict` to quantify the parents' comments as sentiment score and to visualize the sentiments in interactive maps. Each of class has specific methods for analyzing data, saving outputs, and/or visualizing the results. Three classes are compiled together as a module named 'redistrict'. See below for details of the functionality of each class as well as methods within it.

## The second plot using data of elementary schools with all options
The data and approaches used here were outdated. This is just for the exhibit purpose.

During the fellowship, I will use `nltk.sentiment.vader` to calculate the sentiment score of each comments and cluster schools using `K-means` with the sentiment score. I will add the information of the local business to address the crowdedness of those local communities. To show the project here, I just adopt the outdated methods and data.

For the inital whole project, I will refer you to the notebook `senti_notebook.ipynb` as well as the module I developed `redistrict`.
#### Import the module `redistrict`

### 2.2.1 'redistrict' Package
This package includes three newly developed classes `SentimentAnalysis`, `Shape2Json`, `MapVisualization`. Below is brief description of each class.

Class  | Description
------ | -----------
`SentimentAnalysis` | Build a sentiment score dictionary of words based on SentiWordNet 3.0; calculate the score of the sentiment of parents' feedbacks
`Shape2Json`| Convert the ESRI shapefile to geojson file; convert coordinates from the spatial reference of Maryland to the spatial reference of the world
`MapVisualization` | Visualize the sentiment score of different school districts on a interactive map

### 2.2.1.1 The class for the sentiment analysis
```Python
class SentimentAnalysis(object):
    def __init__(self, base='SentiWordNet.txt'):
        self.base = base
        self.swn_all_words = {}
        self.build_swn(base)
```
In general, this class calculates the scores of the sentiments of words of a string or a text file. The results include mean score, percentage, and raw scores of all scored words. The SentiWordNet 3.0 can be download at [here](https://github.com/aesuli/SentiWordNet).

```Python
    def weighting(self, method, score_list):
```
It uses different weighting methods to calculate the mean of the sentiment score.

Parameter | Description
----|----
`method` | arithmetic, geometric, or harmonic method
`score_list` | a list of the raw sentiment scores of the words

```Python
    def build_swn(self, base):
```
This function builds a dictionary of the sentiment scores of words based on SentiWordNet 3.0. The heading and descriptive details of SentiWordNet project has been removed prior to the input for building the dictionary.

Parameter | Description
----|----
`base` | the sentiment score data of the SentiWordNet project, version 3.0

```Python
    def clean_text(self, filename):
```
It changes the upper case to lower case as well as removes non-word characters in a sentence or a paragraph before compiling them together for scoring the sentiment.

Parameter | Description
----|----
`filename` | an input of either a string or a txt file

```Python
    def score_text(self, text):
```
This scores the sentiment of each word in the sentence or paragraphs, and calculate the mean score (arithmetic, geometric, and harmonic) of the sentiments. In addition, it quantify the percentage of positive, negative, and neural sentiment for understanding the preferences of the parents. Raw score for each word are also be recorded.

Parameter | Description
----|----
`text` | a text or a file name

#### An Example:

**Input**:
```python
SentimentAnalysis().score_text('Welcome to our new house.')
```
**Output**:                                                                 
Mean Score (Arithmetic | Geometric | Harmonic) | Percentage (Positive | Negative | Neutral) | Raw Scores
![](examples/result_example1.png)

### 2.2.1.2 The class for converting shapefile to geojson
```Python
class Shape2Json(object):
    def __init__(self, fname, output1, output2, school_param, school_list,
                 addresses=None, coordinates=None):
        self.fname = fname
        self.output1 = output1
        self.output2 = output2
        self.school_param = school_param
        self.school_list = school_names
        self.addresses = addresses
        self.coordinates = coordinates
```
The class converts an ESRI shapefile into a geojson file and get the coordinates of each school. It is noted that, during the generation of the shapefiles, both 'SCHOOL' and 'SCHOOL_1' has been used for a field attribute. In general, the conversion of the shapefile are two-step process using two methods, convert_json and convert_epsg.

Parameter | Description
----|----
`fname` | an input of the shapefile's name
`output1` | json output after converting the shapefile
`output2` | json output after converting output1 from the spatial reference of Maryland to the spatial reference of world
`school_param` | 'SCHOOL_1' used in one of field attributes for elementary schools; 'SCHOOL' used for middle and high schools
`school_list` | a list of elementary schools, middle schools, or high schools
`addresses` | a list of school addresses
`coordinates` | a list of the cooridinates of the schools

```Python
    def convert_json(self):
```
It converts shapefile into geojson file. All files have been output as `output1`.

```Python
    def convert_epsg(self):
```
The function converts json file of output1 that was generated under spatial reference EPSG 2248 to the spatial reference of world EPSG 4326. The files contains not only 'Polygon' but also 'MultiPolygon' which requires additional step for conversion. In addition, this function attains the address of each school.

```Python
    def get_coordinates(self):
```
Its functionality is to acquire the GPS coordinates of every school in the study for visualization.

### 2.2.1.3 The class visualizing the results
```Python
class MapVisualization(object):
    def __init__(self, coordinates, score, option, location, polygon):
        self.coordinates = coordinates
        self.score = precentage
        self.option = option
        self.location = location
        self.polygon = polygon
```
Parameter | Description
----|----
`coordinates` | the GPS coordinates of the schools
`score` | the sentiment score that can be represented as  percentage of the positive, negative, and neural feedbacks from parents
`option` | proposed option A and option B for school redistricting
`location` | central location of the map
`polygon` | the coordinates of school districts by elementary, middle, and high

This class uses folium module to plot results in interactive maps. Each school is represented by popup icon with a pie chart indicating percentage of sentiments of parents' feedback.

```Python
    def get_json(self, data, school_name):
```
Parameter | Description
----|----
`data`| sentiment score data
`school_name`| the name of the school

It uses `vincint` module to acquire json data of the pie chart of the results for visualization.

```Python
    def folium_visual(self, col, file_name):
```
Parameter | Description
----|----
`col`| the color of your choice for popup icon
`file_name`| save the interactive map to a file in the results folder

---
## 3. Results and Conclusion
In general, six interactive maps have been produced based on three school categories and two options. The sentiments vary by different schools. For an example, parents in Urbana area show positive feedbacks for the latest proposal for redistricting middle and high schools, while they have relatively neural feedbacks for the elementary school district. In comparison with the feedbacks from Engagement Session on March, 2019, these results show a great improvement, suggesting that the Board of Education took Urbana parents' feedback seriously and may take extra effort to explore best options for the middle and high school redistricting. However, it remains unclear if parents found the common ground of the elementary school redistricting as the natural sentiments exist. Similarly, other neighborhoods show inconsistent support for or opposition against the latest options by school categories. Thus, it requires board members to review the school redistrict options case by case prior to the superintendent recommendation. By identifying the sentiment and preference of the parents in different neighborhoods, this project helps board members understand the impact of redistricting on each neighborhoods and provides references to them for making final recommendations. In addition, the parents in local communities can easily assess the emotions among their neighbors via the visualized results and recognize if their educational needs are align with the majority of their neighborhoods.

It should be noted that the algorithm of the sentiment analysis is optimized for this project and needs tweaks, such as incorporating with Natural Language Toolkit (`nltk`), to apply to other similar projects. Additionally, the json files for visualization may require some organization in order to plot complete polygons without any interference with each other. However, due to the limited time, the results of current project can still be used as good initial assessments for understanding the needs of parents after the Engagement Session on June, 2019. Future improvements need to address the issues mentioned above.

#### An Example:

**Input**:
```python
MapVisualization(coordinates,
                 score,
                 'A',
                 'Frederick, MD',
                 'ES.json').foliumVisual('blue', 'results/es_A.html')
```
**Output**                                              
**(Please forgive me for not having time to further clean the shapefile)**
![](/examples/result_example2.png)


---
If you have any questions, please contact me at meng.chen03(at)gmail.com.
