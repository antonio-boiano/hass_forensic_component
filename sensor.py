"""GitHub sensor platform."""
import logging
import voluptuous as vol

import asyncio
import datetime
import base64

from typing import Any, Callable, Dict, Optional,Union

from .const import PACKET_154, DOMAIN

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_PATH, EVENT_HOMEASSISTANT_STOP

from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.core import CoreState, Event

from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

_LOGGER = logging.getLogger(__name__)

try:
    import killerbee
except ImportError:
    from . import killerbee


#from .core.zbdump import async_zbdump

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({vol.Optional(CONF_PATH): cv.string})




async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    
    async def printing (event: Event):
        
        new_dict=event.data
        original_dict = {}
        for key, value in new_dict.items():
            if key == 'bytes':
                original_dict[key] = base64.b64decode(value)
            elif key == 'dbm':
                original_dict[key] = int(value)
            elif key == 'datetime':
                original_dict[key] = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
            else:
                original_dict[key] = value
        #_LOGGER.info(original_dict)
        
        
    
    """Set up the sensor platform."""
    #async_zbdump.start_dump(channel=11)
    #ldev=await async_zbdump.get_dev_info()
    #_LOGGER.info(ldev[0])
    #entities = SnifferSensor(async_zbdump)
    #hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, entities.shutdown)
    #unsub = hass.bus.async_listen(PACKET_154, printing)
    #add_entities([entities], True)
    

        

class SnifferSensor(Entity):
    def __init__(self, zb):
        self._zb = zb
        self._state = None
        self._idle_loop_task = None
        self._arrivedpacket = None
        self.packet_count=0
        self._queue = asyncio.Queue(100) #TODO Define this value as costant into a define
    
        
    async def async_added_to_hass(self) -> None:
        """Handle when an entity is about to be added to Home Assistant."""
        if not self.should_poll:
            self._idle_loop_task = self.hass.async_create_task(self.wait_for_packets())
            

    @property
    def name(self):
        dev_list = self._zb.kb.get_dev_info()
        #return dev_list[0]
        return "Forensic 15.4"

    @property
    def state(self):
        return self._state
    
    def packet(self):
        return self._arrivedpacket
    
    #To say to hass that the state should not be polled
    @property
    def should_poll(self) -> bool:
        return False
    
    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        dev_list = self._zb.kb.get_dev_info()
        listToStr = " ".join([str(elem) for elem in dev_list])
        return listToStr
    
    def update(self):
        #self_state = pickle.dumps(self._zb.pnext())            
        self._state =  self.packet_count
        _LOGGER.info(self._state)
        self._attr_native_value=self._state
        
    async def shutdown(self, *_):
        """Close resources."""
        #zb.close() TODO
        if self._idle_loop_task:
            self._idle_loop_task.cancel()

    
    async def wait_for_packets(self):
        """Wait for data pushed from server."""
        asyncio.create_task(self.dump_packets())     
        
    
    async def dump_packets(self):
        """Wait for data pushed from server."""
        #await asyncio.sleep(5)
        while True:
            await asyncio.sleep(0)
            packet: Optional[dict[Union[int, str], Any]] = self._zb.pnext()
            if packet is not None:
                self.packet_count=self.packet_count+1
                #_LOGGER.info(packet)
                self._state = self.packet_count
                    
                new_dict = {}
                for key, value in packet.items():
                    if key in ('bytes', 'dbm', 'datetime', 'validcrc', 'rssi'):
                        if key == 'bytes':
                            encoded = base64.b64encode(value)
                            new_dict[key] = encoded.decode('ascii')
                        if key == 'datetime':
                            new_dict[key] = str(value)

                self.hass.bus.async_fire(PACKET_154,new_dict)
                self.async_write_ha_state()