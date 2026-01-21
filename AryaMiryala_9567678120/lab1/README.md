# DSCI 560 - Lab 1: Installation, Setup, and Web Scraping

## Overview
This repository contains the submission for Laboratory Assignment 1. The objective of this lab was to set up a Linux-based virtual environment (Ubuntu), install Python and necessary libraries, and implement Python scripts for basic interaction, web scraping, and data processing.

The project scrapes dynamic financial and news data from CNBC and processes it into structured CSV files.

## Project Structure
The project is organized into the following directory structure:

```text
├── scripts/
│   ├── task_1.py           # Basic Python input/output script
│   ├── web_scraper.py      # Selenium-based web scraper for CNBC
│   └── data_filter.py      # Data parser to extract and save CSVs
├── data/
│   ├── raw_data/           # Stores the raw HTML file from the scraper
│   │   └── web_data.html
│   └── processed_data/     # Stores the cleaned and structured CSV files
│       ├── market_data.csv
│       └── news_data.csv
└── README.md