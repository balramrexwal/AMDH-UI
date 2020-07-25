import sys
from io import StringIO

class bcolors:
    HEADER = '\033[95m'
    INFO = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    WARNING_HEADER = '\033[33m'
    UNDERLINE = '\033[4m'


class Out:
    def __init__(self, platform):

        if platform is None:
            self.output = StringIO()
            sys.stdout = self.output
            self.platform = None
        else:
            self.platform = platform


    def print_info(self ,message):
        if self.platform == "Linux" or self.platform == "Darwin":
            print(bcolors.INFO + "[-] INFO: " + bcolors.ENDC + f"{message}" )
        elif self.platform == "Windows":
            print("[-] INFO: " + f"{message}")
        else:
            print("INFO: " + f"{message}")



    def print_warning(self, message):
        if self.platform == "Linux" or self.platform == "Darwin":
            print(bcolors.WARNING + "[!] WARNING: " + f"{message}" + bcolors.ENDC)
        elif self.platform == "Windows":
            print("[!] WARNING: "  + f"{message}")
        else:
            print("WARNING: " + f"{message}")

    def print_warning_header(self, message):
        if self.platform == "Linux" or self.platform == "Darwin":
            print(bcolors.WARNING_HEADER + "[!]  " + f"{message}" + bcolors.ENDC)
        elif self.platform == "Windows":
            print("[!] WARNING: " + f"{message}")
        else:
            print("HEADER_WARNING: " + f"{message}")


    def print_error(self, message):
        if self.platform == "Linux" or self.platform == "Darwin":
            print(bcolors.FAIL + "[X] ERROR: " + f"{message}" + bcolors.ENDC)
        elif self.platform == "Windows":
            print("[X] ERROR: " + f"{message}")
        else:
            print("ERROR: " + f"{message}")

    def print_success(self, message):
        if self.platform == "Linux" or self.platform == "Darwin":
            print(bcolors.OKGREEN + "[+] OK: " + f"{message}" + bcolors.ENDC)
        elif self.platform == "Windows":
            print("[+] OK: " + f"{message}")
        else:
            print("OK: " + f"{message}")

    def print_high_warning(self, message):
        if self.platform == "Linux" or self.platform == "Darwin":
            print(bcolors.FAIL + "[!] WARNING: " + f"{message}" + bcolors.ENDC)
        elif self.platform == "Windows":
            print("[!] WARNING: " + f"{message}")
        else:
            print("HIGH_WARNING: " + f"{message}")
