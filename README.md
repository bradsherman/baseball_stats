Baseball Statistics
===================

Brad Sherman
------------

This repository contains a program that takes in a large set of baseball statistics located in data/raw/pitchdata.csv and outputs a new csv at data/processed/output.csv. To install all the dependencies, just run:
```
pip install -r requirements.txt
```
Then you should be able to run:
```
cd python_hiring_test
python run.py
```
The resulting csv should be outputted in about 1.5 seconds!

**NOTE:** I wrote this using python 3.6.1, it does not pass the tests or even run to completion with python 2, so please make sure to test it with python 3.