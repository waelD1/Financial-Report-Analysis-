#pip install pdfminer.six
#pip install tabula-py
# Import Packages
import pandas as pd
import tabula
from io import StringIO
import urllib.request
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import io
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


#Convert url to readable object for pdfminer.six
def url_to_pdf(url):
    '''
    retrives pdf from url as bytes object
    '''
    open = urllib.request.urlopen(url).read()
    return io.BytesIO(open)

#Function that find the page where the report is
def find_page(url, string_to_find):
  page_report = 0
  output_string = StringIO()
  parser = PDFParser(url)
  doc = PDFDocument(parser)
  rsrcmgr = PDFResourceManager()
  device = TextConverter(rsrcmgr, output_string,  laparams=LAParams())
  interpreter = PDFPageInterpreter(rsrcmgr, device)

  for i, page in enumerate(PDFPage.create_pages(doc)):
          interpreter.process_page(page)
          text = ''
          text += output_string.getvalue()
          if string_to_find in text:
            page_report = i + 1
            break
  return page_report

#The reports are different. We regroup the reports that are the most similar
years_2010_2014 = [*range(2010,2015,1)]

years_2015_2017 = [*range(2015,2018,1)]

years_2018_2020 = [*range(2018,2021,1)]
print(years_2018_2020)


# String that allowed us to find the page where the balance sheet is
string_to_find = "CONSOLIDATED STATEMENTS OF INCOME" + "\n" + "(in millions, except per share data)"
dict_of_df = {}

# Iterate through url's to get balance sheet of each year with tabula
for year in years_2010_2014:
  url_2010_2014 = f'https://thewaltdisneycompany.com/app/uploads/2015/10/{year}-Annual-Report.pdf'
  pdf = url_to_pdf(url_2010_2014)
  index_page = find_page(pdf, string_to_find)
  print(index_page)
  df = tabula.read_pdf(url_2010_2014, pages = index_page)
  df_concat = pd.concat(df)
  dict_of_df[year] = df_concat

for year in years_2015_2017:
  url_2015_2017 = f'https://thewaltdisneycompany.com/app/uploads/{year}-Annual-Report.pdf'
  pdf = url_to_pdf(url_2015_2017)
  index_page = find_page(pdf, string_to_find)
  print(index_page)
  df = tabula.read_pdf(url_2015_2017, pages = index_page)
  df_concat = pd.concat(df)
  dict_of_df[year] = df_concat

for year in years_2018_2020:
  if year == 2020:
    string_to_find = "CONSOLIDATED STATEMENTS OF OPERATIONS" + "\n" + "(in millions, except per share data)"
  else:
      #The string changes for year 2020
    string_to_find = "CONSOLIDATED STATEMENTS OF INCOME" + "\n" + "(in millions, except per share data)"
  url_2018_2021 = f'https://thewaltdisneycompany.com/app/uploads/{year+1}/01/{year}-Annual-Report.pdf'
  pdf = url_to_pdf(url_2018_2021)
  index_page = find_page(pdf, string_to_find)
  print(index_page)
  df = tabula.read_pdf(url_2018_2021, pages = index_page)
  df_concat = pd.concat(df)
  dict_of_df[year] = df_concat



########################################## Data processing : changing data to put the tables in the same format
#We will only use the 2020, 2017, and 2014 reports since they each contain results from the previous three years.


#Get the dataframe for years 2018 to 2020 and rename index 
df_2020 = dict_of_df[2020].iloc[:, [0,1,4,6]].copy()
df_2020.rename(columns={'Revenues:' : 'index'}, inplace = True) 

# Due to a defect in the import of the tables, some titles have been separated on several empty columns.
# We will therefore save the names of the useless columns and add them to the columns with the missing names.
cost_2020 = df_2020['index'].loc[3]
earnings_diluted_2020 = df_2020['index'].loc[21] + ' ' + df_2020['index'].loc[22]
earnings_basic_2020 = df_2020['index'].loc[21] + ' ' +  df_2020['index'].loc[26]

