import scrapy
from pathlib import Path

# Usage: scrapy crawl sec13Fspyder -a year=2021 -a quarter=QTR1 -o file.csv -t csv
#
class SEC_13F_Spider(scrapy.Spider):
    name = "sec13Fspider"

    def __init__(self, year=2021, quarter='QTR1', n=3, **kwargs):
        self.url_base = 'https://www.sec.gov/Archives'
        self.n = n
        self.index = list()
        # check if index file is cached locally
        self.fname = f'{Path.cwd()}/index_{year}_{quarter}.txt'
        if Path(self.fname).is_file():
            self.start_urls = [f'file://{self.fname}']
        else:
            self.start_urls \
                    = [f'{url_base}/edgar/full-index/{year}/{quarter}/form.idx']
        super().__init__(**kwargs)

    def parse(self, response):
        if not Path(self.fname).is_file(): 
            with open(self.fname, "wb") as f: # cache index file
                f.write(response.body)

        with open(self.fname, "rb") as f:
            for line in f.read().decode('utf-8').split('\n'):
                if '13F-HR' in line:
                    words = line.split()
                    url = words[-1]
                    cik = words[-3]
                    name = ' '.join(words[1:len(words)-3])
                    self.index.append((cik, name, url))

        for it in self.index:
            if not self.n >= 0:
                break
            self.n -= 1
            self.cik, self.name, url = it
            url = f'{self.url_base}/{url}'
            yield scrapy.Request(url, callback=self.parse_cik)

    def parse_cik(self, response):
        for item in response.xpath('//infotable'):
            yield {
                    'cik' : self.cik,
                    'name' : self.name,
                    'cusip' : item.xpath('cusip/text()').get(),
                    'issuer' : item.xpath('nameofissuer/text()').get(),
                    'value' : item.xpath('value/text()').get(),
                    'quantity' : item.xpath('shrsorprnamt/sshprnamt/text()').get(),
                    'type' : item.xpath('shrsorprnamt/sshprnamttype/text()').get()
                    }
