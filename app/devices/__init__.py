from app import config
from app.clouds.mi_cloud import MiCloud
from app.clouds.tcl_cloud import TclCloud

from .fan import Standing2Fan
from .vacuum import Lite2Vacuum
from .humidifier import Humidifier2
from .humidifier_sensor import Humidifier2Sensor
from .intercom import DomRuApi
from .ac import TclAC

# Xiaomi
mi_cloud = MiCloud(config.MI_CLOUD_USERNAME, config.MI_CLOUD_PASSWORD, 'ru')
fan = Standing2Fan(mi_cloud)
vacuum = Lite2Vacuum(mi_cloud)
humidifier = Humidifier2(mi_cloud)
humidifier_sensor = Humidifier2Sensor(mi_cloud)

# TCL
# tcl_cloud = TclCloud(config.TCL_CLOUD_USERNAME, config.TCL_CLOUD_PASSWORD, 'ru')
# ac = TclAC(tcl_cloud)

# Custom devices
intercom = DomRuApi(config.DOMRU_TOKEN, config.DOMRU_PLACE_ID, config.DOMRU_CONTROL_ID)

devices = {
    'dmaker.fan.p18': fan,
    'ijai.vacuum.v10': vacuum,
    'deerma.humidifier.jsq2w': humidifier,
    'deerma.humidifier.jsq2w.sensor': humidifier_sensor,
    'domru.intercom.355': intercom,
    # 'tcl.ac.355': ac
}
