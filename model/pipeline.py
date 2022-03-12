import pymysql
import json
import ast

class dbConnection():
    ## Setup Connection
    __host = 'localhost'
    __db   = 'scraper'
    __user = 'root'
    __pass = ''
    def __init__(self, tableName):
        self.connect = pymysql.connect(
            host        = dbConnection.__host,
            db          = dbConnection.__db,
            user        = dbConnection.__user,
            passwd      = dbConnection.__pass,
            charset     = 'utf8',
            use_unicode = True
        )
        self.cursor     = self.connect.cursor()
        self.tableName  = tableName

    
    ## General Functions
    def showColumns(self):
        self.cursor.execute( f"SHOW COLUMNS FROM {self.tableName}" )
        columns = []
        for c in self.cursor.fetchall():
            columns.append(c[0])
        return columns

    def latestDate(self):
        self.cursor.execute( f'SELECT max(update_timestamp) FROM {self.tableName}' )
        date = self.cursor.fetchone()[0]
        return date.strftime("%Y-%m-%d")

    def closeDb(self):
        self.connect.close()

    ## Rumah123temp DB Functions
    def insertData(self, item, isTransacted):
        self.cursor.execute( f'INSERT INTO rumah123temp (url, update_timestamp, response, transacted, visited) VALUE ("{item["url"]}", "{item["update_timestamp"]}", "{item}", {isTransacted}, 0)' )
        self.connect.commit()

    def updateStatus(self, item):
        self.cursor.execute( f'SELECT visited FROM rumah123temp WHERE update_timestamp="{item["update_timestamp"]}" AND url="{item["url"]}"' )
        query  = self.cursor.fetchone()
        visited = query[0]
        self.cursor.execute( f'UPDATE rumah123temp SET visited="{visited+1}" WHERE url="{item["url"]}" AND update_timestamp="{item["update_timestamp"]}"' )
        self.connect.commit()

    def updateData(self, item):
        self.cursor.execute( f'UPDATE rumah123temp SET response="{item}" WHERE url="{item["url"]}" AND update_timestamp="{item["update_timestamp"]}"' )
        self.connect.commit()
        self.updateStatus(item)

    def readData(self, item, visited=None, multiple=False):
        if multiple:
            if visited:
                if item.get('transacted')==0 or item.get('transacted')==1:
                    self.cursor.execute( f'SELECT response FROM rumah123temp WHERE update_timestamp="{item["update_timestamp"]}" AND visited = {visited} AND transacted="{item["transacted"]}"' )
                else:
                    self.cursor.execute( f'SELECT response FROM rumah123temp WHERE update_timestamp="{item["update_timestamp"]}" AND visited = {visited}' )
            else:
                if 'transacted' in item:
                    self.cursor.execute( f'SELECT response FROM rumah123temp WHERE update_timestamp="{item["update_timestamp"]}" AND transacted="{item["transacted"]}"' )
                else:
                    self.cursor.execute( f'SELECT response FROM rumah123temp WHERE update_timestamp="{item["update_timestamp"]}"' )
            query  = self.cursor.fetchall()
            record = list()
            for i in query:
                record.append(ast.literal_eval(i[0]))
        else:
            self.cursor.execute( f'SELECT response FROM rumah123temp WHERE update_timestamp="{item["update_timestamp"]}" AND url="{item["url"]}"' )
            query = self.cursor.fetchone()
            record = ast.literal_eval(query[0])
        return record


    ## Rumah123 (main) DB Functions
    def insertMainData(self, item):
        self.cursor.execute( 
            "insert into rumah123 (channel, property_id, property_type, province, regency, subdistrict, title, built_up, land_area, bedroom, bathroom, furnishing, conditions, floor, certificate, electricity, completion_date, price, price_unit, transacted, agent_id, agent_name, agency, url, agent_url, update_timestamp) value(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (  item['channel'],
                   item['property_id'],
                   item['property_type'],
                   item['province'],
                   item['regency'],
                   item['subdistrict'],
                   item['title'],
                   item['built_up'],
                   item['land_area'],
                   item['bedroom'],
                   item['bathroom'],
                   item['furnishing'],
                   item['condition'],
                   item['floor'],
                   item['certificate'],
                   item['electricity'],
                   item['completion_date'],
                   item['price'],
                   item['price_unit'],
                   item['transacted'],
                   item['agent_id'],
                   item['agent_name'],
                   item['agency'],
                   item['url'],
                   item['agent_url'],
                   item['update_timestamp']
                 ) 
        )            
        self.connect.commit()
        # update status
        self.updateStatus(item)

    def readMainData(self, time=None):
        if time:
            self.cursor.execute( f'SELECT * FROM rumah123 WHERE update_timestamp="{time}"' )   
        else:
            self.cursor.execute( f'SELECT * FROM rumah123' )   
        return self.cursor.fetchall()