import re
import shlex
import subprocess
import sys
import traceback


def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        elif output:
            print(output.strip().decode("utf-8"))
        else:
            break
    rc = process.poll()
    return rc


with open("friendsite/settings.py") as f:
    for line in f:
        if line.startswith("FRIENDSHIP_VERSION"):
            version = re.search(r"\"(.*)\"", line).group(1)
            break

try:
    run_command(
        "docker build -t friendships/friendships-prod:{} .".format(
            version
        )
    )
    # run_command(
    #     "docker push friendships/friendships-prod:{}".format(version)
    # )
except Exception as e:
    print(e)
    traceback.print_exc()
