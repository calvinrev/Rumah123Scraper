import time
import pandas as pd
import numpy as np
from model.rumah123 import Rumah123FormatData


def getData(f123):
    ## Get data
    dset = f123.conn.readData({'update_timestamp':f123.runtime}, visited=1, multiple=True)
    ## Transform to pandas dataframe
    dset = pd.DataFrame(dset)
    print(f'> Data Shape: {dset.shape[0]} rows {dset.shape[1]} columns')
    return dset    

def main():
    ## Instantiate the Rumah123FormatData class
    f123 = Rumah123FormatData()
    ## change the date by uncomment day variable below, if not the default date will be set today
    # f123.runtime = '2022-03-10'

    # Get dataset
    ds = getData(f123)
    if not ds.empty:
        ## Preprocess and Reformat data
        ds['completion_date'] = ds.completion_date.apply(lambda r: f123.formatDate(r) if r is not None else None)
        ds['regency'] = ds.regency.apply(f123.formatRegency)
        ds['subdistrict'] = ds.subdistrict.apply(f123.formatSubdistrict)
        ds['title'] = ds.title.apply(f123.formatTitle)
        ds['built_up'] = ds.built_up.apply(f123.formatInt)
        ds['land_area'] = ds.land_area.apply(f123.formatInt)
        ds['bedroom'] = ds.bedroom.apply(f123.formatInt)
        ds['bathroom'] = ds.bathroom.apply(f123.formatInt)
        ds['floor'] = ds.floor.apply(f123.formatInt)
        price = ds.price.apply(f123.formatPrice)
        ds['price'] = [i[0] for i in price]
        ds['price_unit'] = [i[1] for i in price]
        agent = ds.agent_url.apply(f123.formatAgent)
        ds['agent_id'] = [i[0] for i in agent]
        ds['agent_name'] = [i[1] for i in agent]
        ds['agency'] = [i[2] for i in agent]

        ## Change nan cell to Null 
        # ds.fillna('', inplace=True)
        ds = ds.replace({np.nan:None})

        ## Insert into main database
        for row in ds.to_dict(orient='records'):
            f123.conn.insertMainData(row)
        f123.conn.closeDb()
        print(f'> {len(ds)} data records have been preprocessed and inserted into main database!')
    else:
        print('No more data to be preprocessed!')

# Execute main function
if __name__=="__main__":
    start_time = time.time()
    main()
    print("> %s minutes elapsed time" % round((time.time() - start_time)/60, 3))