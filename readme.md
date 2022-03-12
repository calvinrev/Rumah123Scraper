# Rumah123Scraper
This repository contains the code for crawling property data from (https://www.rumah123.com). This code is written in Python by using Requests and BeautifulSoup4 library. The data scraping method is done by utilizing the html elements found on the website. The scraper starts crawling from listing all active ads and then visit it one by one. After that, then it visits agents' pages and visit all rented and sold property ads data and then visit it one by one. The collected data is stored in a temporary database. After that, the data will be preprocessed and after that the results are saved to the main database. The database we use in this repository is MySql.

## Setup
1) pip install -r requirements.txt.
2) Create a new MySql database, then import the model/db.sql file. Two tables will be created, namely the rumah123 table and the rumah123temp table.
3) Open model/pipeline.py file, then change the DB setup adjusted to the database you have created previously.

## Workflow
1) Active Ads
   - Run the activeList.py file
   - Run the activeDetails.py file
2) Transacted Ads
   - Run the transactedList.py file
   - Run the transactedDetails.py file
3) Preprocess Data
   - Run the preprocessing.py file