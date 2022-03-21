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
fileHandler  = logging.FileHandler(f'log/{runtime}-transactedAdsDetails.log')
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

## Scraping Function
def getDetails(response, r123, kabkot):
    html = bs4(response.text, 'html.parser')
    url  = response.url
    r123.item['property_id']  = url.split('/')[5]
    r123.item['property_type']= r123.typeCode[r123.item['property_id'][:2]]

    regency = url.split('/')[4]
    r123.item['province']     = kabkot[regency]
    r123.item['regency']      = regency
    r123.item['subdistrict']  = html.find("div", {'class':'r123-listing-summary-v2__address'}).getText()
    title = html.find('title').getText()
    r123.item['title']       = (title.strip()).replace(':','')
    r123.item['built_up']    = html.find("span", string=re.compile(r"LB : ")).getText()
    r123.item['land_area']   = html.find("span", string=re.compile(r"LT : ")).getText()
    bedroom = html.find("i", {'class':'rui-icon ui-atomic-icon rui-icon-bed-small'})
    if bedroom:
        try:
            r123.item['bedroom'] = bedroom.find_next_sibling("span").getText()
        except:
            r123.item['bedroom']= None    
    else:
        r123.item['bedroom']= None
    bathroom = html.find("i", {'class':'rui-icon ui-atomic-icon rui-icon-bath-small'})
    if bathroom:
        try:
            r123.item['bathroom'] = bathroom.find_next_sibling("span").getText()
        except:
                r123.item['bathroom']= None
    r123.item['furnishing']  = (html.find("p", string=re.compile(r"Dilengkapi Perabotan"))).find_next_sibling("p").getText()
    r123.item['condition']   = (html.find("p", string=re.compile(r"Kondisi Properti"))).find_next_sibling("p").getText()
    r123.item['floor']       = (html.find("p", string=re.compile(r"Jumlah Lantai"))).find_next_sibling("p").getText()
    r123.item['certificate'] = (html.find("p", string=re.compile(r"Sertifikat"))).find_next_sibling("p").getText()
    r123.item['electricity'] = (html.find("p", string=re.compile(r"Daya Listrik"))).find_next_sibling("p").getText()
    r123.item['price']       = (html.find("div", {'class':'r123-listing-summary-v2__price'}).find("span")).getText()
    r123.item['price_unit']  = None
    r123.item['transacted']  = html.find("div", {'class':'r123-listing-summary-v2__badge r123-listing-summary-v2__badge--red'}).getText()
    r123.item['agent_id']    = None
    r123.item['agent_name']  = None
    r123.item['agency']      = None
    r123.item['completion_date'] = None
    # # update to database
    r123.conn.updateData(r123.item)

# Main function
def main(date=None):
    # instantiate the rumah123 class
    r123 = Rumah123(runtime)
    # set date for db query --> format: YYYY-MM-DD
    date = date if date else r123.conn.latestDate()
    # test connection
    r123.testConnection('https://rumah123.com')
    # get kabkot list
    kabkot = r123.getKabkot()
    # load property dataset to visit
    dataset = r123.conn.readData({'update_timestamp':date, 'transacted':1}, visited=0, multiple=True)
    for i, row in enumerate(dataset, start=1):
        try:
            r123.item = row
            response = r123.req(r123.item['url'])
            if response:
                getDetails(response, r123, kabkot)
            # show progress
            print(f"Progress: {round(i/len(dataset)*100,2)}% ({i}/{len(dataset)})")
            if i%25==0:
                time.sleep(3)
                if i%100==0 and response:
                    logging.info(f'-- {i} - {response.url} : {response.status_code}')
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