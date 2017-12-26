import sys
import os
import json

def traversal(rootDir):
    for index, lists in enumerate(os.listdir(rootDir)):
        path = os.path.join(rootDir, lists)
        json_deal(path)
        if index %10000 == 0:
            print(index)

def deal(filename):
    with open(filename,'rt',encoding="utf-8") as f:
        content = {'text':""}
        for index, line in enumerate(f):
            if index == 0:content["url"] = line.replace('\n','')
            if index == 1:content['title'] = line.replace('<h1>','').replace('</h1>','').replace('\n','')
            if index != 0 and index != 1: content['text'] += line.replace('\n','')
        content['comment'] = 'no comment'
    jsonfile = filename.replace('documents','json_documents').replace('\\','/').replace('E:','N:')
    with open(jsonfile,'wt', encoding="utf-8") as f:
        json.dump(obj=content,fp=f,ensure_ascii=False)

def json_deal(filename):
    with open(filename, 'rt', encoding="utf-8") as f:
        input_data = json.load(f)
        #print(input_data)
        input_data["text"] = input_data["text"].replace("\"", "").replace("·","")
    jsonfile = "/home/dc/桌面/json/"+filename.split("/")[-1]
    with open(jsonfile, 'wt', encoding = "utf-8") as f:
        jsonObj = json.dumps(obj=input_data, ensure_ascii=False)
        f.write(jsonObj)

traversal('/home/dc/桌面/json_documents')