# Drop the useless columns and put the first row with the titles as header
df_2020.drop(index=[3, 21,22,26], inplace = True)
df_2020 = df_2020.T
new_header = df_2020.iloc[0] 
df_2020 = df_2020[1:] 
df_2020.columns = new_header 

#reset index
df_2020.reset_index(drop=True, inplace = True)

#rename index
df_2020.rename(index={0:2020, 1 : 2019, 2 : 2018}, inplace = True)
df_2020.drop(columns = ['Continuing operations $', 'Discontinued operations'], inplace = True)

# rename columns with same name
column_names = df_2020.columns.to_series()
column_names.iloc[20] = earnings_diluted_2020
column_names.iloc[21] = earnings_basic_2020
df_2020.columns = column_names

# Rename column names to have the same for all the dataframes
df_2020.rename(columns = {'Services $' : 'Services',
'Equity in the income (loss) of investees' : 'Equity in the income of investees',
'Income (loss) from continuing operations before income taxes' : 'Income before income taxes',
'Income taxes on continuing operations' : 'Income taxes',
'Net income (loss)' : 'Net income',
'Net income from continuing operations attributable to noncontrolling and redeemable (390)noncontrolling interests' :  'Less: Net income attributable to noncontrolling interests',
'Net income (loss) attributable to The Walt Disney Company (Disney) $' : 'Net income attributable to The Walt Disney Company (Disney)',
'Earnings (loss) per share attributable to Disney(1): Diluted' : 'Earnings per share attributable to Disney: Diluted',
'Earnings (loss) per share attributable to Disney(1): Basic' : 'Earnings per share attributable to Disney: Basic'}, inplace = True)

#columns to drop
df_2020.drop(columns = ['Net income (loss) from continuing operations',
                        'Income (loss) from discontinued operations, net of income tax benefit (expense) of $10, (32)($39) and $0, respectively',
                        'Net income from discontinued operations attributable to noncontrolling interests'
                        ], inplace = True)

#adding the column that the scrapper failed to retrieve
df_2020['Weighted average number of common and common equivalent shares outstanding: Diluted'] = ['1,808', '1,666','1,507']
df_2020['Weighted average number of common and common equivalent shares outstanding: Basic'] = ['1,808', '1,656','1,499']

#adding a missing value that is in the PDF but not in the scrapped table
df_2020['Less: Net income attributable to noncontrolling interests'].replace({np.nan : '390'}, inplace = True)


####################################### Same process for the years 2015-2017
#2017 to 2015
df_2017 = dict_of_df[2017].iloc[:, [0,2,4,6]].copy()
df_2017.rename(columns={'Revenues:' : 'index'}, inplace = True) #inplace=True

cost_2017 = df_2017['index'].loc[3]
earnings_2017 = df_2017['index'].loc[18]
shares_2017 = df_2017['index'].loc[21] + ' ' +  df_2017['index'].loc[22]

df_2017.drop(index=[3, 18,21, 22], inplace = True)

#set the header row as the dataframe headers
df_2017 = df_2017.T
new_header = df_2017.iloc[0] 
df_2017 = df_2017[1:] 
df_2017.columns = new_header 

#reset index
df_2017.reset_index(drop=True, inplace = True)

#rename index
df_2017.rename(index={0:2017, 1 : 2016, 2 : 2015}, inplace = True)

#rename columns to have same name as all the other dataframes
column_names = df_2017.columns.to_series()
column_names.iloc[17] = earnings_2017 + ' ' + column_names.iloc[17]
column_names.iloc[18] = earnings_2017 + ' ' + column_names.iloc[18] 

column_names.iloc[19] = shares_2017 + ' ' + column_names.iloc[19]
column_names.iloc[20] = shares_2017 + ' ' + column_names.iloc[20] 

df_2017.columns = column_names

####################################### Same process for the years 2012-2014

#2014 to 2012
df_2014 = dict_of_df[2014].iloc[:, [0,2,4,6]].copy()
df_2014.rename(columns={'Revenues:' : 'index'}, inplace = True) #inplace=True

cost_2014 = df_2014['index'].loc[3]
earnings_2014 = df_2014['index'].loc[18]
shares_2014 = df_2014['index'].loc[21] + ' ' +  df_2014['index'].loc[22]

