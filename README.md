# check_dyn_dsf


Nagios plugin to check the DSF status in DynECT (using API REST).
Tested in [EyesOfNetwork](www.eyesofnetwork.com) distribution (CentOS 6.5).


## Prerequisite

Tested and works with python 2.6.
Need NSCA configured.


## Installation


1. Just copy the files into Nagios plugins directory and adapt Nagios rights.
2. Change args value (in check_dyn_dsf.py) to correspond to your authentication parameter.
3. Create Nagios check in passive mode.


## Usage

check_dyn_dsf.py <dsf_name>

I use the NSCA protocol to check in passive mode because the API connection is too slow and can product timeout.
I recommend to create a cron file like this :

```
* * * * * nagios /srv/eyesofnetwork/nagios/plugins/check_dyn_dsf.py <dsf_name> &> /dev/null
```
