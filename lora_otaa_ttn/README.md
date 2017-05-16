# Using The Things Network
To set up your Lopy to communicate you can first generate a EUI (a.k.a. Extended Unique Identifier). It works in the same way as a MAC address.

Use the script found [here](https://github.com/rbraggaar/sensor-city-delft/tree/master/device_eui).

The output will look like below:

![](https://github.com/rbraggaar/sensor-city-delft/blob/master/assets/eui.PNG?raw=true)

Write down the number, it starts with 70 in this case, but yours will be different.

# Register your device at TTN
You can follow [this procedure](https://www.thethingsnetwork.org/docs/devices/lopy/usage.html).
For our final application we will implement LoRa through the OTAA method. It is more secure and also more reliable.

# Testing
Once setup, copy the app-eui and the app-key and place them in the config file `config.py`, [line 5 and 6 of this file](https://github.com/rbraggaar/sensor-city-delft/blob/master/lora_otaa_ttn/config.py).

You are now ready to send some test messages. Let's start by saying hi to TTN:
`send_hi_bytes()` or `send_hi_string()` can be called to send this greeting.

You will notice in TTN console the data is displayed in hex format:

![the output](https://github.com/rbraggaar/sensor-city-delft/blob/master/assets/sending%20hi.PNG?raw=true)

Also test with some other messages:

![other messages](https://github.com/rbraggaar/sensor-city-delft/blob/master/assets/different-payloads.PNG?raw=true)

Now click on a payload to inspect it further:

![inspect payload](https://github.com/rbraggaar/sensor-city-delft/blob/master/assets/copy-clipboard.PNG?raw=true)

To see what it says we convert it manually back to ascii (you can use your own scripts for this, e.g. with Node-Red).

![convert to ascii](https://github.com/rbraggaar/sensor-city-delft/blob/master/assets/convert-ascii.PNG?raw=true)

Finally, also note there is some interesting metadata available for each message send over LoRa. These parameters can be used to geo-locate yourself or determine the quality of the link.

![metadata](https://github.com/rbraggaar/sensor-city-delft/blob/master/assets/meta-data.PNG?raw=true)
