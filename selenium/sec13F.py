#!/usr/bin/env python

# Usage: PATH=$PATH:. python sec13F.py
#   (assuming geckodriver is in current dir)

from selenium import webdriver, common
from pathlib import Path
from bs4 import BeautifulSoup

def main(year, quarter, n):
    """Scrape 13F-HR reports from SEC website

    :year: TODO
    :quarter: TODO
    :n: TODO
    :returns: TODO

    """

    url_base = r"https://www.sec.gov/Archives"

    def get_index():
        fname = f'index_{year}_{quarter}.txt'
        if not Path(fname).is_file():
            # download index file (it is huge)
            fp = webdriver.FirefoxProfile()
            fp.set_preference("browser.download.folderList",2)
            fp.set_preference("browser.download.manager.showWhenStarting",False)
            fp.set_preference("browser.download.dir", str(Path.cwd()))
            fp.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                    "application/octet-stream")
            options = webdriver.firefox.options.Options()
            options.headless = True
            browser = webdriver.Firefox(firefox_profile=fp, options=options)
            url = f'{url_base}/edgar/full-index/{year}/{quarter}/form.idx'
            # Browser does not get load successful event after downloading
            #   file. Set a timeout and loop until successful.
            browser.set_page_load_timeout(5)
            max_attempts = 5
            for attempts in range(max_attempts):
                try:
                    browser.get(url)
                    break
                except common.exceptions.TimeoutException:
                    if Path('form.idx').is_file():
                        break
            browser.quit() 
            if attempts == (max_attempts - 1):
                raise Exception('Failed to save index file')

            if Path('form.idx').is_file():
                Path('form.idx').replace(Path(fname))
        
        if not Path(fname).is_file():
            raise Exception('Failed to save index file')

        # read index file and return a generator
        with open(fname, "rb") as f:
            for line in f.read().decode('utf-8').split('\n'):
                if '13F-HR' in line:
                    words = line.split()
                    url = words[-1]
                    cik = words[-3]
                    name = ' '.join(words[1:len(words)-3])
                    yield (cik, name, url)

    print('cik,name,cusip,issuer,value,quantity,type')
    options = webdriver.firefox.options.Options()
    options.headless = True
    browser = webdriver.Firefox(options = options)
    for cik, name, url in get_index():
        if n is not None:
            if n > 0:
                n -= 1
            else:
                break
        url = f'{url_base}/{url}'
        browser.get(url)
        # our link points to a text file. firefox puts the text inside <pre> so 
        #   we have a proper html document
        content = browser.find_element_by_tag_name('pre').text
        # parse extracted text as xml
        soup = BeautifulSoup(content, 'lxml')
        items = soup.find_all('infotable')
        for it in items:
            print(cik, name,
                    it.cusip.string, 
                    it.nameofissuer.string, 
                    it.value.string,
                    it.shrsorprnamt.sshprnamt.string,
                    it.shrsorprnamt.sshprnamttype.string, sep=',')
    browser.quit()

if __name__ == "__main__":
    year = 2021
    quarter = 'QTR1'
    n = 2
    main(year, quarter, n)
