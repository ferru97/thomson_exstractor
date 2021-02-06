# thomson_exstractor
Convert THOMSON REUTERS STREETEVENTS reports from PDF to CSV

## Requirements
- Python 3.x downloadable from [HERE](https://www.python.org/downloads/)
- [*Boxoft PDF to HTML*](http://www.boxoft.com/pdf-to-html/#:~:text=Boxoft%20PDF%20to%20HTML%20Freeware,HTML%20format%20for%20publishing%20online.) to convert the PDFs to HTMLs.

## How to use
- Place the folders containing the converted HTMLs in the folder *input/*. Note: the script will analyze only the HTMLs ending with *s.html*
- Only the first time, open the CMD in the script folder and run `pip install -r requirements.txt` to install the requirements
- To run the script, open the CMD in the script folder and run `py main.py`
- The results are saved in *results/*

**Remember to empty the *resources* folder before running the script**