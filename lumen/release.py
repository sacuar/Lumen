import json,re,urllib.request
from lumen import __version__
def check():
    req=urllib.request.Request("https://api.github.com/repos/sacuar/Lumen/releases/latest",headers={"User-Agent":"Lumen/"+__version__,"Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req,timeout=8) as r:data=json.load(r)
    tag=data.get("tag_name","")
    if not re.fullmatch(r"v\d+\.\d+\.\d+",tag):return {"available":False,"version":__version__}
    return {"available":tuple(map(int,tag[1:].split(".")))>tuple(map(int,__version__.split("."))),"version":tag[1:],"notes":data.get("body","")[:3000],"url":"https://github.com/sacuar/Lumen/releases/tag/"+tag}
