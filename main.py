from os import walk, path
from bs4 import BeautifulSoup
import re

imput_folder = "input\\"

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
         pages[c] = re.sub(r'<b>D I S C L A I M E R</b>(.|\n)*', '',  pages[c])
         c += 1
    
    return pages


def analyzeFile(content):
    index = getIndex(content)
    
    content = content.split("<hr>") 
    content = removeDisclaimer(content)
    print(content[16])

    #soup = BeautifulSoup(content, 'html.parser')



if __name__ == "__main__":
    for (dirpath, dirnames, filenames) in walk(imput_folder):
        for file in filenames:
            if "s.html" in file:
                file_path = path.join(dirpath,file)
                with open(file_path, 'r') as f:
                    content = f.read()
                analyzeFile(content)
