""" This file contains classes used to scrape data from internet.
    Author: Noah Czelusta
"""

from bs4 import BeautifulSoup
import requests


class PriceScraper:

    def __init__(self, url):
        """ set root URL
        """
        self.root_url = url
        self.prod_nums = []

    def get_soup(self, url):
        """ Returns BS object of soup from 'url'
        """
        page = requests.get(url, timeout=5)
        if page.status_code != 200:
            print('HTTP Error Encountered')
            return None
        return BeautifulSoup(page.content, "html.parser")


class NeweggScraper(PriceScraper):

    def __init__(self, url):
        super().__init__(url)

    def get_prod_nums(self, page_limit=1):
        """ Initialize and fill prod_nums with all product numbers.
        """
        for i in range(page_limit):
            soup = self.get_soup(self.root_url_page_q(i+1))
            items = soup.find_all('div', attrs={'class': 'item-container'})
            for item in items:
                link = item.find('a', attrs={'class': 'item-title'})['href']
                # Storing product numbers in a list for now
                num = self.get_prod_num(link)
                if num not in self.prod_nums:
                    self.prod_nums.append(num)

    def root_url_page_q(self, page):
        """ Returns a string that is the root_url with page query
        """
        return self.root_url + '&page={}'.format(page)

    def get_prod_num(self, url):
        """ Given a newegg URL, returns the product number associated
        """
        index = url.find('/p/')
        return url[index+3:]

    def get_prod_url(self, num):
        """ Given a product number, returns the url of the associated product
        """
        return 'https://www.newegg.com/p/' + num

    def get_specs(self, prod_num):
        """ Returns a dictionary of the specs given a product number
            Items:
                String CPU Brand
                Int CPU Series
                Int CPU Gen
                Int RAM Size
                Int HDD
                Int SSD
                String OS
                Float Price
        """
        soup = self.get_soup(self.get_prod_url(prod_num))
        specs = {'vendor': 'Newegg', 'number': prod_num}

        # CPU Type
        specs.update(self.get_cpu(soup))

        # RAM
        specs.update(self.get_ram(soup))

        # Storage
        specs.update(self.get_storage(soup))

        # OS
        specs.update(self.get_os(soup))

        # Price
        specs.update(self.get_price(soup))

        # Graphics
        specs.update(self.get_graphics(soup))

        print('[*] Retrieved specs for item # {}'.format(prod_num))

        return specs

    def get_cpu(self, soup):
        """ Given a soup return cpu brand, series, and generation
        """
        cpu = soup.find(text='CPU Type').parent.nextSibling.string
        brand = series = gen = ''

        # Find brand name
        if cpu.find('Intel') != -1:
            brand = 'Intel'
        else:
            brand = 'AMD'

        # Series
        for char in cpu:
            if char.isnumeric():
                series = int(char)
                break

        # Generation
        for char in cpu[cpu.index(str(series))+1:]:
            if char.isnumeric():
                gen += char
        if gen:
            gen = int(gen)

        return {'cpu_brand': brand, 'cpu_series': series, 'cpu_gen': gen}

    def get_ram(self, soup):
        memcap = soup.find(text='Memory Capacity')
        ram = memcap.parent.nextSibling.string

        return {'ram': int(ram.split()[0])}

    def get_storage(self, soup):
        """ Return dictionary of hdd and ssd size in GB's
        """
        memcap = soup.find(text='Memory Capacity')
        table = memcap.findParent('table').nextSibling
        storage = {}

        # HDD
        hdd = table.find(text='HDD')
        if hdd:
            hdd_size = hdd.parent.nextSibling.string
            hdd_size = hdd_size.split()
            if hdd_size[0].isnumeric():
                if hdd_size[1].find('GB') == -1:
                    multiplier = 1000
                else:
                    multiplier = 1
                storage['hdd'] = int(hdd_size[0]) * multiplier
            else:
                storage['hdd'] = 0
        else:
            storage['hdd'] = 0

        # SSD
        ssd = table.find(text='SSD')
        if ssd:
            ssd_size = ssd.parent.nextSibling.string
            ssd_size = ssd_size.split()
            if ssd_size[0].isnumeric():
                if ssd_size[1].find('GB') == -1:
                    multiplier = 1000
                else:
                    multiplier = 1
                storage['ssd'] = int(ssd_size[0]) * multiplier
            else:
                storage['ssd'] = 0
        else:
            storage['ssd'] = 0

        return storage

    def get_graphics(self, soup):
        """ Integrated graphics or special card
        """
        gpu = soup.find(text='GPU/VGA Type').parent.nextSibling.string
        if gpu.lower().find('vega') != -1 or gpu.lower().find('intel') != -1:
            return {'graphics': 'Integrated'}
        else:
            return {'graphics': gpu}

    def get_os(self, soup):
        """ Return dictionary of string of OS
        """
        quick_info = soup.find(text='Quick Info').parent.nextSibling  # tbody
        os = quick_info.find(text='Operating System').parent.nextSibling.string
        return {'os': os}

    def get_price(self, soup):
        """ Return dictionary of price
        """
        current_price = soup.find('li', attrs={'class': 'price-current'})
        price = current_price.strong.string  # before decimal
        price += current_price.sup.string    # after decimal

        return {'price': float(price.replace(',', ''))}

    def dict_to_tuple(self, specs):
        """ Returns a tuple of the dictionary in the format for sqlite add row
        """
        data = []
        data.append(specs['vendor'])
        data.append(specs['number'])
        data.append(specs['cpu_brand'])
        data.append(specs['cpu_series'])
        data.append(specs['cpu_gen'])
        data.append(specs['ram'])
        data.append(specs['hdd'])
        data.append(specs['ssd'])
        data.append(specs['graphics'])
        data.append(specs['os'])
        data.append(specs['price'])
        return tuple(data)
