# Booking Appointment in TLScontact

** A simple script to check the available appointment of TLScontact. **

Tested with Visa Application Centre for France in Edinburgh, the United Kingdom.

## Usage:

```
usage: TLScontact.py [-h] [-d DELAY] [-v] login password month day

Script to check the available appointment of TLScontact.

positional arguments:
  login                      TLScontact login (e-mail address)
  password                   TLScontact password
  month                      The latest acceptable month
  day                        The latest acceptable day

optional arguments:
  -h, --help                 show this help message and exit
  -d DELAY, --delay DELAY    delay between attempts, in seconds(default: 300)
  -v, --verbose              verbose mode
```

### What's more, modify the url in code with your TLScontact application center.

* Modify `TLS_EDI = '<https://fr.tlscontact.com/gb/EDI/index.php>'` with TLScontact homepage in your location
* Modify `TLS_CNX = '<https://fr.tlscontact.com/gb/EDI/login.php>'` with TLScontact connexion page
* Modify `TLS_APP = '<https://fr.tlscontact.com/gb/EDI/myapp.php>'` with My account page

## To-Do:

* Use HTML Parser in the place of split everywhere
* Add booking appointment function
* Replace sleep with Emmm...

Coded for 🍳
