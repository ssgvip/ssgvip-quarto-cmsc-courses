
# import pandas lib as pd

import pandas as pd

filename = "cmsc-bulletin-spring-2023.xlsx"

# read by default 1st sheet of an excel file

xlsx = pd.ExcelFile( filename )
dataframe1 = pd.read_excel(xlsx,"CMSC-Courses")


print(dataframe1)

