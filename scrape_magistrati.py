#scrape_magistrati.py
#py script for finding the links for downloading files from two lists of links, organising the
#links by which court they refer to, then making lists of these links according to this hierarchy
#these list then feed into a crawler that actually downloads the files and puts them in the appropriate
#directory

#NB!!! It looks like this thing has neglected to scrape date for the military court of appeals! DEBUG!!

import re, os, time, urllib.request

root_path = "/home/radu/insync/docs/CornellYears/6.SixthYear/currently_working/gender_judiciary/data/magistrati/crawler/"
jud = root_path + "judecatori_html_of_links.txt"
proc = root_path + "procurori_html_of_links.txt"
root_link = 'http://old.csm1909.ro/csm/'

def extract_links_old(file):
    """
    Extracts links from the old-style CSV website (this updates up to 2017).
    :param file: path to file which contains a certain HTML to be searched
            --> HTML chunk taken from line 1387 of the sites below, from a RO judicial site that has full employment
                rolls for several days
            --> old.csm1909.ro/csm/index.php?cmd=080101&pg=1&arh=1(judges)
            --> old.csm1909.ro/csm/index.php?cmd=080201&pg=1&arh=1 (prosecutors)
    :return: a dictionary: key is hieararchical unit, values is list of links associated with that unit
    """

    dict = {} #initiate empty dict
    with open(file) as f:
        html = f.readline() #open first line
        # make search object. Each object corresponds to one court/parquet, i.e. one hierarchical unit
        search_all = re.findall(r'<tr>(.*?)<table width="100%" >',html)
        #iterate over units
        for unit in search_all:
            #find name of unit, associated links, then make key-value pair in in dict
            name = re.search(r'"titlu_comunicat">(.*?)<',unit).group(1)
            links = re.findall(r'href="(.*?)"',unit)
            dict.update({name:links})

    return dict

def download_files(dict,root_path,root_link):
    """
    :param dict: dict whose keys are different hierarchical units, and whose entries are links to download from
    :param root_path: root of path where to place directory with downloads
    :param root_link: root of link to ping
    :return: None
    """

    counter = 0
    #iterate over key-values
    for unit, list_of_links in dict.items():
        for link in list_of_links: #go through the list of links
            #make appropriate folders, unless they already exists. Hierarchy is year, month, court/parquet
            if not os.path.exists(root_path + link[14:18] + '/' + link[11:13] + '/' + unit.replace(" ","")):
                os.makedirs(root_path + link[14:18] + '/' + link[11:13] + '/' + unit.replace(" ",""))
            # their robots.txt request a one second lag, BE KIND
            time.sleep(1)
            url = root_link + link
            #change header so we don't get the 403 Error i.e. generic bloc for python scrapers
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Linux Mint 18, 32-bit)')]
            urllib.request.install_opener(opener)
            #now download
            urllib.request.urlretrieve(url, root_path + link[14:18] + '/' + link[11:13] + '/' + unit.replace(" ","") + link[7:])
            counter += 1
            print(counter) #just to keep track


#get dicts for courts and parquets
courts = extract_links_old(jud)
parquets = extract_links_old(proc)

#now build your DB
#download_files(courts,root_path,root_link)
download_files(parquets,root_path,root_link)
