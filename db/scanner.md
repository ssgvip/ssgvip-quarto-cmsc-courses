---
date: 4/25/23
title: Building this web site
toc-title: Table of contents
---

[Quarto](https://quarto.org) is used to build this web site.

A list of CMSC courses was downloaded from the [campus
bulletin](http://bulletin.vcu.edu/azcourses/cmsc/). The list was stored
into a [google
sheet](https://docs.google.com/spreadsheets/d/1qrN3L7eRLsM-aVMHYaLQN-FMYtrTJf0_h6dLKlUdPkk/edit#gid=107368023)
and signficantly cleaned.

Two tabs are significant in the [google
sheet](https://docs.google.com/spreadsheets/d/1qrN3L7eRLsM-aVMHYaLQN-FMYtrTJf0_h6dLKlUdPkk/edit#gid=107368023):

1.  [CMSC-course-data](https://docs.google.com/spreadsheets/d/1qrN3L7eRLsM-aVMHYaLQN-FMYtrTJf0_h6dLKlUdPkk/edit#gid=107368023):
    This tab contains one record per course found in the [VCU
    Bulletin/online catalog](http://bulletin.vcu.edu/azcourses/cmsc/).
    These are CMSC classes *on the books* and not necessarily taught
    regularly, or even taught at all.

2.  [CMSC-course-topics](https://docs.google.com/spreadsheets/d/1qrN3L7eRLsM-aVMHYaLQN-FMYtrTJf0_h6dLKlUdPkk/edit#gid=338318647):
    This tab contains one record per topic per course. The first column
    is the CourseID and then there are one or more topics on successive
    rows. Topics were pulled from several different sources:

    -   From the course catalog description itself,
    -   From the instructors course description in their Spring 2023
        syllabus, and
    -   from the course topic outline found in their Spring 2023 course
        syllabus.

Not every instructor included a custom course description or topical
outline in their Spring 2023 syllabus. In general the topics are all
treated as comparable, but they are distinquishable using the *Source*
column in the topics tab, so we can analysis their differences.

The code in the sections below below generates this website using the
course data in the google sheet. The construction of the web site is a
2-step process:

1.  Build a quarto website template using data stored in the database.
    This includes building:

    a.  individual course pages,
    b.  the *index* page that serves as the index/home page of the site,
    c.  a *listing* page that presents summaries of all courses and
        topics,
    d.  a *topics* page that lists all the unique topics and connects
        them to individual courses,
    e.  and this *code* page, which represents the script that builds
        the site,

2.  Rendering the files created above into the website using quarto.

This website is posted using [github
pages](https://quarto.org/docs/publishing/github-pages.html). The site
is rendered to the */docs* folder within the [github
repo](https://github.com/ssgvip/ssgvip-quarto-cmsc-courses). GITHUB
create a corresponding web site on github.io.

The code sections below demonstrate how quarto can leverage google
sheets to generate and publish a static website.

# Connecting to google sheets

::: {#setting-credentials .cell execution_count="1"}
``` {.python .cell-code}
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
from IPython.display import Markdown
from tabulate import tabulate

# define scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# create credentials object
credential_file = os.path.join(os.path.expanduser("~"), ".gsecrets", "gsheets-credentials.json")
if not os.path.isfile( credential_file ):
  print("Missing credential file:",credential_file)
  sys.exit()
```
:::

# Connection details

::: {.cell execution_count="2"}
::: {.cell-output .cell-output-display}
The *secrets-file* is a service account JSON file created on the google
console. By convention (for this program) we're storing the credentials
off the github repo in the *.gsecrets* folder under the user home
directory.

The *CLIENT_EMAIL* is set inside the secrets file. If the user
encounters "PERMISSION DENIED" or other access errors, this email
address should be added as a "share" to the file on the regular google
sheets interface.

-   secrets-file:
    *C:`\Users`{=tex}`\jdleonard`{=tex}.gsecrets`\gsheets`{=tex}-credentials.json*
-   client_email:
    *jdleonard-egr-jl-rak1-srv@jdleonard.iam.gserviceaccount.com*
:::
:::

# Loading the course and topics data

::: {#loading-google-sheet .cell execution_count="3"}
``` {.python .cell-code}
# authorize the client
creds = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scope)
client = gspread.authorize(creds)

# Course data: open the google sheet and tab
spreadsheet_key = "1qrN3L7eRLsM-aVMHYaLQN-FMYtrTJf0_h6dLKlUdPkk"
worksheet_name = "CMSC-course-data"
sheet = client.open_by_key(spreadsheet_key).worksheet(worksheet_name)

# Course data: Read the data into a Pandas DataFrame
data = sheet.get_all_values()
headers = data.pop(0)
course_df = pd.DataFrame(data, columns=headers)

# Course data: do a little data cleaning, converting strings into integers
for col in ["Number","Hours"]:
  course_df[col] = course_df[col].astype("int")

# Topics data: Read the data into a Pandas DataFrame
sheet2 = client.open_by_key(spreadsheet_key).worksheet("CMSC-course-topics")
data = sheet2.get_all_values()
headers = data.pop(0)
topics_df = pd.DataFrame(data, columns=headers)

# Topics data: do a little data cleaning, converting strings into integers
for col in ["Count","Number","Level"]:
  topics_df[col] = topics_df[col].astype("int")

topics_df["CourseId"] = topics_df["CourseId"].apply( str.strip )


# Coverage data: restack ABET 1, 2 and 3 categories
g1 = topics_df[ ["abet_tag1","ADJTopic","idx","CourseId"] ]
g2 = topics_df[ ["abet_tag2","ADJTopic","idx","CourseId"] ].rename(columns={"abet_tag2":"abet_tag1"})
g3 = topics_df[ ["abet_tag3","ADJTopic","idx","CourseId"] ].rename(columns={"abet_tag3":"abet_tag1"})
g =  pd.concat( [g1,g2,g3],axis=0)
coverage_df = g[ g["abet_tag1"] != ""]
```
:::

# Loading past syllabii

::: {.cell execution_count="4"}
``` {.python .cell-code}
directories = ['../docs']

# Create an empty pandas DataFrame
syllabii_df = pd.DataFrame(columns=['filename', 'url', 'idx', 'termId','termName','urlByTermName','urlByCourseId'])

# Loop through all the directories
for directory in directories:
    # Loop through all the files in the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is a PDF file
            if file.endswith('.pdf') and file.startswith('CMSC_'):
                # Append the filename to the pandas DataFrame
                filename = file.strip()
                url = "./"+root[8:]+"/"+file
                idx = file[0:4] + file[5:8]
                termId = root[8:]
                termName = " ".join(filename.split('_')[-2:])[:-4]
                urlByTermName = "<a href='"+url+"'>"+termName+"</a>"
                urlByCourseId = "<a href='"+url+"'>"+idx+"</a>"
                syllabii_df.loc[len(syllabii_df)] = [filename,url,idx,termId,termName,urlByTermName,urlByCourseId]


def showSyllabiiByTerm( courseId ):
  off = syllabii_df[ syllabii_df["idx"]==courseId ];
  slist = ", ".join( off["urlByTermName"])
  if slist=="":
    slist = "(none since Spring 2021)"
  return slist
```
:::

## a list of columns in the *CMSC-course-data* tab

::: {.cell execution_count="5"}
::: {.cell-output .cell-output-display}
Here is a list of columns:`<br/>`{=html}'Subject', 'Number', 'CourseId',
'idx', 'Title', 'Hours', 'foc', 'bscs', 'bscs-cyber', 'bscs-data',
'bscs-sftengr', 'postbac', 'Catalog', 'Catalog Description',
'Restrictions', 'Isolated Description'.
:::
:::

## CMSC Courses in the Bulletin

::: {.cell execution_count="6"}
::: {.cell-output .cell-output-display}
[Table 1](#tbl-table1) presents a list of CMSC courses in the bulletin.
There are 83 courses in the bulletin.
:::

::: {.cell-output .cell-output-display}
::: {#tbl-table1}
  CourseId   Title
  ---------- -------------------------------------------------------------
  CMSC 101   Introduction to Computer Science
  CMSC 144   Code Beats With Python
  CMSC 191   Topics in Computer Science
  CMSC 210   Computers and Programming
  CMSC 235   Computing and Data Ethics
  CMSC 245   Introduction to Programming Using C++
  CMSC 246   Advanced Programming Using C++
  CMSC 254   Introduction to Problem-solving
  CMSC 255   Introduction to Programming
  CMSC 256   Data Structures and Object Oriented Programming
  CMSC 257   Computer Systems
  CMSC 302   Introduction to Discrete Structures
  CMSC 303   Introduction to the Theory of Computation
  CMSC 311   Computer Organization
  CMSC 312   Introduction to Operating Systems
  CMSC 320   Software Engineering and Web Development
  CMSC 330   Data Science Skills
  CMSC 340   Cybersecurity Skills
  CMSC 355   Fundamentals of Software Engineering
  CMSC 391   Topics in Computer Science
  CMSC 401   Algorithm Analysis with Advanced Data Structures
  CMSC 403   Programming Languages
  CMSC 404   Compiler Construction
  CMSC 409   Artificial Intelligence
  CMSC 410   Introduction to Quantum Computing
  CMSC 411   Computer Graphics
  CMSC 412   Social Network Analysis and Cybersecurity Risks
  CMSC 413   Introduction to Cybersecurity
  CMSC 414   Computer and Network Security
  CMSC 415   Introduction to Cryptography
  CMSC 416   Introduction to Natural Language Processing
  CMSC 420   Software Project Management
  CMSC 425   Introduction to Software Analysis and Testing
  CMSC 428   Mobile Programming: iOS
  CMSC 435   Introduction to Data Science
  CMSC 440   Data Communication and Networking
  CMSC 441   Senior Design Studio I (Laboratory/Project Time)
  CMSC 442   Senior Design Studio II (Laboratory/Project Time)
  CMSC 451   Senior Project I
  CMSC 452   Senior Project II
  CMSC 455   Software as a Service
  CMSC 475   Design and Implementation of User Interfaces
  CMSC 491   Topics in Computer Science
  CMSC 492   Independent Study
  CMSC 501   Advanced Algorithms
  CMSC 502   Parallel Algorithms
  CMSC 506   Computer Networks and Communications
  CMSC 508   Database Theory
  CMSC 510   Regularization Methods for Machine Learning
  CMSC 512   Advanced Social Network Analysis and Security
  CMSC 516   Advanced Natural Language Processing
  CMSC 525   Introduction to Software Analysis, Testing and Verification
  CMSC 526   Theory of Programming Languages
  CMSC 531   3D Computer Vision for Robot Navigation
  CMSC 591   Topics in Computer Science
  CMSC 601   Convex Optimization
  CMSC 602   Operating Systems
  CMSC 603   High Performance Distributed Systems
  CMSC 605   Advanced Computer Architecture
  CMSC 608   Advanced Database
  CMSC 610   Algorithmic Foundations of Bioinformatics
  CMSC 611   Computer Multimedia
  CMSC 612   Game Theory and Security
  CMSC 615   Cryptocurrency and Blockchain Techniques
  CMSC 618   Database and Application Security
  CMSC 619   The Design and Specifications of User Interfaces
  CMSC 620   Applied Cryptography
  CMSC 621   Theory of Computation
  CMSC 622   Network and System Security
  CMSC 623   Cloud Computing
  CMSC 624   Software Quality Assurance
  CMSC 625   Advanced Software Analysis, Testing and Verification
  CMSC 628   Mobile Networks: Applications, Modeling and Analysis
  CMSC 630   Image Analysis
  CMSC 635   Knowledge Discovery and Data Mining
  CMSC 636   Artificial Neural Networks and Deep Learning
  CMSC 654   Memory and Malware Forensics
  CMSC 678   Statistical Learning and Fuzzy Logic Algorithms
  CMSC 691   Special Topics in Computer Science
  CMSC 692   Independent Study
  CMSC 697   Directed Research
  CMSC 701   Research Methods
  CMSC 702   Computer Science Seminar

  : Table 1: List of courses
:::
:::
:::

# Generating individual course QMD files

Now for the tricky AND fun part. Using the data from the dataframe,
let's create a bunch of QMDs one for each course.

::: {.cell execution_count="7"}
``` {.python .cell-code}
def expandURL( courseList ):
  """ expand list of courses into a string of URL pointing to course pages """
  urls = course_df[ course_df["idx"].isin( courseList) ].reset_index()
  urls["url"] = "<a href='"+urls["idx"]+".qmd"+"'>"+urls["CourseId"]+"</a>"
  returnValue = "";
  for i,url in urls["url"].items():
    if i==0:
      returnValue = url
#    elif i % 4 == 0:
#        returnValue = returnValue + ", <br/>\n" + url
    else:
      returnValue = returnValue + ", " + url
  return returnValue

def showTopics( courseId ):
  """ expand topic list to a single string """
  topics = topics_df[ topics_df["CourseId"].str.contains(courseId[5:]) & topics_df["CourseId"].str.contains(courseId[:4]) ]
#  slist = courseId[:4]+"/"+courseId[5:]+": "+", ".join( topics["ADJTopic"] )
  slist = ", ".join( topics["ADJTopic"].unique() )
  return slist

def showCoverage( courseId ):
  """ expand coverage list to a single string """
  topics = coverage_df[ coverage_df["CourseId"].str.contains(courseId[5:]) & coverage_df["CourseId"].str.contains(courseId[:4]) ]
#  slist = courseId[:4]+"/"+courseId[5:]+": "+", ".join( topics["ADJTopic"] )
  slist = ", ".join( topics["abet_tag1"].unique() )
  return slist

def showMap( courseId ):
  """ map topics and coverages for specific course """
  topics = coverage_df[ coverage_df["CourseId"].str.contains(courseId[5:]) & coverage_df["CourseId"].str.contains(courseId[:4]) ]
#  df_grouped = topics.groupby(['ADJTopic','abet_tag1'])['idx'].unique().apply( expandURL ).reset_index()
  df_grouped = topics.groupby(['abet_tag1','ADJTopic'])['idx'].unique().apply( expandURL ).reset_index()
  tab = tabulate(df_grouped, tablefmt='fancy', showindex=False, headers=["ABET coverage","Adjusted Topic","Course"] )
  d = Markdown(tab).data
  return d


block = "";
for index, row in course_df.iterrows():
  filename = f'./qmds/{row["Subject"]}{row["Number"]}.qmd'
  with open(filename, 'w',encoding="utf-8") as file:
    file.write(f"""---
title: "{row["CourseId"]} - {row["Title"]}"
date: last-modified
format:
  html:
    toc: true
---

## Catalog Description

{row["Catalog Description"]}


## Restrictions including pre- or co-requisities
 
{row["Restrictions"]}

## Description

{row["Isolated Description"]}

## Past Syllabii

{showSyllabiiByTerm( row["idx"] )}

## Topics

{showTopics( row["CourseId"] )}

## ABET Coverage

{showCoverage( row["CourseId"] )}

## Coverage and Topics Map

Note that topics without associated ABET category assignments are excluded from this map.  See the [mapping](https://docs.google.com/spreadsheets/d/1qrN3L7eRLsM-aVMHYaLQN-FMYtrTJf0_h6dLKlUdPkk/edit#gid=338318647) for more details.

{showMap( row["CourseId"] )}


## Syllabus Statements

Students should visit the URL below and review all syllabus statement information. The full university syllabus statement includes information on safety, registration, the VCU Honor Code, student conduct, withdrawal and more.

*<https://provost.vcu.edu/faculty/faculty-resources/syllabus/#statements>*


"""
    )
    file.close()

  block = block + f"""

{filename}


"""
```
:::

# Autogenerating left menu bar in *contents.yml*

::: {.cell execution_count="8"}
``` {.python .cell-code}
from math import floor

def floor_to_nearest_100(number):
    return floor(number / 100) * 100

filename = "qmds/_contents.yml"
with open(filename, 'w',encoding="utf-8") as file:
  file.write("""website:
  sidebar:
    contents:
"""
  )

  oldBlockId = 0
  for index, row in course_df.iterrows():
    if (oldBlockId != floor_to_nearest_100(row["Number"])):
      oldBlockId = floor_to_nearest_100(row["Number"])
      file.write(f"""
    - section: "{oldBlockId} level"
      contents:
"""
)
    file.write(f'        - href: {row["Subject"]}{row["Number"]}.qmd\n')
    file.write(f'          text: {row["Subject"]} {row["Number"]}\n')

  file.write("\n")
  file.close()
```
:::

# Autogenerating *index.qmd*

::: {.cell execution_count="9"}
``` {.python .cell-code}
def showRowSyllabiiByTerm( row ):
  off = syllabii_df[ syllabii_df["idx"]==row["idx"] ];
  slist = ", ".join( off["urlByTermName"])
  if slist=="":
    slist = "(none since Spring 2021)"
  return slist

filename = "qmds/index.qmd"
with open(filename, 'w',encoding="utf-8") as file:
  file.write(f"""---
title: "CMSC Courses and Titles"
date: last-modified
---
""" )

  course_df['urlID'] = "[" + course_df["CourseId"].astype(str) + "](" + course_df["Subject"].astype(str) + course_df["Number"].astype(str) + '.qmd)'
  course_df['urlTitle'] = "[" + course_df["Title"].astype(str) + "](" + course_df["Subject"].astype(str) + course_df["Number"].astype(str) + '.qmd)'

  course_df = course_df.assign(Offerings=course_df.apply( showRowSyllabiiByTerm,axis=1 ))

  cols = ["urlID","urlTitle"]
  file.write(tabulate(
  course_df[ cols ],
  showindex=False,
  headers=["Course","Title","Syllabii"],
  tablefmt="fancy"
    )
  )
  file.close()
```
:::

# Autogenerating *catalog.qmd*

::: {.cell execution_count="10"}
``` {.python .cell-code}
def xxxshowTopics( courseId ):
  topics = topics_df[ topics_df["CourseId"].str.contains(courseId[5:]) & topics_df["CourseId"].str.contains(courseId[:4]) ]
#  slist = courseId[:4]+"/"+courseId[5:]+": "+", ".join( topics["ADJTopic"] )
  slist = ", ".join( topics["ADJTopic"] )
  return slist


course_df['urlHeader'] = "[" + course_df["CourseId"].astype(str) + " - " +  course_df["Title"].astype(str) + "](" + course_df["Subject"].astype(str) + course_df["Number"].astype(str) + '.qmd)'

block = "";
for index, row in course_df.iterrows():
  h = "hours" if(row["Hours"]>1) else "hour"
  block = block + f"""
## {row["urlHeader"]}

Semester course. {row["Hours"]} {h}.

**Restrictions:** {row["Restrictions"]}

**Description:** {row["Isolated Description"]}

**Syllabii:** { showSyllabiiByTerm( row["idx"])}

**Topics:** { showTopics( row["CourseId"] ) }

**ABET coverage:** { showCoverage( row["CourseId"] ) }

"""

filename = "qmds/catalog.qmd"
with open(filename, 'w',encoding="utf-8") as file:
  file.write(f"""---
title: "Catalog of CMSC Courses and Titles"
date: last-modified
format:
  html:
    toc: False
---
The following a complete catalog of CMSC courses listed in the VCU 2022-2023 Catalog. Not all courses
are offered on a regular basis.

""" )

  file.write(block)
  file.close()
```
:::

# Autogenerating *topics.qmd*

::: {.cell execution_count="11"}
``` {.python .cell-code}
from textwrap import wrap

def xxxexpandURL( courseList ):
  urls = course_df[ course_df["idx"].isin( courseList) ].reset_index()
  urls["url"] = "<a href='"+urls["idx"]+".qmd"+"'>"+urls["CourseId"]+"</a>"
  returnValue = "";
  for i,url in urls["url"].items():
    if i==0:
      returnValue = url
#    elif i % 4 == 0:
#        returnValue = returnValue + ", <br/>\n" + url
    else:
      returnValue = returnValue + ", " + url
  return returnValue
 

filename = "qmds/topics.qmd"
with open(filename, 'w',encoding="utf-8") as file:
  file.write(f"""---
title: "CMSC topics and courses"
date: last-modified
---
""" )

#  course_df['urlID'] = "[" + course_df["CourseId"].astype(str) + "](" + course_df["Subject"].astype(str) + course_df["Number"].astype(str) + '.html)'
#  course_df['urlTitle'] = "[" + course_df["Title"].astype(str) + "](" + course_df["Subject"].astype(str) + course_df["Number"].astype(str) + '.html)'


  df_grouped = topics_df.groupby(['ADJTopic','abet_tag1'])['idx'].unique().apply( expandURL ).reset_index()
  
  file.write(
    tabulate(df_grouped, tablefmt='fancy', showindex=False, headers=["Adjusted Topic","ABET Coverage","Course"] )
  )

  file.close()
```
:::

# Autogenerating *coverage.qmd*

::: {.cell execution_count="12"}
``` {.python .cell-code}
from textwrap import wrap


filename = "qmds/coverage.qmd"
with open(filename, 'w',encoding="utf-8") as file:
  file.write(f"""---
title: "CMSC courses and ABET topic coverage"
date: last-modified
---
The mappings listed below represent ABET coverage for undergraduate courses only.

""" )

#  course_df['urlID'] = "[" + course_df["CourseId"].astype(str) + "](" + course_df["Subject"].astype(str) + course_df["Number"].astype(str) + '.html)'
#  course_df['urlTitle'] = "[" + course_df["Title"].astype(str) + "](" + course_df["Subject"].astype(str) + course_df["Number"].astype(str) + '.html)'

  df_grouped = coverage_df[ coverage_df["idx"]<"CMSC600" ].groupby('abet_tag1')['idx'].unique().apply( expandURL ).reset_index()

  file.write(
    tabulate(df_grouped, tablefmt='fancy', showindex=False, headers=["ABET coverage topic","Course"] )
  )

  file.close()
```
:::

# Autogenerating *syllabii.qmd*

::: {.cell execution_count="13"}
``` {.python .cell-code}
from textwrap import wrap


filename = "qmds/syllabii.qmd"
with open(filename, 'w',encoding="utf-8") as file:
  file.write(f"""---
title: "Past syllabii"
date: last-modified
---
The following table maps our course catalog against a list of existing course syllabii. Note that some
courses have not been taught for a while! In other cases, some of the courses are freshly
added to the catalog and have not yet been taught.

""" )

#  course_df['urlID'] = "[" + course_df["CourseId"].astype(str) + "](" + course_df["Subject"].astype(str) + course_df["Number"].astype(str) + '.html)'
#  course_df['urlTitle'] = "[" + course_df["Title"].astype(str) + "](" + course_df["Subject"].astype(str) + course_df["Number"].astype(str) + '.html)'

  df = syllabii_df.pivot(index="idx",columns="termId",values="urlByTermName").reset_index()
  df = pd.merge(course_df[ ["idx"] ],df,how="left",on="idx")

  for columnName in df:
    df[columnName] = df[columnName].replace(np.nan,"&nbsp;")

  df["idx"] = "<a href='"+df["idx"]+".qmd'>"+df["idx"]+"</a>"

  file.write("\n")
  file.write(
    tabulate(df, tablefmt='fancy', showindex=False, headers=df.columns)
  )

  file.close()
```
:::
