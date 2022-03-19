import requests
import pandas as pd
import json, time, logging
from datetime import datetime
from bs4 import BeautifulSoup as bs4
from model.pipeline import dbConnection
from os import path

class Rumah123():
    ## Setup Attributes
    item = dict()
    def __init__(self, runtime=datetime.now().strftime("%Y-%m-%d"), tableName='rumah123temp'):
        self.header   = {
                           "User-Agent"   : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
                           "Content-Type" : "application/json"
                        }
        self.cookies  = {}
        self.typeCode = {
                            'ho': 'rumah',
                            'ap': 'apartemen',
                            'sh': 'ruko',
                            'la': 'tanah',
                            'fa': 'pabrik',
                            'of': 'kantor',
                            'wa': 'gudang',
                            'cs': 'ruang-usaha'
                        }
        self.propertyTypes = ["rumah", "apartemen", "ruko", "tanah", "pabrik", "kantor", "gudang", "ruang-usaha"]
        self.channel       = ["jual", "sewa"]
        self.transacted    = ["Terjual","Tersewa"]
        self.filePath      = ['data/listingStatus.json', 'data/list/agentlist.json']
        self.runtime       = runtime
        self.tableName     = tableName
        self.conn          = dbConnection(self.tableName)

    ## General Functions
    # Get province list
    def getProvinces(self):
        provList = json.loads(open('data/list/provlist.json', "r").read())
        provList = [prov['prov'] for prov in provList]
        return provList

    def getKabkot(self):
        kabkot = json.loads(open('data/list/kabkotlist.json', "r").read())
        kabkotList = dict()
        for i in kabkot:
            kabkotList[i['kabkot']]=i['provinsi']
        return kabkotList

    # Test connection
    def testConnection(self, url):
        session  = requests.Session()
        response = session.get(url, headers=self.header)
        print(f"Connection Status:{response.status_code} \nCookies={session.cookies.get_dict()}")
        return response

    # Session management
    def setSession(self, session):
        self.cookies['_csrf'] = session.cookies.get_dict()['_csrf']
        
    def renewSession(self, session):
        self.closeConn(session)
        self.cookies.pop('_csrf')

    # Requests a page
    def req(self, url, session=False, trial=1):
        # Make a page request
        try:
            if not self.cookies.get('_csrf'):
                sess     = requests.Session()
                response = sess.get(url, headers=self.header, stream=True, timeout=60)
                cookies  = response.cookies.get_dict()
                if not cookies.get('PHPSESSID'):
                    self.setSession(sess)
            else:
                response = requests.get(url, headers=self.header, cookies=self.cookies, stream=True, timeout=300)
        except Exception as e:
            logging.critical(e, exc_info=True)
        time.sleep(1.2)
        # Connection error management
        if response: 
            if trial<3:
                if response.status_code==404:
                    logging.warning(f'{response.status_code}: {response.url}')
                    self.req(url, session, trial=trial+1)
                elif response.status_code==429 | response.status_code==403:
                    time.sleep(60)
                    logging.warning(f'{response.status_code}: {response.url}')
                    self.renewSession(response)
                    self.req(url, session, trial=trial+1)
            # return
            if session:
                return response, response.cookies.get_dict()
            else:
                return response
        # None response management
        else:
            if trial<3:
                self.req(url, session, trial=trial+1)
            else:
                return None

    # Close requests connection
    def closeConn(self, session):
        session.close()
    
    ## Active Ads Functions
    # Set scraping property listing status
    def setListingStat(self, response=None, error=None):
        if path.exists(self.filePath[0]):
            with open(self.filePath[0]) as f:
                jsonFile = json.load(f)
        else:
            jsonFile = list()
        if response:
            record = {'update_timestamp':self.runtime, 'url':response.url, 'status':response.status_code}
        elif error:
            record = {'update_timestamp':self.runtime, 'url':error['url'], 'status':error['status_code']}
        if record not in jsonFile:
            jsonFile.append(record)
        with open(self.filePath[0], 'w') as f:
            json.dump(jsonFile, f)
        f.close()

    # Read scraping property listing status
    def readListingStat(self, runtime=None):
        try:
            jsonFile = json.loads(open(self.filePath[0], "r").read())
        except Exception as e:
            logging.critical(e, exc_info=True)
        if runtime:
            jsonFile = list(filter(lambda r: r['update_timestamp'] == runtime, jsonFile))
        return jsonFile

    # Update scraping property listing status
    def updateListingStat(self, response, runtime=None):
        jsonFile = readListingStat(runtime)
        for row in jsonFile:
            if row['url']==response.url:
                row['status'] = response.status_code
        with open(self.filePath[0], 'w') as f:
            json.dump(jsonFile, f)
        f.close()

    ## Transacted Ads Functions
    # Get agent list
    def getAgentList(self):
        try:
            jsonFile = json.loads(open(self.filePath[1], "r").read())
            return jsonFile
        except Exception as e:
            logging.critical(e, exc_info=True)


