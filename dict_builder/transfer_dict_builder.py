'''
Syntax: dict[fron_stop] = [to_stop,time_sec]
'''
def build_save_footpath_dict(transfser, full_trans):
    import pandas as pd
    from tqdm import tqdm
    print("bulidng footpath dict..")
    transfers_dict={}
    g=transfser.groupby("from_stop_id")
    for from_stop,details in tqdm(g):
        transfers_dict[from_stop]=[]
        for _,row in details.iterrows():
            transfers_dict[from_stop].append((row.to_stop_id,pd.to_timedelta(float(row.min_transfer_time),unit='seconds')))
    import pickle
    if full_trans==1:
        with open('./dict_builder/transfers_dict_full.pkl', 'wb') as pickle_file:
            pickle.dump(transfers_dict,pickle_file)
    else:
        with open('./dict_builder/transfers_dict.pkl', 'wb') as pickle_file:
            pickle.dump(transfers_dict,pickle_file)
    print("transfers_dict done")
    return transfers_dict
