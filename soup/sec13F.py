#!/usr/bin/env python

from pathlib import Path
from bs4 import BeautifulSoup
import urllib
import requests

def main(year, qtr, n):

    # header for SEC 
    headers = {'user-agent': 'soup_girish/0.0.1'}

    url_base = r"https://www.sec.gov/Archives"

    def get_index():
        """Index of 13-HR reports filed during a quarter

        :year: year filed
        :qtr: quarter of year (QTR1, ...)
        :returns: list of company name, CIK, and url to 13F-HR report
        """
        fname = f'index_{year}_{qtr}.txt'
        if not Path(fname).is_file():
            url = f'{url_base}/edgar/full-index/{year}/{qtr}/form.idx')
            content = requests.get(url, headers=headers).content
            # read only once, and cache data (this is a huge file)
            with open(fname, "wb") as f:
                f.write(content)
        with open(fname, "rb") as f:
            for line in f.read().decode('utf-8').split('\n'):
                if '13F-HR' in line:
                    words = line.split()
                    url = words[-1]
                    cik = words[-3]
                    name = ' '.join(words[1:len(words)-3])
                    yield (cik, name, url)

    # write csv formatted output to stdout
    print('cik,name,cusip,issuer,value,quantity,type')

    for cik, name, url = get_index():
        if n is not None:
            if n > 0:
                n -= 1
            else:
                break

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

if __name__ == "__main__":
    main("2021", "QTR1", 3)
