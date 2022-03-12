import logging, re, time
from datetime import datetime
from bs4 import BeautifulSoup as bs4
from model.rumah123 import Rumah123

## Setup runtime
runtime = datetime.now().strftime("%Y-%m-%d")
## Setup log & log file
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
fileHandler  = logging.FileHandler(f'log/{runtime}-activeAdsList.log')
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)
## Setup property-list classes
classList = [
                "ui-atomic-card ui-organisms-card-r123-basic__wrapper",
                "ui-atomic-card ui-organisms-card-r123-featured ui-organisms-card-r123-featured--premier",
                "ui-atomic-card ui-organisms-card-r123-featured ui-organisms-card-r123-featured--featured",
                "ui-atomic-card ui-organisms-card-r123-newlaunch",
                "ui-atomic-card basic-newlaunch ui-organisms-card-r123-newlaunch"
            ]


## Scraping Function
def getProperties(response, r123):
    # parse html
    html = bs4(response.text, 'html.parser')
    # get properties link and completion date
    properties = list()
    for cl in classList:
        newList = html.find_all("div", {"class": cl})
        properties += newList
    msg = f'-- {response.url:} - {len(properties)} properties found'
    logging.info(msg)
    print(msg)
    # loop saving each property
    for prop in properties:
        url = prop.find("a",href=True)
        r123.item['completion_date'] = prop.find("p", string=re.compile(r"Tayang Sejak")).getText()
        r123.item['url']             = f"https://www.rumah123.com{url['href']}"
        #insert data to db
        r123.conn.insertData(r123.item, isTransacted=0) 
    # set property listing status
    r123.setListingStat(response=response)
    # loop for next page
    nextPage = html.find("li",{"class":"ui-molecule-paginate__item--next flex"})
    if nextPage:
        try:
            nextPage = nextPage.find("a",href=True)
            response = r123.req(nextPage['href'])
            if response:
                getProperties(response, r123)
        except Exception as e:
            logging.critical(e, exc_info=True)
  

# Main function
def main():
    # instantiate the rumah123 class
    r123 = Rumah123(runtime)
    # test connection
    r123.testConnection('https://rumah123.com')
    # loop over each province for each sub-category
    for prov in r123.getProvinces()[0:1]: #change here to restrict data collection
        for pType in r123.propertyTypes:
            for ch in r123.channel:
                r123.item['province']         = prov
                r123.item['property_type']    = pType
                r123.item['channel']          = ch
                url = f'https://www.rumah123.com/{ch}/{prov}/{pType}'
                r123.item['update_timestamp'] = r123.runtime
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