df_2014.drop(index=[3, 18,21, 22], inplace = True)

#set the header row as the table headers
df_2014 = df_2014.T
new_header = df_2014.iloc[0] 
df_2014 = df_2014[1:] 
df_2014.columns = new_header 

#reset index
df_2014.reset_index(drop=True, inplace = True)

#rename index
df_2014.rename(index={0:2014, 1 : 2013, 2 : 2012}, inplace = True)

#rename columns to have the same as the others dataframe
df_2014.rename(columns = {"Other income/(expense), net" : "Other income, net", "Interest income/(expense), net" : "Interest expense, net"}, inplace = True)

# Adding missing parts of columns titles
column_names = df_2014.columns.to_series()
column_names.iloc[17] = earnings_2014 + ' ' + column_names.iloc[17]
column_names.iloc[18] = earnings_2014 + ' ' + column_names.iloc[18] 

column_names.iloc[19] = shares_2014 + ' ' + column_names.iloc[19]
column_names.iloc[20] = shares_2014 + ' ' + column_names.iloc[20] 

df_2014.columns = column_names




################################################################## Concatenate all the results

#concatenate all the results
report = pd.concat([df_2020, df_2017, df_2014])

#delete brackets around numbers
for col in report.columns:
  if report[col].dtype == 'object':
    report[col] = report[col].str.strip('()')

#replace missing value
report['Other income, net'].replace({'—' : np.nan}, inplace = True)

#convert str to float
col_to_convert = [
  'Earnings per share attributable to Disney: Diluted',
  'Earnings per share attributable to Disney: Basic',
  'Dividends declared per share'
  ]

for col in report.columns:
  if col in col_to_convert:
    report[col] = report[col].astype(float)

# replace NaN value to 0, then change the format and replace those 0 values with the interpolation from pandas 
report['Other income, net'].replace(np.nan, '0', inplace = True)

# deleting the '-' in the table
for col in report.columns:
  if report[col].dtype != float:
    report[col] = report[col].str.replace(',', '').astype(int)


#replace missing values with interpolate from pandas
report.loc[[2016, 2015], 'Other income, net'] = np.nan
report['Other income, net'].interpolate(method='linear', inplace = True)
# then change  the type to int
report['Other income, net'] = report['Other income, net'].astype(int)


################################################################## Creating charts

# Revenues over time
fig = go.Figure()
fig.add_trace(go.Scatter(x=report.index, y=report['Total revenues'],
                    mode='lines',
                    name='Total Revenues (Products + Services)'))
fig.add_trace(go.Scatter(x=report.index, y=report['Services'],
                    mode='lines+markers',
                    name='Revenues : Services'))
fig.add_trace(go.Scatter(x=report.index, y=report['Products'],
                    mode='lines+markers', name='Revenues : Products'))

fig.show()

# Total costs for year 2020
list_cols = ['Cost of services (exclusive of depreciation and amortization)',
'Cost of products (exclusive of depreciation and amortization)',
'Selling, general, administrative and other',	
'Depreciation and amortization']

fig = px.pie(report.loc[2020], 
              values=report.loc[2020][list_cols].values, 
              names=list_cols,
              color_discrete_sequence=px.colors.sequential.RdBu)
fig.show()


# Net income of Walt Disney Company over time
import plotly.express as px
fig = px.bar(report, x=report.index, y='Net income attributable to The Walt Disney Company (Disney)',
             hover_data=['Net income attributable to The Walt Disney Company (Disney)'], color='Net income attributable to The Walt Disney Company (Disney)',
             labels = {'Net income attributable to The Walt Disney Company (Disney)' : 'Net income (in millions)'}
             )
fig.show()



# Share price over time
fig = go.Figure()
fig.add_trace(go.Scatter(x=report.index, y=report['Earnings per share attributable to Disney: Diluted'],
                   line =  dict(color='firebrick', width=4, dash='dot'),
                   name = 'Earnings per share attributable to Disney: Diluted'))
# Edit the layout
fig.update_layout(title='Earnings per share of Disney over time (in $)',
                   xaxis_title='Years',
                   yaxis_title='shares price in dollars')
fig.show()