"""
this module defines absolute paths and reads a verion number from the file
VERSION if it exists.  If it doesn't find VERSION, it creates the file
and writes "no_version" for the version number.

to use this in another module:

import context

then use context.data_dir and context.root_dir to read data files etc. and
context.__version__ to access the version number
"""
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
data_dir = root_dir / 'data'

sys.path.insert(0,str(root_dir))
sep = "*" * 30
print(f"{sep}\ncontext imported. Front of path:\n{sys.path[0]}\n"
      f"back of path: {sys.path[-1]}\n{sep}\n")

version_file= root_dir / 'VERSION'

if not version_file.is_file():
    __version__ = 'no_version'
    try:
        with open(version_file,'w') as f:
            f.write(__version__)
    except:
        __version_file__=None
else:
    with open(version_file) as f:
        __version__=f.read().strip()
