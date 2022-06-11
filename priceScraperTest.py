from Scrapers import NeweggScraper
from Database import Database

url = 'https://www.newegg.com/p/pl?N=100019096'

scraper = NeweggScraper(url)

db = Database('test.db')
db.delete('Desktops')
scraper.get_prod_nums(page_limit=10)

print('Getting specs for {} items.'.format(len(scraper.prod_nums)))

for item in scraper.prod_nums:
    try:
        db.add_row('Desktops', scraper.dict_to_tuple(scraper.get_specs(item)))
    except BaseException as e:
        print('Could not get specs for {} : {}'.format(item, e))

db.exit()
