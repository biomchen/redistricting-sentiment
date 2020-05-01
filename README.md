#### About

# **Better or Worse?**
For detailed analyses, please see the notebook `redistricting_nb.ipynb`
## **Problem**
School redistricting in Linganore-Oakdale-Urbana (LOU) area has stirred outcry from the local communities in the social media. In order to understand the concerns about local communities, Frederick County Board of Education provided an online platform for community members to express their opinions and conducted a basic statistic analyses of local community concerns. However, their analyses lack of details about what sentiment of the local communities were and why the communities show favor/disfavor to the school redistricting plans.
\
![](./figs/fig1.png)\
**Fig. 1** Word clouds of the LOU feedbacks.

## **Insights**
* The LOU commmunities show more positive attitudes towards the second-round proposed school redistricting pl ans. Particularly, both Options A and B of high school districts have much less negative feedbacks than previous versions. Local communities that have childrens enrolled in Linganore HS prefer Option B instead of Option A; those in Oakdale HS like Option A more than Option B. Urbana HS parents seems OK for both options.
* For middle school districts, communities that have their children enrolled in New Market MS, Oakdale MS, Urbana MS largely prefer Option A. Windosor Knolls MS community shows neurtual attitde towards both options, despite its sentiment score of the Option B is slightly higher. Some parents of Thomas Johnson MS show great objection to the Option A, but relatively neutral attitude to the Option B.
* Among elementary school districts, the Option A of Deer Crossing ES, Centerville ES, and Spring Ridge ES were largely preferred by local communities, while the Option B gain positive feedbacks among parents of Spring Ridge ES, Green Valley, and Kempton ES. It seems that Spring Ridge ES community particularly favored the Option B.
* Using interactive sentiment analyses, local education administration could effectively identify where local community needs were and tailor its resources to address them, which would save time and money.
* My [web app](https://bit.ly/BetterOrWorseDemo) could serve as a platform for general public to understand their neighbors' feelings of the school redistricting studies (see **Fig 2** for example).

![](./figs/fig3.png)\
**Fig. 2** Example of the interactive map of sentiments among different school districts.

## **Data**
The community feedbacks for the second-round proposals of new school districts were assembled in single pdf file that contains numerous tables stretching over 200-page long. The tables store feedbacks for elementary, middle, and high school districts of LOU area in Frederick County, MD. Each school district have tables for options A and B as well as some comments related but not specific to any option. I designated those unspecific comments to option AB.

## **Approach**
In order scrape the data from the pdf file, I extract the comments and parse them into dataframe and stored them in a SQL database. To improve the efficiency of analyzing the data, I created `redistrict` module to scrape data, to perform exploratory data analyses and sentiment analyses, and to finally visualize the insights.

![](./figs/fig2.png)\
**Fig. 3** Example of the interactive plot of sentiment score distribution among elementary schools.

#### **Python Module** `redistrict`
In the module, I developed three classes `PdfTable`, `CommentSentiments`, and `VisualizeResults` to perform the majority of the required functionality.

* `PdfTable`: extracting the data from a pdf file and to parse information to store it into a SQL database;
* `CommentSentiments`: visualizing the Word Clouds of community feedbacks, calculating sentiment scores, performing exploratory analyses (see **Fig. 3** for example), and visualizing the results;
* `VisualizeResults`: parsing the results by different school districts and visualizing the results in a interactive map.

## **Tools and Techs**
* Python
    * Camelot
    * Worldcloud
    * Streamlit
    * Folium
    * GeoPandas
    * NLTK
    * Plotly
    * Vincent
    * Geopy
* OpenStreetMap(OSM)
* NLP
* Feature Engineering
* SQL
* AWS EC2, S3
