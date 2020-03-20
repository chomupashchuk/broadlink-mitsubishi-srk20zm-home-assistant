"""Suppoort for Mitsubishi."""
from datetime import timedelta
import logging
import threading
import voluptuous as vol
import json
import copy

from homeassistant.components.climate import DOMAIN as CLIMATE
from homeassistant.const import (
    CONF_NAME,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.helpers.dispatcher import dispatcher_send

from .const import (
    AC_CODES,
    CLIMATES,
    DATA_MITSUBISHI,
    DEVICES,
    DOMAIN,
    PAR_HVAC_MODE,
    PAR_TEMPERATURE,
    PAR_FAN_MODE,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    IP_ADDRESS,
    FAN_AUTO,
    HUMIDITY_ENTITY,
    TEMPERARURE_ENTITY,
    SUPPORTED_HVAC_MODES,
    SUPPORTED_FAN_MODES,
    TEMP_MIN,
    TEMP_MAX,
)

_LOGGER = logging.getLogger(__name__)

def _has_unique_names(devices):
    names = [device[CONF_NAME] for device in devices]
    vol.Schema(vol.Unique())(names)
    return devices

DEFAULT_NAME = "Mitsubishi"
DEFAULT_HUMIDITY_ENTITY = ""
DEFAULT_TEMPERATURE_ENTITY = ""

DEFAULT_TEMP = 24.0
DEFAULT_HVAC_MODE = HVAC_MODE_OFF
DEFAULT_FAN_MODE = FAN_AUTO

MITSUBISHI_SCHEMA = vol.Schema(
    {
        vol.Required(IP_ADDRESS): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(TEMPERARURE_ENTITY, default=DEFAULT_TEMPERATURE_ENTITY): cv.entity_id,
        vol.Optional(HUMIDITY_ENTITY, default=DEFAULT_HUMIDITY_ENTITY): cv.entity_id,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.All(cv.ensure_list, [MITSUBISHI_SCHEMA], _has_unique_names)},
    extra=vol.ALLOW_EXTRA,
)

class MitsubishiHandler():
    """Mitsubishi handler"""
    
    def __init__(self, hass, device, name, ipaddr, temperature, humidity):
        """Initialize."""
        self._config_data = {}
        self._device = device
        self._hass = hass
        self._lock = threading.Lock()
        self._name = name
        self._file_name = '/config/custom_components/mitsubishi/json/' + name + '.json'
        self._ip_address = ipaddr
        self._temperature_entity = temperature
        self._humidity_entity = humidity

    @property
    def available(self):
        """Return if Mitsubishi is available."""
        return True


    def _read_data_json(self):
        try:
            # read data
            must_reset = False
            
            with open(self._file_name) as json_file:
                read_data = json.load(json_file)
                
            if PAR_HVAC_MODE in read_data:
                if read_data[PAR_HVAC_MODE] in SUPPORTED_HVAC_MODES:
                    self._config_data[PAR_HVAC_MODE] = copy.deepcopy(read_data[PAR_HVAC_MODE])
                else:
                    self._config_data[PAR_HVAC_MODE] = DEFAULT_HVAC_MODE
                    must_reset = True
            else:
                self._config_data[PAR_HVAC_MODE] = DEFAULT_HVAC_MODE
                must_reset = True
                
            if PAR_TEMPERATURE in read_data:
                if read_data[PAR_TEMPERATURE] >= TEMP_MIN and read_data[PAR_TEMPERATURE] <= TEMP_MAX:
                    self._config_data[PAR_TEMPERATURE] = round(read_data[PAR_TEMPERATURE])
                else:
                    self._config_data[PAR_TEMPERATURE] = DEFAULT_TEMP
                    must_reset = True
            else:
                self._config_data[PAR_TEMPERATURE] = DEFAULT_TEMP
                must_reset = True
                
            if PAR_FAN_MODE in read_data:
                if read_data[PAR_FAN_MODE] in SUPPORTED_FAN_MODES:
                    self._config_data[PAR_FAN_MODE] = copy.deepcopy(read_data[PAR_FAN_MODE])
                else:
                    self._config_data[PAR_FAN_MODE] = DEFAULT_FAN_MODE
                    must_reset = True
            else:
                self._config_data[PAR_FAN_MODE] = DEFAULT_FAN_MODE
                must_reset = True
                
        except:
            self._config_data[PAR_HVAC_MODE] = DEFAULT_HVAC_MODE
            self._config_data[PAR_TEMPERATURE] = DEFAULT_TEMP
            self._config_data[PAR_FAN_MODE] = DEFAULT_FAN_MODE
            must_reset = True
            pass
        return must_reset

    def read_data_json(self):
        """Get Mitsubishi data from json file"""
        with self._lock:
            if self._read_data_json():
                self._set_data_json()
    
    def _set_data_json(self):
        """Set Mitsubishi data in json file"""
        with open(self._file_name, 'w') as json_file:
            json.dump(self._config_data, json_file)
    
    def set_data_json(self, parameter_list={}):
        """Set Mitsubishi data in json file"""
        with self._lock:
            self._read_data_json()
            if PAR_HVAC_MODE in parameter_list:
                self._config_data[PAR_HVAC_MODE] = copy.deepcopy(parameter_list[PAR_HVAC_MODE])
            if PAR_FAN_MODE in parameter_list:
                self._config_data[PAR_FAN_MODE] = copy.deepcopy(parameter_list[PAR_FAN_MODE])
            if PAR_TEMPERATURE in parameter_list:
                self._config_data[PAR_TEMPERATURE] = copy.deepcopy(parameter_list[PAR_TEMPERATURE])
                
            try:
                set_hvac_mode = self._config_data[PAR_HVAC_MODE]
                set_fan_mode = self._config_data[PAR_FAN_MODE]
                set_temperature = str(float(self._config_data[PAR_TEMPERATURE]))
                
                if set_hvac_mode == HVAC_MODE_OFF:
                    ir_code = AC_CODES[set_hvac_mode]
                elif set_hvac_mode == HVAC_MODE_FAN_ONLY:
                    ir_code = AC_CODES[set_hvac_mode][set_fan_mode]
                elif set_hvac_mode == HVAC_MODE_DRY:
                    ir_code = AC_CODES[set_hvac_mode][set_temperature]
                else:
                    ir_code = AC_CODES[set_hvac_mode][set_fan_mode][set_temperature]
                if (PAR_HVAC_MODE in parameter_list and self._config_data[PAR_HVAC_MODE] == HVAC_MODE_OFF) or self._config_data[PAR_HVAC_MODE] != HVAC_MODE_OFF:
                    # data sent to AC
                    self._hass.services.call('broadlink', 'send', {'host': self._ip_address, 'packet': ir_code}, False)
                # store data
                self._set_data_json()
                _LOGGER.info("AC generated code {}".format(ir_code))
            except:
                _LOGGER.error("Unknown IR code")

def setup(hass, config):
    """Set up the Mitsubishi component."""
    hass.data.setdefault(DATA_MITSUBISHI, {DEVICES: {}, CLIMATES: []})
    api_list = []
    for device in config[DOMAIN]:
        name = device[CONF_NAME]
        temperature = device[TEMPERARURE_ENTITY]
        humidity = device[HUMIDITY_ENTITY]
        ipaddr = device[IP_ADDRESS]
        try:
            api = MitsubishiHandler(hass, device=device, name=name, ipaddr=ipaddr, temperature=temperature, humidity=humidity)
            api.read_data_json()
        except:
            _LOGGER.error("unknown error", name)
            pass
        hass.data[DATA_MITSUBISHI][DEVICES][name] = MitsubishiDevice(api)
        discovery.load_platform(
            hass, CLIMATE,
            DOMAIN,
            {CONF_NAME: name},
            config)

    if not hass.data[DATA_MITSUBISHI][DEVICES]:
        return False

    # Return boolean to indicate that initialization was successful.
    return True


class MitsubishiDevice:
    """Representation of a base Mitsubishi discovery device."""

    def __init__(
            self,
            api,
    ):
        """Initialize the entity."""
        self.api = api
