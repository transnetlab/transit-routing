from tqdm import tqdm
import pandas as pd


def remove_Uturns(stoptimes_dict):
    print("Running Algorithm 2")
    Transfer_set = pd.read_csv(r"./dict_builder/Transfer_set.csv")
    i_len= len(Transfer_set)
    uturn_index = []
#    temp = Transfer_set[Transfer_set.from_Trip=='4741_1']
    Transfer_set.from_Trip = Transfer_set.from_Trip.str.split("_")
    Transfer_set.to_trip = Transfer_set.to_trip.str.split("_")
    for _, trans in tqdm(Transfer_set.iterrows()):
        try:
            tuple1 = stoptimes_dict[int(trans.from_Trip[0])][int(trans.from_Trip[1])][trans.from_stop_index- 1]
            tuple2 = stoptimes_dict[int(trans.to_trip[0])][int(trans.to_trip[1])][trans.to_stop_index + 1]
            if tuple1[0] == tuple2[0] and tuple1[1] + pd.to_timedelta(10, unit="seconds") <= tuple2[1]:
                uturn_index.append(trans.name)
#                print(f"found u turn at index {trans.name}")
        except IndexError:
            pass
    if uturn_index!=[]:
        Transfer_set = Transfer_set.drop(uturn_index).reset_index(drop=True)

    print(f"1st step reduced {int(((len(Transfer_set)-i_len)/i_len)*100)}% transfers")

    Transfer_set.from_Trip = Transfer_set.from_Trip.str.join("_")
    Transfer_set.to_trip = Transfer_set.to_trip.str.join("_")
    ########Save as a dict
    trip_transfer_dict = {}
    from_T_group = Transfer_set.groupby(['from_Trip'])
    for idx, rows in from_T_group:
        trip_transfer_dict[idx] = list(zip(rows["from_stop_index"], rows['to_trip'],rows['to_stop_index']))
    import pickle
    with open('trip_transfer_dict_partial.pkl', 'wb') as pickle_file:
        pickle.dump(trip_transfer_dict,pickle_file)
    with open('./dict_builder/trip_transfer_dict_partial.pkl', 'wb') as pickle_file:
        pickle.dump(trip_transfer_dict,pickle_file)
    print("trip_Transfer_dict done")
    return trip_transfer_dict

