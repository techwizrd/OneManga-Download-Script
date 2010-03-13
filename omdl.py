#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""Download manga chapters from 'http://onemanga.com'.
"""

import os, sys
from BeautifulSoup import BeautifulSoup

def get_page_html(url):
    """Download a page and return the HTML."""
    os.system("wget -q %s -O page.html" % url)
    html = ""
    with open("page.html") as html_file:
        for line in html_file:
            html += line
    return html

def get_first_page_url(manga, chapter):
    """Get the URL of the first page of the manga."""
    html = get_page_html("http://onemanga.com/%s/%s/" % (manga, chapter))
    soup = BeautifulSoup(html)
    fpage = soup.findAll( 'div', {'id' : 'chapter-cover'})[0].li.a['href']
    return "http://onemanga.com" + fpage

def download_image(url, page_number):
    """Download an image given its URL."""
    os.system("wget -q %s -O %s.jpg" % (url, page_number))

def get_image_url(soup):
    """Get the manga image for the page."""
    return soup.findAll('img', {'class' : 'manga-page'})[0]['src']

def make_image_url(base_url, page_number):
    """docstring for make_image_url"""
    return "%s/%s.jpg" % (os.path.dirname(base_url), page_number)

def get_page_numbers(soup):
    """Get the page numbers for the chapter."""
    select = soup.findAll('select', {'class' : 'page-select'})[0]
    return select.findAll('option')

def write_urls_to_file(urls, filename):
    """Write all urls from urls array to a new text file at filename."""
    with open(filename, 'w') as url_file:
        for url in urls:
            url_file.write(url + "\n")

def make_comic_book_archive(dirname):
    """
    Zip all images in the given directory into a CBZ file and return the
    filename of the created CBZ file.
    """
    os.system("zip -qr %s.cbz %s/* && rm -rf %s" % (dirname, dirname, dirname))
    return os.path.abspath("%s.cbz" % dirname)

def download_manga_chapter(manga, chapter):
    """Download a manga chapter from 'http://onemanga.com'."""
    print (get_first_page_url(manga, chapter))
    html = get_page_html(get_first_page_url(manga, chapter))
    soup = BeautifulSoup(html)
    page_numbers = get_page_numbers(soup)
    image_urls = []
    for page in page_numbers:
        page_num = page['value']
        image_url = make_image_url(get_image_url(soup), page_num)
        image_urls.append(image_url)
    write_urls_to_file(image_urls, "image_urls.txt")
    os.system("wget -r -nv -i image_urls.txt")
    os.system("mkdir -pv %s/%s" % (manga, chapter))
    os.system("mv media.onemanga.com/*/*/* %s/%s/" % (manga, chapter))
    cbz_path = make_comic_book_archive("%s/%s" % (manga, chapter))
    os.system("rm -rf media.onemanga.com page.html image_urls.txt")
    created = "Created " + cbz_path
    print(created)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Too many or too few arguements.")
        print("USAGE: python omdl.py [MANGA] [CHAPTER]")
        sys.exit(1)
    download_manga_chapter(sys.argv[1], sys.argv[2])
