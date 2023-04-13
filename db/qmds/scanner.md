---
date: 4/12/23
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
```
:::

## a list of columns in the *CMSC-course-data* tab

::: {.cell execution_count="4"}
::: {.cell-output .cell-output-display}
Here is a list of columns:`<br/>`{=html}'Subject', 'Number', 'CourseId',
'idx', 'Title', 'Hours', 'foc', 'bscs', 'bscs-cyber', 'bscs-data',
'bscs-sftengr', 'Catalog', 'Catalog Description', 'Restrictions',
'Isolated Description'.
:::
:::

## CMSC Courses in the Bulletin

::: {.cell execution_count="5"}
::: {.cell-output .cell-output-display}
[Table 1](#tbl-table1) presents a list of CMSC courses in the bulletin.
There are 82 courses in the bulletin.
:::

::: {.cell-output .cell-output-display}
::: {#tbl-table1}
  CourseId   Title
  ---------- -------------------------------------------------------------
  CMSC 101   Introduction to Computer Science
  CMSC 144   Code Beats With Python
  CMSC 191   Topics in Computer Science
  CMSC 210   Computers and Programming
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

::: {.cell execution_count="6"}
``` {.python .cell-code}
def showTopics( courseId ):
  topics = topics_df[ topics_df["CourseId"].str.contains(courseId[5:]) & topics_df["CourseId"].str.contains(courseId[:4]) ]
#  slist = courseId[:4]+"/"+courseId[5:]+": "+", ".join( topics["ADJTopic"] )
  slist = ", ".join( topics["ADJTopic"].unique() )
  return slist


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

## Topics

{showTopics( row["CourseId"] )}

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

::: {.cell execution_count="7"}
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

::: {.cell execution_count="8"}
``` {.python .cell-code}
filename = "qmds/index.qmd"
with open(filename, 'w',encoding="utf-8") as file:
  file.write(f"""---
title: "CMSC Courses and Titles"
date: last-modified
---
""" )

  course_df['urlID'] = "[" + course_df["CourseId"].astype(str) + "](" + course_df["Subject"].astype(str) + course_df["Number"].astype(str) + '.html)'
  course_df['urlTitle'] = "[" + course_df["Title"].astype(str) + "](" + course_df["Subject"].astype(str) + course_df["Number"].astype(str) + '.html)'


  cols = ["urlID","urlTitle"]
  file.write(tabulate(
  course_df[ cols ],
  showindex=False,
  headers=["Course","Title"],
  tablefmt="fancy"
    )
  )
  file.close()
```
:::

# Autogenerating *catalog.qmd*

::: {.cell execution_count="9"}
``` {.python .cell-code}
def showTopics( courseId ):
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

**Topics:** { showTopics( row["CourseId"] ) }

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

::: {.cell execution_count="10"}
``` {.python .cell-code}
from textwrap import wrap

def expandURL( courseList ):
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


  df_grouped = topics_df.groupby('ADJTopic')['idx'].unique().apply( expandURL ).reset_index()
  
  file.write(
    tabulate(df_grouped, tablefmt='fancy', showindex=False, headers=["Adjusted Topic","Course"] )
  )

  file.close()
```
:::
