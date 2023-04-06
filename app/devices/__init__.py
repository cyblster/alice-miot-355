from app import config
from app.cloud import MiCloud

from .fan import Standing2Fan
from .vacuum import Lite2Vacuum

api = MiCloud(username=config.CLOUD_USERNAME, password=config.CLOUD_PASSWORD, region='ru')
fan = Standing2Fan(api)
vacuum = Lite2Vacuum(api)

devices = {
    'dmaker.fan.p18': fan,
    'ijai.vacuum.v10': vacuum
}
