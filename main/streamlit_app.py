import os
import runpy

# Set working directory to main
os.chdir(os.path.dirname(__file__))

runpy.run_path("scripts/open_gui.py", run_name="__main__")