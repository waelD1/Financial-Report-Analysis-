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


#The report are differents. We regroup the reports that are the most similar
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
    string_to_find = "CONSOLIDATED STATEMENTS OF INCOME" + "\n" + "(in millions, except per share data)"
  url_2018_2021 = f'https://thewaltdisneycompany.com/app/uploads/{year+1}/01/{year}-Annual-Report.pdf'
  pdf = url_to_pdf(url_2018_2021)
  index_page = find_page(pdf, string_to_find)
  print(index_page)
  df = tabula.read_pdf(url_2018_2021, pages = index_page)
  df_concat = pd.concat(df)
  dict_of_df[year] = df_concat




# Put each dataframe extracted in the right format
#2020 to 2018
df_2020 = dict_of_df[2020].iloc[:, [0,1,4,6]].copy()
df_2020.rename(columns={'Revenues:' : 'index'}, inplace = True) #inplace=True

#Empty column with only header that gives precision. We will keep these headers
cost_2020 = df_2020['index'].loc[3]
earnings_diluted_2020 = df_2020['index'].loc[21] + ' ' + df_2020['index'].loc[22]
earnings_basic_2020 = df_2020['index'].loc[21] + ' ' +  df_2020['index'].loc[26]

#drop the useless row
df_2020.drop(index=[3, 21,22,26], inplace = True)

#Put the first row with as header
df_2020 = df_2020.T
new_header = df_2020.iloc[0] 
df_2020 = df_2020[1:] 
df_2020.columns = new_header 

#reset index
df_2020.reset_index(drop=True, inplace = True)

#rename index
df_2020.rename(index={0:2020, 1 : 2019, 2 : 2018}, inplace = True)
df_2020.drop(columns = ['Continuing operations $', 'Discontinued operations'], inplace = True)

# Change the name of the column
column_names = df_2020.columns.to_series()
column_names.iloc[20] = earnings_diluted_2020
column_names.iloc[21] = earnings_basic_2020
df_2020.columns = column_names

####################################
#2017 to 2015
df_2017 = dict_of_df[2017].iloc[:, [0,2,4,6]].copy()
df_2017.rename(columns={'Revenues:' : 'index'}, inplace = True)

cost_2017 = df_2017['index'].loc[3]
earnings_2017 = df_2017['index'].loc[18]
shares_2017 = df_2017['index'].loc[21] + ' ' +  df_2017['index'].loc[22]

df_2017.drop(index=[3, 18,21, 22], inplace = True)

df_2017 = df_2017.T
new_header = df_2017.iloc[0] 
df_2017 = df_2017[1:] 
df_2017.columns = new_header 

#reset index
df_2017.reset_index(drop=True, inplace = True)

#rename index
df_2017.rename(index={0:2017, 1 : 2016, 2 : 2015}, inplace = True)

#######################################

#2014 to 2012
df_2014 = dict_of_df[2014].iloc[:, [0,2,4,6]].copy()
df_2014.rename(columns={'Revenues:' : 'index'}, inplace = True) #inplace=True

cost_2014 = df_2014['index'].loc[3]
earnings_2014 = df_2014['index'].loc[18]
shares_2014 = df_2014['index'].loc[21] + ' ' +  df_2014['index'].loc[22]

df_2014.drop(index=[3, 18,21, 22], inplace = True)

df_2014 = df_2014.T
new_header = df_2014.iloc[0] 
df_2014 = df_2014[1:]
df_2014.columns = new_header 

#reset index
df_2014.reset_index(drop=True, inplace = True)

#rename index
df_2014.rename(index={0:2014, 1 : 2013, 2 : 2012}, inplace = True)