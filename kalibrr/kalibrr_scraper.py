from utils import parse_job_search_result, parse_job_page
import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

import time
import random
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
from google.cloud import storage
datetime_now = pd.Timestamp.now(tz='Asia/Manila').strftime("%Y-%m-%d %H").split()
date,hour = datetime_now

base_url = "https://www.kalibrr.com/job-board/1"
options = Options()

options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get(base_url)

data_columns = ['datetime_scraped', 'name','name_details','company','company_address',\
           'salary_low','salary_high','date_posted_str','date_application_deadline','link']

##get last page for job postings to know when to stop
soup = BeautifulSoup(requests.get("https://www.kalibrr.com/job-board/1").text, "lxml")
last_page = int(soup.select("ul.k-flex.k-justify-center.k-items-center.k-my-8")[0].find_all("li")[-2].text)

saved_pages = []
df_list = []
time.sleep(5)
for current_page in np.arange(1,2):
    if current_page not in saved_pages:
        print('Scraping page %d/%d...' %(current_page,last_page), end='')
        current_time = pd.Timestamp.now(tz='Asia/Manila').strftime("%Y-%m-%d %H:%M:%S")
        
        #parse page
        page_src = BeautifulSoup(driver.page_source.encode('utf-8').decode('ascii', 'ignore'), 'lxml')
        job_list = page_src.find_all('div', {"itemprop":"itemListElement"})
        data = [parse_job_search_result(j, current_time) for j in job_list]
        df = pd.DataFrame(data, columns = data_columns)

        next_page = current_page + 1
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,\
                                                                   '//a[@aria-label ="Page {0}" or text()="{0}"]'.format(next_page)))).click()

        time.sleep(random.randint(5,10))
        df_list.append(df)
        saved_pages.append(current_page)
        print('DONE!')

##put date in the filename
# file_name_jobs = f"data/kalibrr_jobs_asof_{date}.csv"

jobs_df = pd.concat(df_list).reset_index(drop=True).reset_index().rename(columns={'index': 'job_id'})
jobs_df['job_id']=jobs_df['job_id'].apply(lambda x: "%05d" % (int(x)+1))
jobs_df = jobs_df[['datetime_scraped','job_id']+data_columns[1:]]

# all_df.to_csv(file_name_jobs, index=False, encoding='utf-8')


# datetime_now = pd.Timestamp.now(tz='Asia/Manila').strftime("%Y-%m-%d %H:%M:%S")
# date = datetime_now.split()[0]

# options = Options()
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

# jobs_df = pd.read_csv(f'kalibrr_jobs_asof_{date}.csv')
jobs_df['job_id']=jobs_df['job_id'].apply(lambda x: "%05d" % (int(x)))
data_columns = ['job_id','datetime_scraped', 'name','level','category','educ_reqt','nvacancies','link']

saved_pages = []
data = []

job_links = jobs_df[jobs_df['company_address'].str.contains('Philippines')][['job_id','link']].values

for n,(this_job_id, this_job_link) in enumerate(job_links):
    if this_job_link not in saved_pages:
        print('Scraping page %d/%d...' %(n+1,len(job_links)), end='')
        current_time = pd.Timestamp.now(tz='Asia/Manila').strftime("%Y-%m-%d %H:%M:%S")
        row = parse_job_page(driver,this_job_link,current_time)
        data.append([this_job_id]+row)
        print('DONE!')
        saved_pages.append(this_job_link)
        time.sleep(random.randint(3,8))
        
details_df = pd.DataFrame(data, columns=data_columns)
# all_df.to_csv(f'data/kalibrr_job_details_asof_{date}.csv', index=False, encoding='utf-8')

jobs_df = jobs_df.drop(columns=["datetime_scraped","link","name"])
# d2 = pd.read_csv(f"kalibrr_jobs_asof_{date}.csv")

all_df = pd.merge(details_df,jobs_df,on="job_id")
all_df.to_csv(f"data/kalibbr_full_{date}.csv")

def upload_to_bucket(blob_name, file_path, bucket_name):
    '''
    Upload file to a bucket
    : blob_name  (str) - object name
    : file_path (str)
    : bucket_name (str)
    '''
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    return blob

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] =  r'autonomous-star-351110-686eeb65c12f.json'

storage_client = storage.Client()


file_path = f"data/kalibbr_full_{date}.csv"

upload_to_bucket(blob_name=f"kalibrr_{date}.csv",file_path=file_path,bucket_name="sample-de-hurly")

print(f"kalibbr_full_{date}.csv uploaded to bucket as kalibrr_{date}.csv")