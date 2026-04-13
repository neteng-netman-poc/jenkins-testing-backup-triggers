
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv("error_codes.env")

class sshInfo:
    def __init__(self, config_file:str):
        self.config_file = config_file
        pass

    def _check_file_exists(self)->bool:
        if os.path.isfile(self.config_file):
            return True
        return False


    def _return_csv_dict(self)->list[dict]:
        dataframe  = pd.read_csv(self.config_file)
        list_of_dicts = dataframe.to_dict(orient='records')
        return list_of_dicts

    # list of dicts, string for some summary, int for error code , bool for error_found or not 
    def return_sshconfigs(self)->tuple[list[dict], str, int, bool]:
        if not self._check_file_exists():
            return ([], "cannot find the file !! please check", int(os.getenv("file_not_found")), True)
        return (self._return_csv_dict(), "found - check | format - check", int(os.getenv("all_okay")), False)
        
