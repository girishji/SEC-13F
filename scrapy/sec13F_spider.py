import scrapy
from pathlib import Path

# Usage: scrapy crawl sec13Fspider -a year=<year> -a quarter=<1-4> \
#          -a n=<integer>  -o file.csv -t csv
#        (place this file inside a scrapy project)
#
class SEC_13F_Spider(scrapy.Spider):
    name = "sec13Fspider"

    def __init__(self, year=2021, quarter=1, n=2, **kwargs):
        self.url_base = 'https://www.sec.gov/Archives'
        self.n = n
        # check if index file is cached locally
        self.fname = f'{Path.cwd()}/index_{year}_QTR{quarter}.txt'
        if Path(self.fname).is_file():
            self.start_urls = [f'file://{self.fname}']
        else:
            self.start_urls \
                    = [f'{self.url_base}/edgar/full-index/{year}/QTR{quarter}/form.idx']
        super().__init__(**kwargs)

    def parse(self, response):
        """Parse the main index file that contains links to 13F filings"""
        if not Path(self.fname).is_file(): 
            with open(self.fname, "wb") as f: # cache index file
                f.write(response.body)
        with open(self.fname, "rb") as f:
            for line in f.read().decode('utf-8').split('\n'):
                if '13F-HR' in line:
                    if self.n <= 0:
                        break
                    self.n -= 1
                    words = line.split()
                    url = f'{self.url_base}/{words[-1]}'
                    yield scrapy.Request(url, callback=self.parse_cik)

    def parse_cik(self, response):
        """Parse a 13F-HR filing (in xml format)"""
        cik = response.xpath('//credentials/cik/text()').get().strip('"')
        name = response.xpath('//filingmanager/name/text()').get()
        for item in response.xpath('//infotable'):
            yield {
                    'cik' : cik,
                    'name' : name,
                    'cusip' : item.xpath('cusip/text()').get(),
                    'issuer' : item.xpath('nameofissuer/text()').get(),
                    'value' : item.xpath('value/text()').get(),
                    'quantity' : item.xpath('shrsorprnamt/sshprnamt/text()').get(),
                    'type' : item.xpath('shrsorprnamt/sshprnamttype/text()').get()
                    }
