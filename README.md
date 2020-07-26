# AMDH Web UI
Android Mobile Device Hardening Web UI (version 1.0)



## Install and usage

```
$ git https://github.com/SecTheTech/AMDH-UI.git; cd AMDH-UI
$ python3 -m venv amdh
$ source amdh/bin/activate
(amdh) $ pip3 install flask
(amdh) $ python3 run.py
```

Do not forget to edit the variable "ADB_PATH" in config.py to specify the path ADB if different than "/usr/bin/adb". 

You can access the UI on : [http://127.0.0.1:8880/](http://127.0.0.1:8880/)



## Screenshots

**New Scan**

![New Scan](screenshots/new_scan.png (New Scan))

**Application Scan**

![Application Scan](screenshots/applications_scan.png (Application Scan))


**Applications' Permissions**

![Applications Permissions](screenshots/Apps_perms_actions.png (Applications Permissions))



**Uninstall Apps**

![Uninstall Apps](screenshots/Uninstall_app.png (Uninstall Apps))



## Used Template:
[https://github.com/StartBootstrap/startbootstrap-sb-admin-2](https://github.com/StartBootstrap/startbootstrap-sb-admin-2)

# Participate 
Pull requests are welcome.
