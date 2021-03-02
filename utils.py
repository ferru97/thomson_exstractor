from os import walk, path
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

MonthDict={ "january":1,
            "february":2,
            "march":3,
            "april":4,
            "may":5,
            "june":6,
            "july":7,
            "august":8,
            "september":9,
            "october":10,
            "november":11,
            "december":12
}

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)

def isPersonName(name):
    soup = BeautifulSoup(name, 'html.parser')
    name = soup.text.strip().replace(">",'')
    uppers = sum(1 for c in name if c.isupper())
    if len(name.replace(" ",''))<1:
        return False

    upper_prc = (100/len(name.replace(" ",'')))*uppers

    if not name[0].isupper():
        return False
    if len(name)<4:
        return False
    if upper_prc>30:
        return False
    
    return True


def removeDisclaimer(pages):
    c = 0
    while(c<len(pages)):
         pages[c] = re.sub(r'<b>D I S C L A I M E R<\/b>(.|\n)*', '',  pages[c])
         pages[c] = re.sub(r'<A name="outline"></a><h1>Document Outline</h1>(.|\n)*</ul>','',pages[c])
         c += 1
    return pages


def haveTitle(s):
    soup = BeautifulSoup(s, 'html.parser')
    txt = soup.text.strip()
    uppers = sum(1 for c in txt if c.isupper())
    upper_prc = (100/len(txt.replace(" ",'')))*uppers
    
    return upper_prc>30


def removeDuplicate(l):
    newSpeackers = []
    dict_ = {}
    for e in l:
        k = e[0]+str(e[1])
        if not k in dict_:
            newSpeackers.append(e)
            dict_[k] = True
    return newSpeackers



def genFileName(location,name):
    name = name.replace('/','')
    name = re.sub('[^-a-zA-Z0-9_.() ]+', '', name)
    out = location+name

    if len(out)>150:
        name = name[:-4]
        while(len(out)>150):
            name = name[:-1]
            out = location+name
        name += ".csv"

    n = 1
    while path.exists(out):
       n += 1
       out = location+"("+str(n)+')'+name
    return out


def getDateTimeType(date):
    day = "NA"
    time = "NA"
    _type = "NA"
    try:
        date = date.split('/')
        day = date[0]

        temp = day.replace(',','').split(" ")
        m = str(MonthDict[temp[0].lower()])
        d = temp[1]
        y = temp[2]
        if len(m)==1:
            m = '0'+m
        if len(d)==1:
            d = '0'+d
        day = m+"/"+d+"/"+y
      
        if len(date)>1:
            time = date[1]
        
        date_type = time.split(",")
        if (len(date_type))>1:
            time = date_type[0].strip()
            _type = date_type[1].strip()
    except:
        pass

    return day,time,_type

def removeFooter(content):
    content =  re.sub(r'\d+<br>\n[^"]+<\/i>', '',  content)
    return content.replace("||","")

def saveSpeeches(speeches,speech_type,date,name,company,rpt,df):
    
    day,time,_type = getDateTimeType(date)

    if speech_type == 0:
        isPresentation = True
        isQeA = False
        isTranscript = False
    elif speech_type==1:
        isPresentation = False
        isQeA = True
        isTranscript = False
    else:
        isPresentation = False
        isQeA = False
        isTranscript = True
   

    for s in speeches:
        new_row = len(df.index)
        df.loc[new_row,"RPT"] = rpt.replace("Rpt. ",'')
        df.loc[new_row,"Company"] = company
        df.loc[new_row,"Date"] = day
        df.loc[new_row,"Time"] = time
        df.loc[new_row,"Title"] = name
        df.loc[new_row,"Speacker"] = s[0]
        df.loc[new_row,"Provenance"] = s[1]
        df.loc[new_row,"Role"] = s[2]
        df.loc[new_row,"Is Q&A"] = isQeA
        df.loc[new_row,"Is Presentation"] = isPresentation
        df.loc[new_row,"Is Transcript"] = isTranscript
        df.loc[new_row,"Content"] = s[3]
        df.loc[new_row,"Type"] = _type