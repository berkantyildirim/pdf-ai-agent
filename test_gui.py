"""GUI test script."""
import sys
import os

# Add the project directory to path
project_dir = r"C:\Users\pc\Documents\Varsayılan Proje\pdf-ai-agent"
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

os.chdir(project_dir)

from main import App

try:
    app = App()
    print("OK - App created successfully")
    print(f"  Window title: {app.title()}")
    print(f"  Window geometry: {app.geometry()}")
    print(f"  Is busy: {app.busy}")
    print("OK - GUI initialization successful!")
    # We don't call mainloop() here - that would block
except Exception as e:
    print("ERROR -", type(e).__name__, ":", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)