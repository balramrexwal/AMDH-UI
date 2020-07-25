from flask import Flask, render_template, request, redirect, url_for

from core.adb import ADB
from core.application import App
from core.settings import Settings

app = Flask(__name__)

json_settings = "config/settings.json"


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def index():
    adb = ADB("/usr/bin/adb")
    devices = adb.list_devices()
    return render_template('home.html', devices=devices)

def refresh_scan(device, app_type):
    adb = ADB(device_id=device)

    packages = adb.list_installed_packages(app_type)
    dict_packages = dict()
    for package in packages:
        dumpsys_out = adb.dumpsys(["package", package])
        perms_list = adb.get_req_perms_dumpsys_package(dumpsys_out)
        app = App(adb, package, perms_list=perms_list)
        perm_desc, dangerous_perms, device_owner = app.check_app()

        dict_packages[package] = dict()
        dict_packages[package]["dangerous"] = dangerous_perms
        dict_packages[package]["isAdmin"] = app.is_app_device_owner()
        dict_packages[package]["all_perms"] = perm_desc

    return dict_packages

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        if 'scan' in request.form.keys() and request.form['scan'] == 'apps_scan':
            device = request.form['device']
            app_type = request.form['app']
            dict_packages = refresh_scan(device,app_type)
            return render_template('scan.html', scan="apps_scan", app_type=app_type, show=request.form['show'], packages=dict_packages,
                                   device=device)

        if 'scan' in request.form.keys() and request.form['scan'] == 'settings_scan':
            device = request.form['device']
            adb = ADB(device_id=device)
            settings = Settings(json_settings, adb)
            settings.check()
            return render_template('scan.html', scan="settings_scan", secure_result=settings.get_scan_report("secure"),
                                   global_result=settings.get_scan_report("global"), device=device)

    return redirect(url_for('index'))


@app.route('/application/<string:device>/<string:app_type>/<string:show>/<string:package>')
def application( device, app_type, show, package):
    adb = ADB(device_id=device)
    dumpsys_out = adb.dumpsys(["package", package])
    perms_list = adb.get_req_perms_dumpsys_package(dumpsys_out)
    app = App(adb, package, perms_list=perms_list)
    all_perms, dangerous_perms, device_owner = app.check_app()
    if show == "danger_perms":
        return render_template('application.html', app_type=app_type, show=show, device=device, package=package, perms=dangerous_perms)
    else:
        return render_template('application.html', app_type=app_type, show=show, device=device, package=package, perms=all_perms)


@app.route('/application/<string:device>/<string:app_type>/<string:show>/<string:package>/action', methods=['POST', 'GET'])
def app_action(device, app_type, show, package):
    adb = ADB(device_id=device)

    if 'action' in request.form.keys() and request.form['action'] == 'revoke':
        for perm in request.form.keys():
            if perm == 'action':
                continue
            try:
                adb.revoke_perm_pkg(package, perm)
            except Exception as e:
                # To-Do
                print(e)
    elif 'action' in request.form.keys() and request.form['action'] == 'uninstall':
        try:
            adb.uninstall_app(package)

        except Exception as e:
            # To-Do
            print(e)

    elif 'action' in request.form.keys() and request.form['action'] == 'rm_admin':
        try:
            dumpsys_out = adb.dumpsys(["package", package])
            perms_list = adb.get_req_perms_dumpsys_package(dumpsys_out)
            app = App(adb, package)
            app.remove_device_admin_for_app()
        except Exception as e:
            # To-Do
            print(e)
    dict_packages = refresh_scan(device, app_type)

    return render_template('scan.html', scan="apps_scan", app_type=app_type, show=show, packages=dict_packages,
                           device=device)

@app.route('/application/<string:device>/settings/harden', methods=['POST'])
def harden_settings(device):
    adb = ADB(device_id=device)
    settings = Settings(json_settings, adb, True)
    settings.check()

    return render_template('scan.html', scan="settings_scan", secure_result=settings.get_scan_report("secure"),
                           global_result=settings.get_scan_report("global"), device=device)


if __name__ == '__main__':
    app.run(debug=False, host="127.0.0.1", port=8880)
