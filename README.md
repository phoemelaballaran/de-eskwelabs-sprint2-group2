# Eskwelabs DE Bootcamp Sprint 2 Project (Group 2)

In January 2022, Philippine Statistics Authority estimated that 94% of the labor force are employed while 6% are unemployed. These numbers may seem impressive but when we convert the 6% into the number of Filipinos without jobs, it’s almost 3 million. One of the government programs that addresses unemployment is the Technical Education and Skills Development Authority or TESDA. So for our project we decided to provide data that will enable them to create data-informed upskilling programs. We scraped Philippine-based jobs from Indeed, Glassdoor, and Kalibrr; created a BigQuery dataset containing the combined data from the scraped sites, and created an ETL pipeline that updates every 24 hours.

[Link to the presentation](https://drive.google.com/file/d/1aBvXHXe595E721rUVA1-2Y4YFTzuY2mP/view?usp=sharing)

## Requirements Installation

Utilize the requirements.txt file inside each scraper folder

```bash
pip install -r requirements
```
## Other Requirements

Create your own GCP key, DO NOT upload the .json file to your repository.

## Others

```python

#rename filepath according to VM or Local
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your_gcp_config.json'

#rename bucket name according to GCS bucket
bucket = client.get_bucket('bucket_name/folder_name')

```

## License
[MIT](https://choosealicense.com/licenses/mit/)
