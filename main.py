from os import walk, path
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

imput_folder = "input/"
out_folder = "results/"

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

def isPersonName(name):
    soup = BeautifulSoup(name, 'html.parser')
    name = soup.text.strip()
    uppers = sum(1 for c in name if c.isupper())
    upper_prc = (100/len(name.replace(" ",'')))*uppers

    if not name[0].isupper():
        return False
    if len(name)<4:
        return False
    if upper_prc>30:
        return False
    
    return True
    

def getIndex(content):
    index = []
    regex = r'<A href=".*">\d+ - \d+</a>'
    links = re.findall(regex, content) 

    for l in links:
        temp = re.sub(r'<A href=".*">', '', l)
        temp = re.sub(r'</a>', '', temp)
        temp = temp.split('-')
        index.append( (int(temp[0].strip()),int(temp[1].strip())) )

    if len(index)>0:
        return index
    else: 
        return [(0,len(content))]


def removeDisclaimer(pages):
    c = 0
    while(c<len(pages)):
         pages[c] = re.sub(r'<b>D I S C L A I M E R<\/b>(.|\n)*', '',  pages[c])
         pages[c] = re.sub(r'<A name="outline"></a><h1>Document Outline</h1>(.|\n)*</ul>','',pages[c])
         c += 1
    return pages

def getName(page):
    title =  (page.split('\n'))[1]
    soup = BeautifulSoup(title, 'html.parser')
    title = soup.text
    date = ""
    name = ""

    title = title.split('-')
    if len(title)>1:
        date = title[0].strip()
        name = title[1].strip()

    return date, name


def haveTitle(s):
    soup = BeautifulSoup(s, 'html.parser')
    txt = soup.text.strip()
    uppers = sum(1 for c in txt if c.isupper())
    upper_prc = (100/len(txt.replace(" ",'')))*uppers
    
    return upper_prc>30


def getNameAndPosition(line):
    soup = BeautifulSoup(line, 'html.parser')
    line = soup.text.strip()
    line = line.split('-')
    
    name = line[0].strip()

    provenance = "NA"
    if len(line)>1:
        provenance = line[1].strip()

    role = "NA"
    if len(line)>2:
        role = line[2].strip()

    return name, provenance, role
    

def getText(speech):
    soup = BeautifulSoup(speech, 'html.parser')
    speech = soup.text
    return speech.replace('\n'," ").strip()


def getSpeeches(speech):
    def removeDuplicate(l):
        newSpeackers = []
        dict_ = {}
        for e in l:
            k = e[0]+str(e[1])
            if not k in dict_:
                newSpeackers.append(e)
                dict_[k] = True
        return newSpeackers

    regex = r'<b>.*<\/b>'
    possible_speackers = re.findall(regex, speech)
    speackers = []
    for s in possible_speackers:
        if(isPersonName(s)):
            speacker_pos = [m.start() for m in re.finditer(s, speech)]
            for p in speacker_pos:
                speackers.append((s,p))
    
    speackers = removeDuplicate(speackers)
    speackers.sort(key = lambda x: x[1])

    result = []
    i = 0
    while i < len(speackers):
        speech_start = (speackers[i])[1]
        if i<len(speackers)-1:
            speech_end =  (speackers[i+1])[1]
        else:
            speech_end =  len(speech)
        
        temp = speech[speech_start:speech_end]
        temp = re.sub(r'<A name=.*<br>', '',  temp) #remove header
        temp = re.sub(r'\d+\s*<br>\nTHOMSON(.|\n)+<i>\d+<\/i><br>', '',  temp) #remove footer
        temp = re.sub(r'\d+\s*<br>\n(<A.*>)?THOMSON(.|\n)+companies.<br>', '',  temp) #remove footer v2
        
        rows = temp.split('\n')
        if len(rows)>1 and len(rows[1])>5 and not haveTitle(rows[1]):
            name, provenance, role = getNameAndPosition(rows[0])
            text = getText(" ".join(rows[1:]))
            result.append([name,provenance,role,text])
        i = i + 1
        
    return result


