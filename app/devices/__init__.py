from app import config
from app.cloud import MiCloud

from .fan import Standing2Fan
from .vacuum import Lite2Vacuum
from.intercom import DomRuApi

# Xiaomi MIOT
api = MiCloud(username=config.CLOUD_USERNAME, password=config.CLOUD_PASSWORD, region='ru')
fan = Standing2Fan(api)
vacuum = Lite2Vacuum(api)

# Custom devices
intercom = DomRuApi(config.DOMRU_TOKEN, config.DOMRU_PLACE_ID, config.DOMRU_CONTROL_ID)

devices = {
    'dmaker.fan.p18': fan,
    'ijai.vacuum.v10': vacuum,
    'domru.intercom.355': intercom
}
