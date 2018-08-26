# Car Comparison
## Background & Info
This repository holds two scripts to accomplish one goal.

I started this project because I wanted to buy a car. I talked to my friends, and they gave me their opinion, but it didn't necessarily always line up, and it generally seemed to boil down to _only_ opinion. Word-of-mouth is great, and of course you can find a great car just based on what other people tell you based on their experiences. However, I though to myself, what about using data?

From there it's an easy two-step process:

1) The first part of the project was getting the data. `scraper.py` scrapes data from an automobile information website. I was interested in SUVs, so these scripts are set up to find the best SUV. Therefore, the script only scrapes SUVs. This can be easily changed.

2) The second part was analyzing the data. `comparer.py` takes care of this. I initially wrote it as a Jupyter Notebook, which you can find in the `notebooks` folder. You can just run comparer.py, though, and it will take any CSV files in the `input` folder and print a CSV to a new `output` folder. There's no error-handling for there being no input folder so just run `scraper.py` first, okay?

The `comparer.py` script will, by default, create a CSV of the top 100 best cars for you. Currently, this is based on gas mileage (city/highway), fuel tank capacity, and cargo space.

## Requirements
You should be able to get everything you need by installing Anaconda:
https://www.anaconda.com/download/

## TODOs
* Allow command line options so you don't have to go in and change the code directly
* Error handling if the input 
* Better scraper error handling (404s etc)
* Caching or something? If there's already data for a car make, it shouldn't be redownloaded
* Machine learning! /s