def genFileName(location,name):
    name = name.replace('/','')
    name = re.sub('[^-a-zA-Z0-9_.() ]+', '', name)
    out = location+name

    while(len(out)>240):
        name = name[:-1]
        out = location+name

    n = 1
    while path.exists(out):
       n += 1
       out = location+"("+str(n)+')'+name
    return out

def analyzeFile(content, folder):
    def saveSpeeches(speeches, type,date,name,company):
        date = date.split('/')
        day = date[0]

        try:
            temp = day.replace(',','').split(" ")
            m = str(MonthDict[temp[0].lower()])
            d = temp[1]
            y = temp[2]
            if len(m)==1:
                m = '0'+m
            if len(d)==1:
                d = '0'+d
            day = m+"/"+d+"/"+y
        except:
            pass

        time = "NA"
        if len(date)>1:
            time = date[1]

        if tp == 0:
            isPresentation = True
            isQeA = False
            isTranscript = False
        elif tp==1:
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

    index = getIndex(content)
    if len(index) == 1:
        rpts = ["NA"]
        companies = ["NA"]
    else:
        rpts = re.findall(r'Rpt\. \d+', content)     
        companies = re.findall(r'<A href=".*"><b>.*</b></a><br>', content)
        companies = [re.sub(r'(<A.*<b>)|(</b></a><br>)','',e) for e in companies]    
    
    content = content.split("<hr>") 
    content = removeDisclaimer(content)

    for i,rpt,comp in zip(index,rpts,companies):
        df = pd.DataFrame(columns=["RPT","Company","Date","Time","Title","Speacker","Provenance","Role","Is Q&A","Is Presentation","Is Transcript","Content"])
        date, name = getName(content[i[0]+1])
        speech = " ".join(content[i[0]:i[1]])

        start_presentation = speech.find("<b>P R E S E N T A T I O N</b>")
        start_qa = speech.find("<b>Q U E S T I O N S   A N D   A N S W E R S</b>")
        start_transcript = speech.find("<b>T R A N S C R I P T</b><br>")
        end_qa = len(speech) 
        
        if start_qa>start_presentation:
            end_presentation = start_qa-1
        else:
            end_presentation = len(speech)

        if start_presentation > 0:
            presentation = speech[start_presentation:end_presentation]
        else:
            presentation = None

        if start_qa > 0:
            qa = speech[start_qa:end_qa]
        else:
            qa = None

        if qa==None and presentation==None and start_transcript>0:
            transcript = speech[start_transcript:len(speech)]
        else:
            transcript = None

        tp = 0
        for part in [presentation,qa,transcript]:
            if part==None:
                continue
            part = part.replace('<b>P R E S E N T A T I O N</b>', '')
            part = part.replace('<b>Q U E S T I O N S   A N D   A N S W E R S</b>', '')
            speeches = getSpeeches(part)
            saveSpeeches(speeches,tp,date,name,comp)
            tp += 1

        df.to_csv(genFileName(out_folder+folder+"/",name+".csv"),encoding='utf-8-sig')

if __name__ == "__main__":
    count = 1
    for (dirpath, dirnames, filenames) in walk(imput_folder):
        for file in filenames:
            if "s.html" in file:
                print("{} - {}".format(str(count),file))
                outf = file.replace("s.html",'')
                if not os.path.isdir(out_folder+outf):
                    os.mkdir(out_folder+outf)
                file_path = path.join(dirpath,file)
                with open(file_path, 'r', encoding="utf8", errors='ignore') as f:
                    content = f.read()
                    content = content.replace("<b>QUESTIONS AND ANSWERS<br>","'<b>Q U E S T I O N S   A N D   A N S W E R S</b><br>'\n<b>")
                    content = re.sub('<IMG src=".*"><br>\nPRELIMINARY<br>\n',"",content)
                    content = re.sub('\*</b>',"</b>",content)
                    content = content.replace("&amp;","&")
                    content = content.replace(";","")
                analyzeFile(content,outf)
                count += 1
    print("Done!")