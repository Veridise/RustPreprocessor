
import json
import sys
import re


def readMetadata(metadataList):
    summary = dict()
    summary["compiler"] = "cargo-contract"
    summary["version"] = readVersion(metadataList[0])
    summary["contracts"] = [readContract(c) for c in metadataList]
    return summary

def readVersion(metadata):
    return metadata["source"]["language"]

def readContract(metadata):
    contractSpec = dict()
    contractSpec["id"] = 0
    contractSpec["name"] = readContractName(metadata)
    impSpec = readContractSpec(metadata["V3"])
    contractSpec.update(impSpec)
    return contractSpec

def readContractName(metadata):
    return metadata["contract"]["name"]

def readContractSpec(spec):
    contractImp = dict()
    contractImp["inherits"] = []
    idToType = readTypes(spec["types"])
    contractImp["events"] = readEvents(idToType, spec["spec"]["events"])
    contractImp["functions"] = readConstructors(idToType, spec["spec"]["constructors"])
    contractImp["functions"] += readMessages(idToType, spec["spec"]["messages"])
    contractImp["variables"] = readStorage(idToType, spec["storage"])
    contractImp["structs"] = []
    contractImp["enums"] = []
    return contractImp

def readConstructors(idToType, constructorList):
    return [readConstructor(idToType, c) for c in constructorList]

def readArgs(idToType, argList):
    return [readArg(idToType, a) for a in argList]

def readArg(idToType, arg):
    a = dict()
    if("label" in arg):
        a["name"] = arg["label"]
    else:
        if("displayName" in arg):
            a["name"] = arg["displayName"][0]
        else:
            a["name"] = arg["type"]["displayName"]

    if(isinstance(arg["type"], dict)):
        a["type"] = idToType[arg["type"]["type"]]
    else:
        a["type"] = idToType[arg["type"]]

    return a

def readConstructor(idToType, construct):
    fn = dict()
    fn["isConstructor"] = True
    fn["selector"] = construct["selector"]
    fn["name"] = construct["label"]
    fn["visibility"] = "public"
    fn["mutability"] = "payable" if construct["payable"] else "nonpayable"
    fn["params"] = readArgs(idToType, construct["args"])
    fn["returns"] = []
    fn["modifiers"] = []
    return fn
    

def readEvents(idToType, eventList):
    return [readEvent(idToType, e) for e in eventList]

def readEvent(idToType, event):
    e = dict()
    e["name"] = event["label"]
    e["params"] = readArgs(idToType, event["args"])
    return e

def readMessages(idToType, msgList):
    return [readMessage(idToType, m) for m in msgList]

def readMessage(idToType, spec):
    fn = dict()
    fn["isConstructor"] = False
    fn["selector"] = spec["selector"]
    fn["name"] = spec["label"]
    fn["visibility"] = "public"
    fn["mutability"] = "payable" if spec["payable"] else "nonpayable"
    fn["params"] = readArgs(idToType, spec["args"])
    fn["returns"] = []
    if(spec["returnType"]):
        fn["returns"].append(readArg(idToType, spec["returnType"]))
    fn["modifiers"] = []
    return fn

def readStructFields(idToType, fieldList):
    return [readStructField(idToType, f) for f in fieldList]

def readStructField(idToType, field):
    f = dict()
    f["name"] = field["name"]
    f["type"] = idToType[field["layout"]["cell"]["ty"]]
    return f

def readStorage(idToType, storage):
    if("struct" in storage):
        return readStructFields(idToType, storage["struct"]["fields"])
    print("Unknown storage")
    sys.exit(1)

def getName(idToType, ty):
    if(ty["subType"] == "MapType"):
        if(ty["key"] in idToType):
            keyName = getName(idToType, idToType[ty["key"]])
        else:
            keyName = getName(idToType, ty["key"])

        if(ty["value"] in idToType):
            valName = getName(idToType, idToType[ty["value"]])
        else:
            valName = getName(idToType, ty["value"])

        return "Mapping<" + keyName + ", " + valName + ">"
    elif(ty["subType"] == "ArrayType"):
        if(ty["base"] in idToType):
            return "Array<" + getName(idToType, idToType[ty["base"]]) +  ">"
        else:
            return "Array<" + getName(idToType, ty["base"]) +  ">"
    return ty["name"]

def readTypes(types):
    idToType = {t["id"]:readType(t["type"]) for t in types}

    for ty in idToType.values():
        if(ty["subType"] == "MapType"):
            ty["name"] = getName(idToType, ty)
            ty["key"] = idToType[ty["key"]]
            ty["value"] = idToType[ty["value"]]
        elif(ty["subType"] == "ArrayType"):
            name = getName(idToType, ty)
            ty["base"] = idToType[ty["base"]]
   
    return idToType

def readType(typeSpec):
    ty = dict()
    if("path" in typeSpec):
        typename = ":".join(typeSpec["path"])
        if(typename == "ink_storage:lazy:mapping:Mapping"):
            ty["subType"] = "MapType"
            ty["key"] = typeSpec["params"][0]["type"]
            ty["value"] = typeSpec["params"][1]["type"]
            return ty
        if(typename == "ink_env:types:AccountId"):
            ty["subType"] = "ElementaryType"
            ty["name"] = "address"
            return ty
        ty["name"] = typename
    if("primitive" in typeSpec["def"]):
        ty["subType"] = "ElementaryType"
        if(re.match(r'u\d+', typeSpec["def"]["primitive"])):
            ty["name"] = "uint" + typeSpec["def"]["primitive"][1:]
        if(re.match(r'i\d+', typeSpec["def"]["primitive"])):
            ty["name"] = "int" + typeSpec["def"]["primitive"][1:]
    if("array" in typeSpec["def"]):
        ty["subType"] = "ArrayType"
        ty["base"] = typeSpec["def"]["array"]["type"]
    if("composite" in typeSpec["def"]):
        ty["subType"] = "UserDefinedType"
        ty["refId"] = -1

    # We will probably need to fix this later. Just not sure now what type information we needs
    if("subType" not in ty):
        ty["subType"] = "ElementaryType"
        if("name" not in ty):
            ty["name"] = list(typeSpec.keys())[0]

    return ty  
    



if(len(sys.argv) < 1):
    print("Usage: summarizer.py [metadata files]")
    sys.exit(1)

metadataList = [json.load(open(f)) for f in sys.argv[1:]]
summary = readMetadata(metadataList)
print(json.dumps(summary, indent=2))

