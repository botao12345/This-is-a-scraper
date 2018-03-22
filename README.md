# This-is-a-scraper

## Introduction

These scrapers are designed to collect users' contact information on
various websites.

## Pre-requisites

* scrapy
* selenium (only used for places4student)

```
pip install Scrapy
pip install -U selenium 
```

Selenium requires a driver which must ne installed before running the script.

Here is a list of drivers for different browsers:
* [Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads)
* [Firefox](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
* [Safari](	https://webkit.org/blog/6900/webdriver-support-in-safari-10/)

## Running the scripts

Open the script in an IDE. 
- crawler_meetup.py requires log in information in the def parse method. The script can be modified and applied to different groups on meetup.com 
- other scripts can be run directly. The results will be saved in a .csv file in the current folder.

## Author 

* Tao Bo