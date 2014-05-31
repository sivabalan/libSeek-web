import json, os, shelve, sys, shutil, stat
from threading import Thread

count = 0
shelveobj = shelve.open("persistent.shelve")

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def allDetails(entry, dirname):
    result = {}
    result["fullpath"] = os.path.join(dirname, entry)
    if entry.endswith(".py"):
        result["name"] = ".".join(entry.split(".")[:-1])
        result["pyfile"] = True
        parts = dirname.split(os.path.sep) + [result["name"]]
        if len(parts) > 1:
            parts = parts[1:]
        else:
            parts = []
        modulelist = []
    
        if len(parts) == 1:
            modulelist = parts
        else:
            for i in range(len(parts)):
                for  j in range(i + 1, len(parts) + 1):
                    modulelist.append(".".join(parts[i:j]))
        result["dirs"] = modulelist
    else:
        result["name"] = entry
        result["pyfile"] = False
    return result

def validfile(entry):
    return ("setup" not in entry and "__init__" not in entry and entry.endswith(".py")) or ("readme" in entry) or entry.endswith(".md") or "descri" in entry

def getAllNeededFiles(dirname):
    list_of_files = []
    for entry in os.listdir(dirname):
        abspath = os.path.join(dirname, entry)
        if os.path.isdir(abspath) and entry.lower() != "venv":
            list_of_files.extend(getAllNeededFiles(abspath))
        else:
            if validfile(entry.lower()):
                list_of_files.append(allDetails(entry, dirname))
    return list_of_files

def saveAllFiles(filelist, dirname, repo):
    destination = "../repoData/" + dirname + "/"
    try:
        os.mkdir(destination)
    except OSError:
        a = 5
    txt = open(destination + "description.txt", "w")
    py = open(destination + "allPythonContent.py", "w")
    modulelist = set()
    for filedata in filelist:
        file = open(filedata["fullpath"], "r")
        if filedata["pyfile"]:
            py.write("__FILENAME__ = " + filedata["name"] + "\n")
            py.write(file.read() + "\n")
            py.write("########NEW FILE########\n")
            modulelist = modulelist.union(set(filedata["dirs"]))
        else:
            txt.write(file.read() + "\n")
        file.close()
    modfile = open(destination + "mods.json", "w")
    json.dump(list(modulelist), modfile, sort_keys=True, indent=4, separators=(',', ': '))
    modfile.close()
    metadata = open(destination + "metadata.json", "w")
    json.dump(repo, metadata, sort_keys=True, indent=4, separators=(',', ': '))
    metadata.close()

def cleandata(repo):
    os.chmod(repo["name"], stat.S_IEXEC)
    shutil.rmtree(repo["name"] + "/.git", onerror=remove_readonly)
    list_of_files = getAllNeededFiles(repo["name"])
    saveAllFiles(list_of_files, repo["full_name"].replace("/", "-"), repo)
    #### change this for each os
    os.system("rmdir /Q /S " + repo["name"] + " > file.out")
    shelveobj[repo["clone_url"].encode("utf-8")] = True
    shelveobj.sync()
    

skip = set(["natural-earth-vector"])
data = json.load(open("Data.json", "r"))
try:
    for repo in data:
        if not shelveobj.has_key(repo["clone_url"].encode("utf-8")) and repo["name"] not in skip:
            os.system("git clone --depth 1 " + repo["clone_url"])
            count += 1
            print ("Done with " + str(count) + "/" + str(len(data)))
            t = Thread(target = cleandata, args = (repo,))
            t.start()
except KeyboardInterrupt:
    t.join()