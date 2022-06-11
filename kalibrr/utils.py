import numpy as np
import pandas as pd
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver

def clean_salary(x):
    try:
        return float(''.join(re.sub('[^0-9.]','',x)))
    except:
        return np.nan

def clean_job_ad_title(text):
    job_name = text.split('|')[0].strip()
    job_ad_details = ','.join(j.strip() for j in text.split('|')[1:])
    return job_name, job_ad_details

def clean_job_specs(text_list):
    job_hiring_company, job_company_address, job_salary_low, job_salary_high = 4*[np.nan]
    if len(text_list)>=5:
        job_hiring_company, job_company_address, job_salary_low, job_salary_high, *rest = text_list
        job_salary_low = clean_salary(job_salary_low)
        job_salary_high = clean_salary(job_salary_high)
    elif len(text_list)==4:
        job_hiring_company, job_company_address, job_salary_low, *rest = text_list
        job_salary_low = clean_salary(job_salary_low)
    elif len(text_list)==2:
        job_hiring_company, job_company_address = text_list
    return job_hiring_company, job_company_address, job_salary_low, job_salary_high

def clean_job_dates(text_list):
    if len(text_list)==2:
        date_posted, date_deadline = text_list[0].split(' Apply')
        date_posted = date_posted.replace('Posted ', '').strip()
        date_deadline = date_deadline.replace('before','').strip()
        return date_posted, date_deadline

def parse_job_search_result(this_job, current_time, show_raw=False):
    # get job link
    job_link = "https://www.kalibrr.com"+ this_job.find("a",{"class":'k-text-primary-color'})['href']
    # parse job text
    job_text = [] 
    for element in this_job:
        if element.text:
            if element.find('span'):
                job_text.append([e.text for e in element.find_all('span') if e.text])
            else:
                job_text.append(element.text)
    if show_raw:
        print(job_text)
    job_ad_title, job_specs, job_date_details, _ = job_text
    
    job_name, job_ad_details = clean_job_ad_title(job_ad_title)
    job_hiring_company, job_company_address, job_salary_low, job_salary_high = clean_job_specs(job_specs)
    job_date_posted, job_date_apply_deadline = clean_job_dates(job_date_details)
    
    #put results in list
    row = [current_time,job_name, job_ad_details, \
          job_hiring_company, job_company_address, job_salary_low, job_salary_high, \
          job_date_posted, job_date_apply_deadline,\
          job_link]
    
    return row

def parse_job_page(driver,job_link, current_time, show_raw=False):
    #Job Title
    driver.get(job_link)
    time.sleep(5)
    page_src = BeautifulSoup(driver.page_source.encode('utf-8').decode('ascii', 'ignore'), 'lxml')
    job_title =  page_src.find('h1', {"itemprop":"title"}).text.split("|")[0].strip()
    #Job Details- find and clean job summary
    page_text_sections = [section for section in  page_src.find_all('div', {"class":"md:k-flex"})]
    job_text_sections = [p for p in page_text_sections if "Jobs Summary" in p.text][0]

    keywords = ['Job Level','Job Category','Educational Requirement','Vacancy']
    job_summary = [p for p in job_text_sections.find_all('div',{"class":"md:k-flex"})\
                        if any([keyword in p.text for keyword in keywords])][0]
    if show_raw:
        print(job_summary.text)
        
    job_summary_headers = [j.text for j in job_summary.find_all('dt',{"class":"k-text-overline k-text-subdued"})]
    job_summary_content = [j.text for j in job_summary.find_all('dd',{"class":"k-inline-flex k-items-center"})]
    job_summary_dict = dict(zip(job_summary_headers,job_summary_content))

    job_level = job_summary_dict['Job Level']
    job_category = job_summary_dict['Job Category']
    job_educ_reqt = job_summary_dict['Educational Requirement']
    job_n_vacancies = int(job_summary_dict['Vacancy'].split(' ')[0])
    
    #put results in list
    row = [current_time, job_title, job_level, job_category, job_educ_reqt, job_n_vacancies, job_link]
    
    return row