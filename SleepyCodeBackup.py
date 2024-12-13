"""
Code design for the girls of Girleek during a workshop on python.
"""

EMAIL = 'YOUR_MEROSS_EMAIL'
PASSWORD = 'YOUR_MEROSS_PASSWORD'

import asyncio
import os
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
import socket


async def main():
    # Setup the HTTP client API from user-password
    # When choosing the API_BASE_URL env var, choose from one of the above based on your location.
    # Asia-Pacific: "iotx-ap.meross.com"
    # Europe: "iotx-eu.meross.com"
    # US: "iotx-us.meross.com"
    http_api_client = await MerossHttpClient.async_from_user_password(api_base_url='https://iotx-eu.meross.com',
                                                                      email=EMAIL, 
                                                                      password=PASSWORD)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('', 3615))
   
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    await manager.async_device_discovery()
    plugs = manager.find_devices(device_type="mss210")
    bool_quit=False
    while True:
        data, address = udp_socket.recvfrom(1024)
        text= data.decode().strip()
        print(f"Received data: {text} from {address}")  
        if text == "on" or text.startswith("*"):
            for dev in plugs:
                await dev.async_update()
                await dev.async_turn_on(channel=0)
        elif text == "off" or text.startswith("+"):
            for dev in plugs:
                await dev.async_update()
                await dev.async_turn_off(channel=0)
        else:
            print("Invalid command")
        if bool_quit:
            break
        # for plug in plugs:
        #     print(f"- {plug}")
        #     # Turn it on channel 0
        #     # Note that channel argument is optional for MSS310 as they only have one channel
        #     dev = plugs[0]

        #     # The first time we play with a device, we must update its status
        #     await dev.async_update()

        #     # We can now start playing with that
        #     print(f"Turning on {dev.name}...")
        #     await dev.async_turn_on(channel=0)
        #     print("Waiting a bit before turing it off")
        #     await asyncio.sleep(5)
        #     print(f"Turing off {dev.name}")
        #     await dev.async_turn_off(channel=0)

    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()

    udp_socket.close()

if __name__ == '__main__':
    # Windows and python 3.8 requires to set up a specific event_loop_policy.
    #  On Linux and MacOSX this is not necessary.
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.stop()
