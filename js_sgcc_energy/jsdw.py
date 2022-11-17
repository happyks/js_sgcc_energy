import logging
import datetime as dt
import json
import asyncio
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import urllib

         
_LOGGER=logging.getLogger(__name__)

BASE_API_URL = "https://weixin.js.sgcc.com.cn/wxapp_dlsh/wx/oauth_executeNewMini.do"

class AuthFailed(Exception):
    pass


class InvalidData(Exception):
    pass


class JS_sgcc_data:
    def __init__(self, session, openid, time_stamp, noncestr, sign, unionid, jmConsNo, more_people, more_apply_date):
        self._info = {}
        self._session = session
        self._openid = openid
        self._time_stamp = time_stamp
        self._noncestr = noncestr
        self._sign = sign
        self._unionid = unionid
        self._jmConsNo = jmConsNo
        self._more_people = more_people
        self._more_apply_date = more_apply_date

    def commonHeaders(self):
        headers = {
            'Host': 'weixin.js.sgcc.com.cn',
            'Connection':  'keep-alive',
            'Content-Length': '0',
            'content-type': 'application/json',
            'Accept-Encoding': 'gzip,compress,br,deflate',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0(0x18000026) NetType/WIFI Language/zh_CN',
            'Referer': 'https://servicewechat.com/wx203b37ad2ad5d2a6/32/page-frame.html',
        }
        return headers
        
    def get_json_data(time_stamp, noncestr, sign, jmConsNo):
        dicts={}
        with open('/config/custom_components/js_sgcc_energy/js_sgcc_param.json', 'r',encoding="utf-8") as f:
            old_data = json.load(f)
            old_data['time_stamp'] = time_stamp
            old_data['noncestr'] = noncestr
            old_data['sign'] = sign
            old_data['jmConsNo'] = jmConsNo
            dicts = old_data
        f.close()
        return(dicts)

    def write_json_data(dict):
        with open('/config/custom_components/js_sgcc_energy/js_sgcc_param.json', 'w',encoding="utf-8") as r:
            json.dump(dict,r,indent=4)
        r.close()

    
    async def async_get_token(self):
                   
        return True   

    async def async_get_baseinf(self):
        _LOGGER.debug(f"async_get_baseinf runing")
        ret = True
        base_url_headers = self.commonHeaders()
        base_url_params = {
            "openid": self._openid,
            "timestamp": self._time_stamp,
            "noncestr": self._noncestr,
            "sign": self._sign,
            "unionid": self._unionid,
            "userInfo": 'null'         
        }
        url = BASE_API_URL  + "?openid=" + self._openid +"&timestamp=" + self._time_stamp + "&noncestr=" + self._noncestr + "&sign=" + self._sign + "&unionid=" + self._unionid + "&userInfo=null" 
        _LOGGER.debug(f"{url}")
        resp = await self._session.post(url, headers=base_url_headers, timeout=20)
        _LOGGER.debug(f"{resp.url}")
        _LOGGER.debug(f"{resp.status}")
        return ret 
            
    async def get_monthly_bill(self):
         return True
        
    async def get_daily_bills(self):
          return True
        
    async def async_get_data(self):
        self._info = {}
        await self.async_get_token()
        await self.async_get_baseinf()
        tasks = [
            self.get_monthly_bill(),
            self.get_daily_bills()
        ]
        await asyncio.wait(tasks)
        #_LOGGER.debug(f"Data {self._info}")
        return True
  #  return self._info
        
        


