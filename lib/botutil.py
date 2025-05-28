import subprocess

def updateBot() -> None:
    result = subprocess.run("git pull", capture_output=True, shell=True, text=True)
    if result.returncode == 0:
        output = result.stdout
        if output == "Already up to date.":
            return False
        else:
            return True