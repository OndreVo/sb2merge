from typing import Dict,List,Tuple
import zipfile
import json
import os
import shutil
import sys

JSON_REL_PATH = 'project.json'

#zip all files in dir to a zip - handle
def zipdir(path:str, ziph:any)->None:
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), file)

#read JSON from sb2 file
def readJSON(sourceFile:str, workingDir:str)->Dict[str, any]:
    if os.path.isdir(workingDir):
        shutil.rmtree(workingDir)
    with zipfile.ZipFile(sourceFile,"r") as zip_ref:
        zip_ref.extractall(workingDir)
    with open(os.path.join(workingDir, JSON_REL_PATH), encoding="utf-8") as f:
        source:Dict[str, any] = json.load(f)
    return source

#merge 2 sb2 files
def mergeSB2(basePath:str, sourceFileName1:str, files:List[str], targetName:str)->None:
    targetFile = os.path.join(basePath, targetName)
    tempDir = os.path.join(basePath, 'sb2merge_temp')
    resultDir = os.path.join(basePath, 'sb2merge_result')
    sourceFile1 = os.path.join(basePath, sourceFileName1)

    #use first source as template for result - so extract it directly to result dir
    source1 = readJSON(sourceFile1, resultDir)

    anyMerge = False
    for sourceFileName2 in files:
        if sourceFileName2 == sourceFileName1: #don't merge source1 to itself
            continue
        anyMerge = True
        sourceFile2 = os.path.join(basePath, sourceFileName2)

        #second source uses temDir
        source2 = readJSON(sourceFile2, tempDir)

        mergeChildren(source1, source2, sourceFileName2)
        mergeVariables(source1, source2)

    #build result
    if anyMerge:
        with open(os.path.join(resultDir, JSON_REL_PATH), 'w') as outfile:
            json.dump(source1, outfile)
        with zipfile.ZipFile(targetFile,"w",zipfile.ZIP_DEFLATED) as zip_ref:
            zipdir(resultDir, zip_ref)

#merge children array in jsons
def mergeChildren(source1, source2, sourceFileName2):
    # copy and rename all children from source2 to source1
    for child in source2["children"]:
        if 'objName' in child:
            child["objName"] = sourceFileName2 + '-' + child["objName"]
        source1["children"].append(child)

#merge variables array in jsons
def mergeVariables(source1, source2):
    if not "variables" in source2:
        return #no need for merge
    if not "variables" in source1:
        source1["variables"] = []
    # copy all variables from source2 to source1
    for vardef in source2["variables"]:
        source1["variables"].append(vardef)

#merge all files to one
def mergeAll2One(basePath, fileName):
    files = [fileName for fileName in os.listdir(basePath) if fileName.endswith(".sb2")]
    mergeSB2(basePath, fileName, files, 'merged.sb2')

#merge one file to all
def mergeOne2All(basePath, fileName):
    for file2 in os.listdir(basePath):
        if not file2.endswith(".sb2"):
            continue
        if file2 == fileName: #don't merge source1 to itself
            continue
        mergeSB2(basePath, file2, [fileName], 'merged-'+file2)

def printHelp():
    print("sb2Merge Util - merging sb2 files")
    print("Usage:")
    print("  sb2merge [--o2a] basePath fileName")
    print("  --o2a - optional - merge fileName to every other sb2 file in basePath")
    print("        - when missing - merge all sb2 files in basePath to fileName (will be stored as merged.sb2)")
    print("  basePath - directory with sb2 files")
    print("  fileName - template or target based on --o2a flag")

#parse commandline arguments - one2All mode, base path, file name
def parseArguments()->Tuple[bool,str,str]:
    one2All = False
    if len(sys.argv) < 3:
        printHelp()
        return (True,'','')
    idx = 1
    if (sys.argv[idx].startswith("--")):
        if sys.argv[idx] == "--o2a":
            one2All = True
        idx += 1
    basePath = sys.argv[idx]
    idx += 1
    if len(sys.argv) <= idx:
        printHelp()
        return (True,'','')
    fileName = sys.argv[idx]

    return (one2All, basePath, fileName)


if __name__ == '__main__':
    (one2All,basePath,fileName) = parseArguments()
    if fileName != '':
        if one2All:
            mergeOne2All(basePath, fileName)
        else:
            mergeAll2One(basePath, fileName)
