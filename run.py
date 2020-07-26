from flask import Flask, render_template, request, redirect, url_for

from core.adb import ADB
from core.application import App
from core.settings import Settings

app = Flask(__name__)
app.config.from_object('config')
json_settings = "config/settings.json"

ADB_PATH = app.config["ADB_PATH"]

def refresh_scan(device, app_type):
    adb = ADB(ADB_PATH, device_id=device)

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
        dict_packages[package]["mal_confidence"] = app.malware_confidence
        dict_packages[package]["mal_score"] = app.score

    return dict_packages

def check_device_up(device_id):
    adb = ADB(ADB_PATH)
    devices = adb.list_devices()
    if device_id in devices:
        return True

    return False



@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def index():
    adb = ADB(ADB_PATH)
    devices = adb.list_devices()

    return render_template('home.html', devices=devices)


@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        if 'scan' in request.form.keys() and request.form['scan'] == 'apps_scan':
            device = request.form['device']
            app_type = request.form['app']
            dict_packages = refresh_scan(device, app_type)
            return render_template('scan.html', scan="apps_scan", app_type=app_type, show=request.form['show'],
                                   packages=dict_packages,
                                   device=device)

        if 'scan' in request.form.keys() and request.form['scan'] == 'settings_scan':
            device = request.form['device']
            adb = ADB(ADB_PATH, device_id=device)
            settings = Settings(json_settings, adb)
            settings.check()
            return render_template('scan.html', scan="settings_scan", secure_result=settings.get_scan_report("secure"),
                                   global_result=settings.get_scan_report("global"), device=device)

    return redirect(url_for('index'))


@app.route('/application/<string:device>/<string:app_type>/<string:show>/<string:package>')
def application(device, app_type, show, package):
    adb = ADB(device_id=device)
    dumpsys_out = adb.dumpsys(["package", package])
    perms_list = adb.get_req_perms_dumpsys_package(dumpsys_out)
    app = App(adb, package, perms_list=perms_list)
    all_perms, dangerous_perms, device_owner = app.check_app()
    if show == "danger_perms":
        return render_template('application.html', app_type=app_type, show=show, device=device, package=package,
                               perms=dangerous_perms)
    else:
        return render_template('application.html', app_type=app_type, show=show, device=device, package=package,
                               perms=all_perms)


@app.route('/application/<string:device>/<string:app_type>/<string:show>/<string:package>/action',
           methods=['POST', 'GET'])
def app_action(device, app_type, show, package):
    adb = ADB(ADB_PATH, device_id=device)

    if 'action' in request.form.keys() and request.form['action'] == 'revoke':
        for perm in request.form.keys():
            if perm == 'action' or perm == 'scan_table_length':
                break
            try:
                adb.revoke_perm_pkg(package, perm)
            except Exception as e:
                print(e)
    elif 'action' in request.form.keys() and request.form['action'] == 'uninstall':
        try:
            adb.uninstall_app(package)

        except Exception as e:
            print(e)

    elif 'action' in request.form.keys() and request.form['action'] == 'rm_admin':
        try:
            app = App(adb, package)
            app.remove_device_admin_for_app()
        except Exception as e:
            print(e)

    dict_packages = refresh_scan(device, app_type)

    return render_template('scan.html', scan="apps_scan", app_type=app_type, show=show, packages=dict_packages,
                           device=device)


@app.route('/application/<string:device>/settings/harden', methods=['POST'])
def harden_settings(device):
    adb = ADB(ADB_PATH, device_id=device)
    settings = Settings(json_settings, adb, True)
    settings.check()
    return redirect(url_for('index'))

@app.route('/application/<string:device>/<string:app_type>/<string:show>/apps_action', methods=['POST'])
def apps_action(device, app_type, show):
    adb = ADB(ADB_PATH, device_id=device)

    if 'action' in request.form.keys() and request.form['action'] == 'uninstall':
        for package in request.form.keys():
            if package == 'action' or package == 'scan_table_length':
                continue
            try:
                adb.uninstall_app(package)
            except Exception as e:
                print(e)

    elif 'action' in request.form.keys() and request.form['action'] == 'rm_admin':
        for package in request.form.keys():
            if package == 'action' or package == 'scan_table_length':
                continue
            try:
                app = App(adb, package)
                app.remove_device_admin_for_app()
            except Exception as e:
                print(e)

    dict_packages = refresh_scan(device, app_type)

    return render_template('scan.html', scan="apps_scan", app_type=app_type, show=show, packages=dict_packages,
                           device=device)


if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], host="127.0.0.1", port=app.config["PORT"])
