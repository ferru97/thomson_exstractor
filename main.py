from os import walk, path
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from utils import isPersonName, removeDisclaimer, haveTitle, removeDuplicate, genFileName, saveSpeeches, find_all

imput_folder = "input/"
out_folder = "results/"
    

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


def getNameDate(page):
    title =  (page.split('\n'))[1]
    soup = BeautifulSoup(title, 'html.parser')
    title = soup.text
    date = ""
    name = ""
    _type = "" 

    title = title.split('-')
    if len(title)>1:
        date = title[0].strip()
        name = title[1].strip()

    return date, name


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
    regex = r'<b>.*<\/b>'
    possible_speackers = re.findall(regex, speech)
    speackers = []
    for s in possible_speackers:
        if(isPersonName(s)):
            #speacker_pos = [m.start() for m in re.finditer(s, speech)]
            speacker_pos = find_all(speech,s)
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
        #temp = re.sub(r'\d+\s*<br>(.|\n)+THOMSON REUTERS STREETEVENTS(.|\n)+<\/i><br>', '',  temp) #remove footer
        #temp = re.sub(r'\d+\s*<br>(.|\n)+(<A.*>)?THOMSON REUTERS STREETEVENTS(.|\n)+<\/i><br>', '',  temp) #remove footer v2

        rows = temp.split('\n')
        if len(rows)>1 and len(rows[1])>5 and not haveTitle(rows[1]):
            name, provenance, role = getNameAndPosition(rows[0])
            text = getText(" ".join(rows[1:]))
            result.append([name,provenance,role,text])
        i = i + 1
        
    return result


def analyzeFile(content, folder):
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
        df = pd.DataFrame(columns=["RPT","Company","Date","Time","Type","Title","Speacker","Provenance","Role","Is Q&A","Is Presentation","Is Transcript","Content"])
        date, name = getNameDate(content[i[0]+1])
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
            saveSpeeches(speeches,tp,date,name,comp,rpt,df)
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
                    content = content.replace("<b>QUESTIONS AND ANSWERS</b>","'<b>Q U E S T I O N S   A N D   A N S W E R S</b>")
                    content = content.replace("<b>PRESENTATION</b>","<b>P R E S E N T A T I O N</b>")
                    content = re.sub('<IMG src=".*"><br>\nPRELIMINARY<br>\n',"",content)
                    content = re.sub('\*</b>',"</b>",content)
                    content = content.replace("&amp;","&")
                    content = content.replace(";","")
                analyzeFile(content,outf)
                count += 1
    print("Done!")