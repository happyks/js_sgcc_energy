import logging
import asyncio
import async_timeout
import homeassistant.util.dt as dt_util
import json
from homeassistant.helpers.event import async_track_point_in_utc_time
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers import discovery
from homeassistant.core import HomeAssistant
from .jsdw import JS_sgcc_data, AuthFailed, InvalidData
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=20)


async def async_setup(hass: HomeAssistant, hass_config):
    config = hass_config[DOMAIN]
    with open('/config/custom_components/js_sgcc_energy/js_sgcc_param.json', 'r',encoding="utf-8") as f:
        custom_param = json.load(f)
        openid = custom_param['openid']
        time_stamp = custom_param['time_stamp']
        noncestr = custom_param['noncestr']
        sign = custom_param['sign']
        unionid = custom_param['unionid']
        jmConsNo = custom_param['jmConsNo']
    f.close()
    more_people =  config.get('more_people')
    more_apply_date =  config.get('more_apply_date')
    coordinator = JSSGCCCorrdinator(hass, openid, time_stamp,noncestr,sign,unionid,jmConsNo,more_people,more_apply_date)
    hass.data[DOMAIN] = coordinator

    async def async_load_entities(now):
        try:
            await coordinator.async_auth()
            await coordinator.async_refresh()
            if coordinator.last_update_success:
                _LOGGER.debug("Successful to update data, now loading entities")
                # hass.async_create_task(discovery.async_load_platform(
                #     hass, "sensor", DOMAIN, config, hass_config))
                # return
        except AuthFailed as e:
            _LOGGER.error(e)
            return
        except Exception:
             _LOGGER.error(f"Field to update data, retry after 60 seconds")
             pass
        async_track_point_in_utc_time(hass, async_load_entities, dt_util.utcnow() + timedelta(seconds=60))
        
    async_track_point_in_utc_time(hass, async_load_entities, dt_util.utcnow())
    return True


class JSSGCCCorrdinator(DataUpdateCoordinator):
    def __init__(self, hass, openid, time_stamp, noncestr, sign,unionid, jmConsNo, more_people, more_apply_date):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL
        )
        self._hass = hass
        session = async_create_clientsession(hass)
        self._jsdw = JS_sgcc_data(session, openid, time_stamp, noncestr, sign, unionid, jmConsNo, more_people, more_apply_date)

    async def async_auth(self):
        await self._jsdw.async_get_token()

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(60):
                data = await self._jsdw.async_get_data()
                if not data:
                    raise UpdateFailed("Failed to data update")
                return data
        except asyncio.TimeoutError:
            raise UpdateFailed("Data update timed out")
        except Exception:
            raise UpdateFailed("Failed to data update with unknown reason")
