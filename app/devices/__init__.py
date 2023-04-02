from .fan import Standing2Fan
from .vacuum import Lite2Vacuum
from .tv import MiTvP1

from app import config


fan = Standing2Fan(ip=config.FAN_HOST, token=config.FAN_TOKEN)
vacuum = Lite2Vacuum(ip=config.VACUUM_HOST, token=config.VACUUM_TOKEN)
tv = MiTvP1(host=config.TV_HOST, mac=config.TV_MAC)
