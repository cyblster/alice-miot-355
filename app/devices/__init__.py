from .fan import Standing2Fan
from .vacuum import Lite2Vacuum

from app import config


fan = Standing2Fan(ip=config.FAN_HOST, token=config.FAN_TOKEN)
vacuum = Lite2Vacuum(ip=config.VACUUM_HOST, token=config.VACUUM_TOKEN)
