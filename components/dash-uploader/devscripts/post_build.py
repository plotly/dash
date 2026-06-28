from pathlib import Path
import shutil

root = Path(__file__).resolve().parent.parent

components = root / "src" / "lib" / "components"

component_names = [x.name[:-9] for x in components.glob("*.react.js")]

folder_from = root / "dash_uploader"
folder_to = folder_from / "_build"

filenames = ["metadata.json", "package-info.json", "_imports_.py"] + [
    x + ".py" for x in component_names
]

for filename in filenames:
    shutil.move(folder_from / filename, folder_to / filename)

Path(folder_to / "__init__.py").touch(exist_ok=True)
