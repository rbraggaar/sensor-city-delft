# How to use
Combine config.py and boot.py with other scripts, like main.py.

Set-up the WLAN interface in the boot.py script, e.g. call setup_ap() from within boot.py. 
This will keep the connection alive when soft rebooting.

Config.py contains sensitive settings such as the server username and password (required for both telnet (Putty) and ftp (Filezilla).
