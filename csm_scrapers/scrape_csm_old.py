"""
This code crawls through the old page of the Romanian Superior Council of the Magistracy to download
files containing monthly lists of all judges and prosecutors employed in every court and prosecutor's
office (or "parquet") in Romania, for the period 2009-2017. The files are then saved in a zip archive with
(imaginary) structure year --> month --> largest territorial unit (e.g.. a court of appeals jurisdiction,
with all subordinate courts), to the current directory.
Author of Python Code:
    Pârvulescu, Radu Andrei (2020)
    rap348@cornell.edu
"""

import requests
import time
from bs4 import BeautifulSoup
import re
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
import shutil


def get_file_urls(url_of_urls, headers, url_base, download_url_marker):
    """
    return a list of all urls leading to .doc(x) files
    :param url_of_urls: urls of page containing download urls
    :param headers: dict, header for requests.get
    :param url_base: str, path to root for href url
    :param download_url_marker: str, regex marker for correct download url
    :return: list
    """
    file_urls = []
    page = requests.get(url_of_urls, headers=headers)
    soup = BeautifulSoup(page.text, features="lxml")
    for link in soup.find_all('a', attrs={'href': re.compile(download_url_marker)}):
        file_urls.append(url_base + link.get('href'))
    return file_urls


def download_files_to_zip(urls, headers, zip_file):
    """
    downloads files and writes them to a zip archive
    :param urls: list of str, urls leading to files for downloading
    :param headers: dict, header for requests.get
    :param zip_file: zip file where file is deposited
    """
    exceptions = set()
    for u in urls:
        time.sleep(1)  # robots.txt asks for crawl-delay of 1
        try:
            file = requests.get(u, headers=headers)
            filename = '/' + u[40:44] + '/' + u[37:39] + '/' + u[34:]
            zip_file.writestr(filename, file.content, compress_type=ZIP_DEFLATED)
            if u in exceptions:
                exceptions.remove(u)
        except requests.exceptions.ConnectionError:
            exceptions.add(u)
    # recurse on exceptions
    if not exceptions:
        return
    else:
        time.sleep(30)  # give it half a minute before trying again
        download_files_to_zip(exceptions, headers, zip_file)


def make_zip_archive(url, headers, archive_name, url_base, download_url_marker):
    """
    Find all downloadable doc files on the old CSM site, download them then,
    and store them in a compressed directory in the local folder.
    :param url: str, url containing urls of files to be downloaded
    :param headers: dict, header to pass to requests, tell site who I am
    :param archive_name: str, name of zip archive in which everything will ultimately live
    :param url_base: str, path to root for href url
    :param download_url_marker: str, regex marker for correct download url
    :return: None
    """
    # work in memory, speedier
    in_memory_file = BytesIO()
    zip_file = ZipFile(in_memory_file, mode='w')

    # get the urls to files, download files, dump in zip archive
    file_urls = get_file_urls(url, headers, url_base, download_url_marker)
    download_files_to_zip(file_urls, headers, zip_file)
    zip_file.close()

    # write zip archive to disk
    in_memory_file.seek(0)
    with open(archive_name, 'wb') as f:
        shutil.copyfileobj(in_memory_file, f)


# params
head = {'User-Agent': 'Mozilla/5.0 (Linux Mint 18, 32-bit)'}
url_prosecutors = 'http://old.csm1909.ro/csm/index.php?cmd=080201&pg=1&arh=1'
url_judges = 'http://old.csm1909.ro/csm/index.php?cmd=080101&pg=1&arh=1'
url_path_base = 'http://old.csm1909.ro/csm/'
d_url_marker = '.doc'
judges_archive_name = 'judges_2009_2017.zip'  #
prosecutors_archive_name = 'prosecutors_2009_2017.zip'

make_zip_archive(url_judges, head, judges_archive_name, url_path_base, d_url_marker)
