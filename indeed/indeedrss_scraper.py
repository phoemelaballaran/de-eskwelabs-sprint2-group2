import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
from google.cloud import storage
import os

SCRAPE_TIME = datetime.now().strftime(r"%Y-%m-%d-%H-%M")
fname = f"ph_{SCRAPE_TIME}_indeedrss.csv"

jobList = []
companyList = []
pubDateList = []
geoList = []
JobDescriptions = []
linkList = []
locationList = []
guidList = []
fullJobDescription = []
r = requests.get(f'https://ph.indeed.com/rss/jobs?q=data%20analyst&sort=date')
soup = bs(r.content, features='xml')

jobs = soup.findAll('item')

for job in jobs:
    jobTitle = job.find('title').text
    companies = job.find('source').text
    pubDate = job.find('pubDate').text
    geoLoc = job.find('georss:point').text
    jd = job.find('description').text
    links = job.find('link').text
    guid = job.find('guid').text
    city = jobTitle.split('-')[-1].strip()

    jobList.append(jobTitle)
    companyList.append(companies)
    pubDateList.append(pubDate)
    geoList.append(geoLoc)
    JobDescriptions.append(jd)
    linkList.append(links)
    locationList.append(city)
    guidList.append(guid)


data = list(zip(guidList, jobList, companyList, pubDateList, geoList, locationList,
                JobDescriptions, linkList))

df = pd.DataFrame(data, columns=[
    "JobID", "JobTitle", "Company", "PublicationDate",
    "GeoRSS", "Location", "rssJobDescription", 
    "Link"
])

df = df.replace(r"\n", " ", regex=True)


#rename filepath according to VM
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcp_config.json'

client = storage.Client()

#rename bucket name according to GCS bucket
bucket = client.get_bucket('sample-de-rich/indeedrss_scraped')

bucket.blob(fname).upload_from_string(df.to_csv(), 'text/csv')

