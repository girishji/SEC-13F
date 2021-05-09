#!/usr/bin/env python

# Usage: PATH=$PATH:. python sec13F.py
#   (assuming geckodriver is in current dir)

from selenium import webdriver, common
from pathlib import Path
from bs4 import BeautifulSoup
import argparse

def main(year, quarter, n, *args):
    """Scrape 13F-HR reports from SEC website

    :year: year of filing
    :quarter: quarter of the year of filing
    :n: maximum count of links to follow
    :args: 0 or more CIK numbers of investment firms
    :returns: csv of CIK number of firm, name of firm, stock id, stock name,
                quantity held, value in USD, and type of stock
    """

    url_base = r"https://www.sec.gov/Archives"
    filing_index_file = f'index_{year}_{quarter}.txt'

    def filing_index():
        """Download index file only once (it can be huge)"""
        if not Path(filing_index_file).is_file():
            # setup the headless browser to download file without prompt
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
            # Browser can hang if it does not recieve load-successful event
            #   after downloading file. Set a timeout and loop until successful.
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
            if Path('form.idx').is_file():
                Path('form.idx').replace(Path(filing_index_file))
            else:
                raise Exception('Failed to save index file')
        
    def get_links():
        """Read index file and return a generator to links"""
        with open(filing_index_file, "rb") as f:
            for line in f.read().decode('utf-8').split('\n'):
                if '13F-HR' in line:
                    words = line.split()
                    url = words[-1]
                    cik = words[-3]
                    name = ' '.join(words[1:len(words)-3])
                    yield (cik, name, url)


    # Follow the links and print results
    filing_index()
    print('cik,name,cusip,issuer,value,quantity,type')
    options = webdriver.firefox.options.Options()
    options.headless = True
    browser = webdriver.Firefox(options = options)
    for cik, name, url in get_links():
        if args:
            if int(cik) not in args:
                continue
        else:
            if n is not None:
                if n > 0:
                    n -= 1
                else:
                    break
        if args and int(cik) not in args:
            continue
        url = f'{url_base}/{url}'
        browser.get(url)
        # Our link points to a text file. Selenium cannot parse mangled text
        #   as xml. However, Firefox puts the text inside <pre> so 
        #   we have a proper html document. Isolate xml text.
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


def get_parser():
    """Parser to parse command line args"""
    parser = argparse.ArgumentParser(
            description="Scrape Form 13F-HR from SEC website and report"
            + " current holdings of investment firms",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
            )
    parser.add_argument("--year", "-y", type=int, default=2021,
            help="year when report was filed")
    parser.add_argument("--quarter", "-q", type=int, default=1,
            choices=[1, 2, 3, 4],
            help="quarter (1-4) of year when report was filed")
    parser.add_argument("--count", "-c", type=int, default=2,
            help="maximum number of reports to parse")
    parser.add_argument('ciks', metavar='CIK', type=int, nargs='*',
            help='central index key(s) (CIK) to filter, if specified')
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args.year, args.quarter, args.count, *args.ciks)
