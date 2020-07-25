from utils.out import *
import json

settings_file = "config/settings.json"

class Settings:

    def __init__(self, json_settings_file, adb, harden=False):
        self.json_settings_file = json_settings_file
        self.adb = adb
        self.harden = harden
        self.result_scan = dict()

    def check(self):
        with open(self.json_settings_file) as settingsFile:
            settings = json.load(settingsFile)

        self.loop_settings_check("secure", settings)

        self.loop_settings_check("global", settings)




    def loop_settings_check(self, section, settings):
        for a in settings[section]:
            command_result = self.adb.content_query(section, a["name"])

            if "No result found" in command_result:
                self.append_key_to_result_scan_dict(section, {a["name"]: {'current': "key not found",'expected': a["expected"].strip()}})

            elif command_result.split("value=")[1].strip() == a["expected"].strip():

                self.append_key_to_result_scan_dict(section, {a["name"]: {'current':command_result.split("value=")[1].strip(), 'expected': a["expected"].strip()}})


            else:
                if self.harden:
                    self.adb.content_insert(section, a["name"], expected_value=a["expected"],
                                            expected_value_type=a["type"])
                else:
                    self.append_key_to_result_scan_dict(section, {a["name"]: {'current':command_result.split("value=")[1].strip(), 'expected': a["expected"].strip()}})

        return self.result_scan

    def get_scan_report(self, section):
        if self.result_scan[section]:
            return self.result_scan[section]
        return {}

    def append_key_to_result_scan_dict(self, key, value):
        if key in self.result_scan.keys():
            self.result_scan[key].update(value)
        else:
            self.result_scan[key] = dict()
            self.result_scan[key].update(value)

