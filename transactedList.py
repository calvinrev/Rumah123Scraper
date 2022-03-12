import logging, re, time
from datetime import datetime
from bs4 import BeautifulSoup as bs4
from model.rumah123 import Rumah123UpdateAgent

## Setup runtime
runtime = datetime.now().strftime("%Y-%m-%d")
## Setup log & log file
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
fileHandler  = logging.FileHandler(f'log/{runtime}-transactedAdsList.log')
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)


## Scraping Function
def getProperties(response, r123):
    # parse html
    html = bs4(response.text, 'html.parser')
    # get properties link and completion date
    properties = html.find_all("div", {"class":"photo-container"})
    msg = f'-- {response.url:} - {len(properties)} properties found'
    logging.info(msg)
    print(msg)
    for prop in properties:
        url = prop.find("a",href=True)
        r123.item['url']   = url['href']
        # insert data to db
        r123.conn.insertData(r123.item, isTransacted=1)
    # set property listing status
    r123.setListingStat(response=response)
    # loop for next page
    nextPage = html.find("a", string=re.compile(r"Selanjutnya"), href=True)
    if nextPage:
        try:
            response = r123.req(nextPage['href'])
            if response:
                getProperties(response, r123)
        except Exception as e:
            logging.critical(e, exc_info=True)

# Main function
def main():
    # instantiate the rumah123 class
    r123 = Rumah123UpdateAgent()
    # test connection
    res = r123.testConnection(r'https://www.rumah123.com/property-agent-sitemap-index.xml')
    # update agent list
    r123.updateAgents()
    # loop over each province for each sub-category
    for agent in r123.getAgentList()[:3]: #change here to restrict data collection
        for trx in r123.transacted:
            r123.item['agent_url'] = agent["url"]
            r123.item['channel'] = trx.replace('Ter', '')
            r123.item['update_timestamp'] = r123.runtime
            url = f'{agent["url"]}{trx.lower()}'
            try:
                response = r123.req(url=url)
                if response:
                    getProperties(response, r123)
                else:
                    r123.setListingStat(error={'url':url, 'status_code':404})
            except Exception as e:
                logging.critical(e, exc_info=True)
    # close db connection & requests connection 
    r123.conn.closeDb()
    if response:
        r123.closeConn(response)

# Execute main function
if __name__=="__main__":
    start_time = time.time()
    main()
    print("%s minutes elapsed time" % round((time.time() - start_time)/60, 3))