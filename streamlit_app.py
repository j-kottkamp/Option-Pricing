import os
import runpy

cwd = os.getcwd()

os.chdir("main")
try:
    runpy.run_path("scripts/open_gui.py", run_name="__main__")
finally:
    os.chdir(cwd)
