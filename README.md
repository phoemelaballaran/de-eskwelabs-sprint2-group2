# Eskwelabs DE Bootcamp Sprint 2 Project (Group 2)

This is a data engineering project where we scraped data from recruitment websites such as Indeed, Kalibrr, and Glassdoor. The scraped data is then transformed into a parquet file, stored in a Google Cloud Storage bucket, and transfered to a BigQuery database.

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
