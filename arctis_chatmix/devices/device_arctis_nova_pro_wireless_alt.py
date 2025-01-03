from arctis_chatmix.device_manager.device_manager import device_manager_factory
from arctis_chatmix.devices.device_arctis_nova_pro_wireless import ArctisNovaProWirelessDevice


@device_manager_factory(0x12e5, 'Arctis Nova Pro Wireless X')
class ArctisNovaProWirelessDeviceX(ArctisNovaProWirelessDevice):
    pass
