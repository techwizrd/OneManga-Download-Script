#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""Download manga chapters from 'http://onemanga.com'.
"""

import os, sys
from BeautifulSoup import BeautifulSoup

def get_page_soup(url):
    """Download a page and return the HTML."""
    os.system("wget -q %s -O page.html" % url)
    html = ""
    with open("page.html") as html_file:
        for line in html_file:
            html += line
    return BeautifulSoup(html)

def get_first_page_url(manga, chapter):
    """Get the URL of the first page of the manga."""
    soup = get_page_soup("http://onemanga.com/%s/%s/" % (manga, chapter))
    fpage = soup.findAll( 'div', {'id' : 'chapter-cover'})[0].li.a['href']
    return "http://onemanga.com" + fpage

def download_image(url, page_number):
    """Download an image given its URL."""
    os.system("wget -q %s -O %s.jpg" % (url, page_number))

def get_image_url(soup):
    """Get the manga image for the page."""
    return soup.findAll('img', {'class' : 'manga-page'})[0]['src']

def make_image_url(base_url, page_number):
    """Take the base URL and page number and create the image URL."""
    return "%s/%s.jpg" % (os.path.dirname(base_url), page_number)

def get_page_numbers(soup):
    """Get the page numbers for the chapter."""
    select = soup.findAll('select', {'class' : 'page-select'})[0]
    return select.findAll('option')

def get_chapter_numbers(manga):
    """Returns a list of chapters given a manga name."""
    chapters = []
    soup = get_page_soup("http://onemanga.com/%s/" % manga)
    links = soup.findAll('td', {'class' : 'ch-subject'})
    for link in links:
        chapters.append(link.a['href'][2+len(manga):-1])
    return chapters

def write_urls_to_file(urls, filename):
    """Write all urls from urls array to a new text file at filename."""
    with open(filename, 'w') as url_file:
        for url in urls:
            url_file.write(url + "\n")

def make_comic_book_archive(manga, chapter):
    """
    Zip all images in the given directory into a CBZ file and return the
    filename of the created CBZ file.
    """
    dirname = manga + "/" + chapter
    os.system("mkdir -pv " + dirname)
    os.system("mv media.onemanga.com/*/*/* %s/" % dirname)
    os.system("zip -qr %s.cbz %s/* && rm -rf %s" % (dirname, dirname, dirname))
    return os.path.abspath("%s.cbz" % dirname)

def download_manga_chapter(manga, chapter):
    """Download a manga chapter from 'http://onemanga.com'."""
    cbz_path = os.path.abspath("%s/%s.cbz" % (manga, chapter))
    if os.path.exists(cbz_path):
        print("%s already exists." % cbz_path)
    else:
        print("Downloading %s Chapter %s to %s" % (manga, chapter, cbz_path))
        print (get_first_page_url(manga, chapter))
        soup = get_page_soup(get_first_page_url(manga, chapter))
        page_numbers = get_page_numbers(soup)
        image_urls = []
        for page in page_numbers:
            page_num = page['value']
            image_url = make_image_url(get_image_url(soup), page_num)
            image_urls.append(image_url)
        write_urls_to_file(image_urls, "image_urls.txt")
        os.system("wget -r -nv -i image_urls.txt")
        cbz_path = make_comic_book_archive(manga, chapter)
        print("Created " + cbz_path)

def download_manga(manga):
    """Download all chapters of a manga."""
    chapters = get_chapter_numbers(manga)
    for chapter in chapters:
        download_manga_chapter(manga, chapter)

def cleanup():
    """Clean up unneccesary files created during download."""
    os.system("rm -rf media.onemanga.com page.html image_urls.txt")

if __name__ == '__main__':
    if len(sys.argv) == 3:
        download_manga_chapter(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        download_manga(sys.argv[1])
    else:
        print("Too many or too few arguements.")
        print("USAGE: python omdl.py [MANGA] [CHAPTER]")
        print("       python omdl.py [MANGA]")
    cleanup()