class Rumah123UpdateAgent(Rumah123):
    # Init the child class of Rumah123
    def __init__(self):
        super().__init__()
        self.url = r'https://www.rumah123.com/property-agent-sitemap-index.xml'
    
    def saveAgents(self, agentList):
        agentList = pd.DataFrame(agentList, columns=['url', 'lastmod'])
        agentList.to_json(self.filePath[1], orient='records')
        del agentList

    def updateAgents(self):
        msg = "Updating agent list from sitemap..."
        logging.info(msg)
        print(msg)
        # request sitemap page
        try:
            response = self.req(self.url)    
            page = bs4(response.text, 'html.parser')
            loc = page.find_all("loc")
            loc = list(l.getText() for l in loc)
            lastmod = page.find_all("lastmod")
            lastmod = list(l.getText() for l in lastmod)
            agenList = list(zip(loc,lastmod))
            agenList = agenList[0::2] #filter indonesia url version only (odd index)
            print(len(agenList), 'agents found!')
            self.saveAgents(agenList)
        except Exception as e:
            logging.critical(e, exc_info=True)
            print('Unable to update list agent! using the latest data...')


class Rumah123FormatData(Rumah123):
    # Init the child class of Rumah123
    def __init__(self):
        super().__init__()

    ## Setup Attributes
    bulan = {
        'Januari': '01',
        'Februari': '02',
        'Maret': '03',
        'April': '04',
        'Mei': '05',
        'Juni': '06',
        'Juli': '07',
        'Agustus': '08',
        'September': '09',
        'Oktober': '10',
        'November': '11',
        'Desember': '12',
    }
    price = {
        'Total':1,
        'Ratus': 100,
        'Ribu' : 1000,
        'Juta' : 1000000,
        'Juta Total' : 1000000,
        'Miliar': 1000000000,
        'Miliar Total': 1000000000,
        'Triliun': 1000000000000,
        'Triliun Total': 1000000000000,
    }
    intEx = ['LB : ', 'LT : ',' m²']

    ## Preprocessing Functions
    def formatDate(self, s):
        s = s.replace(',','').replace('Tayang Sejak ','')
        tgl, bln, thn = s.split(' ')
        return f'{thn}-{self.bulan[bln]}-{tgl}'

    def formatPrice(self, s):
        if s:
            s = s.replace('Rp ','').replace(',','.')
            pList = s.split()
            x = float(pList[0])
            y = self.price[pList[1]]
            if len(pList) > 2:
                z = ' '.join(pList[2:])
            else:
                z = None
            return [int(x*y), z]
        else:
            return None

    def formatInt(self, s):
        if s is not None:
            if isinstance(s, str):
                if '-' in s:
                    return None
                else:
                    for ex in self.intEx:
                        s = s.replace(ex,'')
                    # s = float(s)
                    return int(s)
            elif isinstance(s, float):
                return None
        else: 
            pass

    def formatRegency(self, s):
        if s == 'solo':
            return 'surakarta'
        elif s == 'kabupaten-kudus':
            return 'kudus'
        elif s == 'cikarang':
            return 'bekasi'
        elif s == 'semapura':
            return 'klungkung'
        elif s == 'cikampek':
            return 'karawang'
        elif s == 'purwokerto':
            return 'banyumas'
        else :
            return s

    def formatSubdistrict(self, s):
        if s:
            return s.split(',')[0]
        else:
            return None

    def formatTitle(self, s):
        if s:
            s = (s.split(' - ')[0]).strip()
            s = s.replace("'","").replace('"','')
            return s
        else:
            return None

    def formatAgent(self, s):
        name = s.split('/')[5].split('-')
        agentId   = name[-1]
        agentName = ' '.join(name[:-1])
        agency    = s.split('/')[4].replace('-',' ')
        return agentId, agentName, agency