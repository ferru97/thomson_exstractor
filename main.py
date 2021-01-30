from os import walk, path
from bs4 import BeautifulSoup
import pandas as pd
import re

imput_folder = "input/"

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
        index.append( (int(temp[0].strip()),int(temp[1].strip())-1) )

    return index

def removeDisclaimer(pages):
    c = 0
    while(c<len(pages)):
         pages[c] = re.sub(r'<b>D I S C L A I M E R<\/b>(.|\n)*', '',  pages[c])
         c += 1
    return pages

def getName(page):
    title =  (page.split('\n'))[1]
    soup = BeautifulSoup(title, 'html.parser')
    title = soup.text

    title = title.split('-')
    date = (title[0].split('/'))[0].strip()
    name = title[1].strip()

    return date, name


def getContent(start, end, speech):
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
    #continue


def analyzeFile(content, df):
    index = getIndex(content)
    
    content = content.split("<hr>") 
    content = removeDisclaimer(content)

    for i in index:
        new_row = len(df.index)
        date, name = getName(content[i[0]+1])

        speech = " ".join(content[i[0]:i[1]])

        start_presentation = speech.find("<b>P R E S E N T A T I O N</b>")
        start_qa = speech.find("<b>Q U E S T I O N S   A N D   A N S W E R S</b>")

        speech = speech.replace('<b>P R E S E N T A T I O N</b>', '')
        speech = speech.replace('<b>Q U E S T I O N S   A N D   A N S W E R S</b>', '')
        #speech = speech.replace('\n', ' ')

        end_presentation = len(speech)
        end_qa = len(speech) 
        if start_qa>start_presentation:
            end_presentation = start_qa-1
        
        if(start_presentation>0):
            getContent(start_presentation,end_presentation,str(speech))

        df.loc[new_row,"Date"] = date
        df.loc[new_row,"Name"] = name

    #soup = BeautifulSoup(content, 'html.parser')



if __name__ == "__main__":
    df = pd.DataFrame(columns=["RPT","Date","Name","Is Presentation","Is Q&A","Content"])

    for (dirpath, dirnames, filenames) in walk(imput_folder):
        for file in filenames:
            if "s.html" in file:
                file_path = path.join(dirpath,file)
                with open(file_path, 'r', encoding="utf8", errors='ignore') as f:
                    content = f.read()
                analyzeFile(content,df)

    df.to_csv("results.csv")
