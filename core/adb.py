from subprocess import run, PIPE
import re


class ADB:

    def __init__(self, adb_path="/usr/bin/adb", device_id=""):
        """Constructor"""
        self.adb_path = adb_path
        self.device_id = device_id


    def adb_exec(self, commands_array):
        """This function return the output of the command 'adb commands_array[0] commands_array[1] ...'"""

        if not self.device_id :
            commands_array.insert(0, self.adb_path)
            result = run(commands_array,
                         stdout=PIPE, stderr=PIPE, check=True,
                         universal_newlines=True)
        else:
            commands_array.insert(0, self.adb_path)
            commands_array.insert(1, "-s")
            commands_array.insert(2, self.device_id)
            result = run(commands_array,
                         stdout=PIPE, stderr=PIPE, check=True,
                         universal_newlines=True)

        return result.stdout

    
    def list_devices(self):
        """This function return a list of the connected devices"""
        devices = {}
        command_result = self.adb_exec(["devices"]).split("\n")[1:]
        for line in command_result:
            if line:
                temp = line.split("\t")
                devices.update({temp[0].strip(): temp[1].strip()})
        return devices


    # exceptions => apps not available
    # status => Enum in models.py
    def list_installed_packages(self, status):
        """This function return a list of the installed packages. """
        adb_command = ["shell", "pm", "list", "packages", "-"+status]
        output_command = self.adb_exec(adb_command)
        list_installed_apps = []
        for line in output_command.split("\n"):
            if not (":" in line):
                continue
            list_installed_apps.append(line.split(":")[1])

        return list_installed_apps


    def dump_apk_from_device(self, package_name, output_file="base.apk"):
        """This function dump the apk of package_name package as output_file. if output file
         exist, it'll be overwritten."""
        adb_path_command = ["shell", "pm", "path", str(package_name)]
        apk_path = (self.adb_exec(adb_path_command)).split("\n")[0].split(":")[1]

        adb_pull_command = ["pull", apk_path.strip(), output_file]
        output_pull_command = self.adb_exec(adb_pull_command)

        if "1 file pulled" in output_pull_command:
            return True

        return False

    def uninstall_app(self, package_name):
        """This function uninstall package_name using user 0 privileges."""
        adb_uninstall_command = ["shell", "pm", "uninstall", "--user", "0", package_name]
        output_uninstall_command = self.adb_exec(adb_uninstall_command)

        if "Success" in output_uninstall_command:
            return True

        return False

    def disable_app(self, package_name):
        """This function disable package_name using user 0 privileges."""
        adb_uninstall_command = ["shell", "pm", "disable", "--user", "0", package_name]
        output_uninstall_command = self.adb_exec(adb_uninstall_command)

        if "Success" in output_uninstall_command:
            return True

        return False

    # params  is an array of arguments
    def dumpsys(self, params):
        """This function return the output of the command 'dumpsys param[0] param[1] ...'."""
        dumpsys_command = ["shell", "dumpsys"] + params
        return self.adb_exec(dumpsys_command)

    # return list of permissions
    # output = dumpsys package package_name
    def get_req_perms_dumpsys_package(self, dumpsys_output):
        """This function return a list of granted requested permissions from the output of the command
        'dumpsys  package {package_name}' command given as parameter. """
        if "requested permissions" in dumpsys_output:
            granted_perms = re.findall(r"(.*): granted=true", dumpsys_output)
            return [perm.strip(' ') for perm in granted_perms]#re.split(" +", perms_part_tmp)

        return []

    def get_install_perms_dumpsys_package(self, dumpsys_output):
        """This function return a list of granted install permissions from the output of the command
                'dumpsys  package {package_name}' command given as parameter. """
        if "install permissions" in dumpsys_output:

            p = re.compile(r'(?<=install permissions:).+?(?=User [0-9]+:)')
            perms_part = re.search(p, dumpsys_output.replace("\n", " "))
            perms_part_tmp = perms_part.group(0).strip().replace(": granted=true", "")
            return re.split(" +", perms_part_tmp)

        return []


    def content_query(self, settings_section, key):
        """This function return the value of 'key' in the settings_section section.
        section can be one of:
            - secure
            - global
            - system"""
        command = ["shell", "content", "query", "--uri", "content://settings/" + settings_section,
                   "--projection", "name:value", "--where", "'name=\"" + key + "\"'"]
        return self.adb_exec(command)

    def content_delete(self, settings_section, key):
        """This function delete the content of 'key' in the settings_section section.
                section can be one of:
                    - secure
                    - global
                    - system"""
        command = ["shell", "content", "delete", "--uri", "content://settings/" + settings_section,
                   "--where", "'name=\"" + key + "\"'"]
        return self.adb_exec(command)

    def content_insert(self, settings_section, key, expected_value, expected_value_type):
        """This function insert the content of 'key' in the settings_section section and update of exist.
            section can be one of:
                - secure
                - global
                - system"""
        if expected_value_type not in ['b', 's', 'i', 'l', 'f', 'd']:
            return "value type is not recognized! type should be: b,s,i,l,f or d"

        command = ["shell", "content", "insert", "--uri", "content://settings/" + settings_section,
                   "--bind", "name:s:" + key, "--bind value:" + expected_value_type + ":" + expected_value]
        return self.adb_exec(command)


    def remove_dpm(self, dpm_receiver):
        """This function remove dpm_receiver from active admins list"""
        self.adb_exec(["shell", "dpm", "remove-active-admin", dpm_receiver])

    def revoke_perm_pkg(self, package_name, permission):
        """This function revoke 'permission', given as parameter, for the package package_name"""
        self.adb_exec(["shell", "pm", "revoke", package_name, permission])