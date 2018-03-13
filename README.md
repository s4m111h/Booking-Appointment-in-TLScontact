# Booking Appointment in TLScontact

**A simple script to check the available appointment of TLScontact.**

Tested with Visa Application Centre for France in Edinburgh, the United Kingdom.

### Usage:
- Complete *email = ' '* with E-mail of TLScontact
- Complete *pwd = ' '* with Password of TLScontact
- Modify *TLS_EDI = 'https://fr.tlscontact.com/gb/EDI/index.php'* with TLScontact homepage in your location
- Modify *TLS_CNX = 'https://fr.tlscontact.com/gb/EDI/login.php'* with TLScontact connexion page
- Modify *TLS_APP = 'https://fr.tlscontact.com/gb/EDI/myapp.php'* with My account page
- Modify *DELAY = 300* with the time between two checks
- Modify *MONTH_WANT = 4* with latest month you want
- Modify *DAY_WANT = 30* with the latest day you want

### To-Do:
- Use argument in the place of code modification
- Use HTML Parser in the place of split everywhere
- Add debugger with logging package
- Add exit message with signal package
- Add booking appointment function
- Replace sleep with Emmm...
