from cx_Freeze import setup, Executable
import sys, os

base = None

if sys.platform == 'win32':
    PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
    os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
    os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')
    executables = [Executable("gertec_tc506m_sync.py", base="Win32GUI")]

    packages = ["jsonschema", "fabric"]
    options = {
        'build_exe': {
            'packages': packages,
            "include_files": [
                os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
                os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
                "fabfile.py",
                'tc506.ico'
            ]
        }
    }

    setup(
        name = "Gertec TC506M Sync",
        author='Carlos Alexandre',
        author_email='calexandrepcjr@gmail.com',
        options = options,
        version = "0.1",
        description = 'A program to help the sysadmin to sync Gertec TC506M data across the servers',
        executables = executables
    )
