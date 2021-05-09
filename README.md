
<!-- README.md is generated from README.Rmd. Please edit that file -->
<!-- Keep this file sync'ed with vignette -->

# Scraper for SEC Form 13F-HR

## Overview

Securities and Exchange Commission (SEC) describes form 13F-HR as
“Quarterly report filed by institutional managers, Holdings”. SEC
requires professional investment managers (who manage over 100MM USD) to
disclose their holdings every quarter by filing Form 13F-HR.

Scraping Form 13F-HR allows us to track holdings of an investment firm,
and sheds some light on the trading pattern if we compare the holdings
to previous quarters. Form 13F-HR does not track derivative exposures
though. There are a few portals that aggregate 13F-HR data, but the SEC
website is fairly easy to scrape since SEC publications are
scraper-friendly. SEC publishers [daily
reports](https://www.sec.gov/Archives/edgar/daily-index/) as well as
[quarterly aggregates](https://www.sec.gov/Archives/edgar/full-index/).

The scrapers in this folder scrape using quarterly index. It is trivial
to adapt the scrapers to scrape using daily index files. Scraping is a
two-step process: First, index file is scraped to build a list of links
to follow. Index file contains a list of filings. Each entry lists the
type of form filed, CIK (central index key) number of the filing firm,
name of the firm, and a relative URL to the filed report. Following
these links lead to text files containing 13F-HR forms (with embedded
XML content containing holdings). Each holding entry has name of stock,
number of stocks held, and their USD value, among other details. Index
file for quarterly aggregates can be big (over 50MB). This file is
downloaded into a local copy to reduce burden on SEC servers and to make
incremental scraping faster.

## Usage

#### Soup

The scraper found in *soup* directory uses BeautifulSoup to parse tags.
Specify year, quarter, and (optionally) number of links (CIKs) to follow
or a list of CIK numbers to include.

``` zsh
python soup/sec13F.py -h

#> usage: sec13F.py [-h] [--year YEAR] [--quarter {1,2,3,4}] [--count COUNT]
#>                  [CIK [CIK ...]]
#> 
#> Scrape Form 13F-HR from SEC website and report current holdings of investment
#> firms
#> 
#> positional arguments:
#>   CIK                   central index key(s) (CIK) to filter, if specified
#>                         (default: None)
#> 
#> optional arguments:
#>   -h, --help            show this help message and exit
#>   --year YEAR, -y YEAR  year when report was filed (default: 2021)
#>   --quarter {1,2,3,4}, -q {1,2,3,4}
#>                         quarter (1-4) of year when report was filed (default:
#>                         1)
#>   --count COUNT, -c COUNT
#>                         maximum number of reports to parse (default: 2)
```

**Scrapers in *scrapy* and *selenium* directories produce the same
output as the one based on *BeautifulSoup*.**

#### Scrapy

    # Usage: scrapy crawl sec13Fspider -a year=<year> -a quarter=<1-4> \
    #          -a n=<integer>  -o file.csv -t csv
    #        (place the spider file, sec13F_spider.py, inside a scrapy project)
    #

#### Selenium

Place the geckodriver executable where $PATH can find it.

``` zsh
python selenium/sec13F.py -h

#> usage: sec13F.py [-h] [--year YEAR] [--quarter {1,2,3,4}] [--count COUNT]
#>                  [CIK [CIK ...]]
#> 
#> Scrape Form 13F-HR from SEC website and report current holdings of investment
#> firms
#> 
#> positional arguments:
#>   CIK                   central index key(s) (CIK) to filter, if specified
#>                         (default: None)
#> 
#> optional arguments:
#>   -h, --help            show this help message and exit
#>   --year YEAR, -y YEAR  year when report was filed (default: 2021)
#>   --quarter {1,2,3,4}, -q {1,2,3,4}
#>                         quarter (1-4) of year when report was filed (default:
#>                         1)
#>   --count COUNT, -c COUNT
#>                         maximum number of reports to parse (default: 2)
```

## Example
