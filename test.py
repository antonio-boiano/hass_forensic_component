import asyncio
from core import IotForensics

async def main():
    iot_forensics:IotForensics = IotForensics()

    snf_file_path = "./forensic_capture"
    file_path = "/home/antonio/Desktop/PCPA_REPO/Test_Acquisition/4 device/HASS/SONOFF/sonoff_20min_day2_hass.pcap"

    feat_cfg_dict_tmp = {
    "topology_map": False,
    "time_window": 5,
    #"timestamp":,
    #"relative_time":,
    #"length":,
    #"payload_data_length":,
    #"dbm":,
    #"formatting_type":,
    #"src":,
    #"dest":,
    #"incoming":,
    #"outgoing":,
    #"mean_inter_arrival_time":,
    #"mean_size": ,
    #"mean_payload_size":,
    #"std_inter_arrival_time":,
    #"std_size":,
    #"std_payload_size":,
    #"mad_inter_arrival_time":,
    #"mad_size":,
    #"mad_payload_size":,
    #"csv_separator":,
    "pcap_file_path": file_path
    }

    feat_cfg_dict ={k: v for k, v in feat_cfg_dict_tmp.items() if v is not None}
                 
    await iot_forensics.start_features_capture(snf_file_path=snf_file_path,object_id=None,features_config=feat_cfg_dict, blocking=True)

if __name__ == "__main__" :
    loop = asyncio.get_event_loop()
    #Insert here the function to test
    loop.create_task(main())
    loop.run_forever()
