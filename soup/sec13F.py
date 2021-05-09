#!/usr/bin/env python

# Usage: python sec13F.py -h

from pathlib import Path
from bs4 import BeautifulSoup
import urllib
import requests
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
    # header for SEC 
    headers = {'user-agent': 'soup_girish/0.0.1'}

    # index file contains links to 13F filings by investment firms
    index_file = f'index_{year}_QTR{quarter}.txt'

    def filing_index():
        """Download file containing index of 13-HR's filed during a quarter"""
        if not Path(index_file).is_file():
            url = f'{url_base}/edgar/full-index/{year}/QTR{quarter}/form.idx'
            content = requests.get(url, headers=headers).content
            # cache data in a file (this can be a huge file)
            with open(index_file, "wb") as f:
                f.write(content)

    def get_links():
        """Read index file and return a generator to links"""
        with open(index_file, "rb") as f:
            for line in f.read().decode('utf-8').split('\n'):
                if '13F-HR' in line:
                    words = line.split()
                    url = words[-1]
                    cik = words[-3]
                    name = ' '.join(words[1:len(words)-3])
                    yield (cik, name, url)


    # write csv formatted output to stdout
    print('cik,name,cusip,issuer,value,quantity,type')
    for cik, name, url in get_links():
        if n is not None:
            if n > 0:
                n -= 1
            else:
                break
        if args and int(cik) not in args:
            continue
        url = f'{url_base}/{url}'
        content = requests.get(url, headers=headers).content
        soup = BeautifulSoup(content, 'lxml')
        items = soup.find_all('infotable')
        for it in items:
            print(cik, name,
                    it.cusip.string, 
                    it.nameofissuer.string, 
                    it.value.string,
                    it.shrsorprnamt.sshprnamt.string,
                    it.shrsorprnamt.sshprnamttype.string, sep=',')

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
