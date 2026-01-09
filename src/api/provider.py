# src/api/provider.py
import os
from datetime import datetime
from typing import Literal

from src.api.base_api import BaseApi
from src.api.cexio.cexioNewApi import Api
from src.api.emulatorcexio.cexioEmNewApi import EmulatorApi
from src.config import prj_configs



class ApiProvider:
    @staticmethod
    def get(unix_curr_time: int =None) -> BaseApi:
        mode = str(prj_configs.CALC_MODE).upper()

        if mode == "EMULATION":
            return EmulatorApi(
                username=prj_configs.USER,
                unix_curr_time=unix_curr_time
            )
        if mode == "API":
            return Api(
                username=prj_configs.API_USER,
                api_key=prj_configs.API_KEY,
                api_secret=prj_configs.API_SECRET,
            )

        raise ValueError(f"Unknown MODE: {mode}. Use 'API' or 'EM_API'.")


if __name__ == '__main__':

    api = ApiProvider.get()
    print(api.open_orders())