"""
Fixed Build Script - Resolves numpy import issues
"""

import subprocess
import sys
import os
import shutil
def install_dependencies():
    """Install build dependencies."""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def clean_build():
    """Clean previous build artifacts."""
    dirs_to_clean = ["build", "dist_fixed"]
    for directory in dirs_to_clean:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"🧹 Cleaned {directory}")

def create_fixed_spec():
    """Create fixed PyInstaller spec file with proper numpy/pandas handling."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Essential hidden imports for numpy/pandas
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'PyQt6.QtGui',
    'mysql.connector',
    'mysql.connector.locales.eng',
    'bcrypt',
    'numpy',
    'numpy.core',
    'numpy.core._methods',
    'numpy.lib.format',
    'pandas',
    'pandas._libs.tslibs.base',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.timezones',
    'pandas._libs.tslibs.fields',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.timestamps',
    'pandas._libs.tslibs.conversion',
    'pandas._libs.properties',
    'pandas.io.parsers.readers',
    'pandas.io.common',
    'openpyxl',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'json',
    'datetime',
    'os'
]

# Data files to include
datas = [
    ('sample_credentials.json', '.'),
    ('assets', 'assets'),
]

# Exclude modules that cause issues or aren't needed
excludes = [
    'matplotlib', 'IPython', 'jupyter', 'notebook',
    'sphinx', 'pytest', 'tkinter._test',
    'test', 'tests', 'testing'
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PasswordGenerator_Fixed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX to avoid corruption
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open("fixed.spec", "w") as f:
        f.write(spec_content)
    print("✅ Created fixed spec file with proper numpy/pandas support")

def build_fixed():
    """Build fixed executable."""
    print("🔨 Building fixed executable...")
    
    try:
        venv_pyinstaller = os.path.join(".venv", "Scripts", "pyinstaller.exe")
        if not os.path.exists(venv_pyinstaller):
            venv_pyinstaller = "pyinstaller"
        
        subprocess.check_call([
            venv_pyinstaller,
            "--distpath=./dist_fixed",
            "--workpath=./build",
            "fixed.spec"
        ])
        
        print("✅ Fixed executable built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def copy_files():
    """Copy required files to fixed dist."""
    source_files = [
        "sample_credentials.json",
        "sample_credentials.txt",
        "requirements.txt"
    ]
    
    for file in source_files:
        if os.path.exists(file):
            try:
                shutil.copy2(file, "dist_fixed")
                print(f"📋 Copied {file}")
            except Exception as e:
                print(f"⚠️ Could not copy {file}: {e}")

def create_fixed_readme():
    """Create README for fixed version."""
    readme_content = """# Password Generator - Fixed Version

## This version fixes the numpy import error

### Quick Start:
1. Run `PasswordGenerator_Fixed.exe` directly
2. Configure database credentials when prompted
3. Start using the application

### What's Fixed:
- ✅ Numpy C-extensions import error resolved
- ✅ Pandas compatibility issues fixed
- ✅ All dependencies properly bundled
- ✅ No extraction needed (single file)

### Files:
- `PasswordGenerator_Fixed.exe` - Fixed executable
- `sample_credentials.json` - Database config (JSON format)
- `sample_credentials.txt` - Database config (text format)
- `requirements.txt` - Dependencies reference

### Features:
- Dynamic database configuration
- User management with roles
- File export with storage options
- Secure password generation
- Path preferences memory

---
Password Generator v1.0 - Fixed Build
"""
    
    with open("dist_fixed/README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ Created fixed version README")

def test_imports():
    """Test if the required imports work in current environment."""
    print("🧪 Testing imports in current environment...")
    
    test_modules = ['numpy', 'pandas', 'PyQt6', 'mysql.connector', 'bcrypt', 'openpyxl']
    failed_imports = []
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"⚠️ Missing modules: {failed_imports}")
        print("Installing missing modules...")
        for module in failed_imports:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                print(f"  ✅ Installed {module}")
            except:
                print(f"  ❌ Failed to install {module}")
    
    return len(failed_imports) == 0

def show_results():
    """Show build results."""
    print("\n📊 Fixed Build Results:")
    print("=" * 40)
    
    exe_path = "dist_fixed/PasswordGenerator_Fixed.exe"
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path)
        print(f"📦 Fixed executable: {size:,} bytes ({size/1024/1024:.1f} MB)")
        print(f"📁 Location: {exe_path}")
        print("🎯 This version should resolve the numpy import error")
    else:
        print("❌ Executable not found")

def main():
    """Main fixed build process."""
    print("🔧 Password Generator - Fixed Build")
    print("=" * 50)
    
    if not os.path.exists("main.py"):
        print("❌ main.py not found. Run from project root directory.")
        return False
    
    # Test imports first
    if not test_imports():
        print("❌ Some required modules are missing. Please install them first.")
        return False
    
    install_dependencies()
    clean_build()
    create_fixed_spec()
    
    if not build_fixed():
        return False
    
    copy_files()
    create_fixed_readme()
    show_results()
    
    print("\n🎉 Fixed Build Complete!")
    print("🔧 This version should fix the numpy import error")
    print("📁 Run: ./dist_fixed/PasswordGenerator_Fixed.exe")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)
def install_dependencies():
    """Install build dependencies and ensure compatibility."""
    print("📦 Installing/updating build dependencies...")
    
    # Install specific versions that work well with PyInstaller
    packages = [
        "pyinstaller>=6.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning installing {package}: {e}")

def clean_build():
    """Clean previous build artifacts."""
    dirs_to_clean = ["build", "dist_fixed"]
    for directory in dirs_to_clean:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"🧹 Cleaned {directory}")

def create_fixed_spec():
    """Create a spec file that properly handles numpy/pandas."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect numpy data files and submodules
numpy_data = collect_data_files('numpy', include_py_files=True)
numpy_modules = collect_submodules('numpy')

# Collect pandas data files  
pandas_data = collect_data_files('pandas', include_py_files=True)
pandas_modules = collect_submodules('pandas')

# Essential hidden imports for numpy/pandas compatibility
hiddenimports = [
    # Core PyQt6
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'PyQt6.QtGui',
    
    # MySQL connector
    'mysql.connector',
    'mysql.connector.locales.eng',
    'mysql.connector.constants',
    
    # Bcrypt
    'bcrypt',
    '_bcrypt',
    
    # Numpy essentials
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    'numpy.core._multiarray_tests',
    'numpy.lib.format',
    'numpy.linalg',
    'numpy.linalg._umath_linalg',
    'numpy.random',
    'numpy.random._common',
    'numpy.random._pickle',
    'numpy.fft',
    'numpy.polynomial',
    'numpy.testing',
    
    # Pandas essentials
    'pandas',
    'pandas._libs.algos',
    'pandas._libs.groupby',
    'pandas._libs.hashing',
    'pandas._libs.hashtable',
    'pandas._libs.index',
    'pandas._libs.internals',
    'pandas._libs.join',
    'pandas._libs.lib',
    'pandas._libs.missing',
    'pandas._libs.parsers',
    'pandas._libs.reduction',
    'pandas._libs.reshape',
    'pandas._libs.sparse',
    'pandas._libs.testing',
    'pandas._libs.tslib',
    'pandas._libs.tslibs.base',
    'pandas._libs.tslibs.ccalendar',
    'pandas._libs.tslibs.conversion',
    'pandas._libs.tslibs.fields',
    'pandas._libs.tslibs.nattype',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.offsets',
    'pandas._libs.tslibs.parsing',
    'pandas._libs.tslibs.period',
    'pandas._libs.tslibs.resolution',
    'pandas._libs.tslibs.strptime',
    'pandas._libs.tslibs.timedeltas',
    'pandas._libs.tslibs.timestamps',
    'pandas._libs.tslibs.timezones',
    'pandas._libs.tslibs.tzconversion',
    'pandas._libs.tslibs.vectorized',
    'pandas._libs.writers',
    'pandas.io.formats.style',
    'pandas.plotting',
    
    # Excel support
    'openpyxl',
    'openpyxl.workbook',
    'openpyxl.worksheet.worksheet',
    'xlrd',
    'xlsxwriter',
    
    # Date/time
    'dateutil',
    'dateutil.tz',
    'dateutil.parser',
    'pytz'
] + numpy_modules + pandas_modules

# Exclude problematic modules
excludes = [
    'matplotlib', 'scipy', 'IPython', 'notebook', 'jupyter',
    'sphinx', 'pytest', 'unittest', 'pydoc', 'doctest',
    'tkinter', 'turtle', 'curses'
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[
        ('sample_credentials.json', '.'),
        ('sample_credentials.txt', '.'),
    ] + numpy_data + pandas_data,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out problematic binaries but keep essential numpy/pandas ones
keep_patterns = [
    'numpy', 'pandas', 'pyqt6', 'mysql', 'bcrypt', 'openpyxl',
    'python3', 'msvcr', 'msvcp', 'vcruntime', 'api-ms-win-core'
]

a.binaries = [x for x in a.binaries if any(
    pattern in x[0].lower() for pattern in keep_patterns
) or not any(
    exclude in x[0].lower() for exclude in [
        'qt6network', 'qt6qml', 'qt6quick', 'qt6webengine',
        'qt6multimedia', 'qt6positioning', 'qt6sensors',
        'qt6charts', 'qt6datavis', 'qt6designer'
    ]
)]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PasswordGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX to avoid compatibility issues
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='PasswordGenerator'
)
"""
    
    with open("fixed.spec", "w") as f:
        f.write(spec_content)
    print("✅ Created fixed spec file with numpy/pandas support")

def build_fixed():
    """Build executable with proper numpy support."""
    print("🔨 Building fixed executable...")
    
    try:
        venv_pyinstaller = os.path.join(".venv", "Scripts", "pyinstaller.exe")
        if not os.path.exists(venv_pyinstaller):
            venv_pyinstaller = "pyinstaller"
        
        # Use the fixed spec file
        subprocess.check_call([
            venv_pyinstaller,
            "--clean",  # Clean cache
            "--distpath=./dist_fixed",
            "--workpath=./build",
            "fixed.spec"
        ])
        
        print("✅ Fixed executable built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def copy_files_fixed():
    """Copy required files to fixed dist."""
    source_files = [
        "sample_credentials.json",
        "sample_credentials.txt",
        "requirements.txt"
    ]
    
    dest_dir = os.path.join("dist_fixed", "PasswordGenerator")
    
    for file in source_files:
        if os.path.exists(file):
            try:
                shutil.copy2(file, dest_dir)
                print(f"📋 Copied {file}")
            except Exception as e:
                print(f"⚠️ Could not copy {file}: {e}")

def create_test_script():
    """Create a test script to verify the executable works."""
    test_content = '''@echo off
echo Testing Password Generator executable...
echo.
cd /d "%~dp0PasswordGenerator"

echo Checking if executable exists...
if not exist "PasswordGenerator.exe" (
    echo ERROR: PasswordGenerator.exe not found!
    pause
    exit /b 1
)

echo Starting executable in test mode...
echo If any errors appear, press Ctrl+C to stop
echo.
"PasswordGenerator.exe"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Application failed to start properly
    echo Check the error messages above
) else (
    echo.
    echo Application appears to have started successfully
)

pause
'''
    
    with open("dist_fixed/Test_Application.bat", "w") as f:
        f.write(test_content)
    print("✅ Created test script")

def create_simple_launcher():
    """Create a simple launcher."""
    launcher_content = '''@echo off
cd /d "%~dp0PasswordGenerator"
start "" "PasswordGenerator.exe"
'''
    
    with open("dist_fixed/Start_PasswordGenerator.bat", "w") as f:
        f.write(launcher_content)
    print("✅ Created launcher script")

def create_fixed_readme():
    """Create README for fixed version."""
    readme_content = """# Password Generator - Fixed Version

## Quick Start:
1. Double-click `Start_PasswordGenerator.bat` to run the application
2. If you encounter issues, run `Test_Application.bat` for debugging

## What's Fixed:
- **Numpy Import Issues**: Properly includes all numpy C-extensions
- **Pandas Dependencies**: Complete pandas library support
- **Clean Build**: Removes problematic modules that cause conflicts

## Troubleshooting:
- If the app doesn't start, run `Test_Application.bat` to see error messages
- Ensure you have Visual C++ Redistributables installed
- Check that MySQL is running and accessible

## Files Structure:
```
dist_fixed/
├── Start_PasswordGenerator.bat    # Quick launcher
├── Test_Application.bat          # Test/debug launcher
├── PasswordGenerator/            # Application folder
│   ├── PasswordGenerator.exe    # Fixed executable
│   ├── sample_credentials.json  # Database config
│   └── [library files]          # Required dependencies
└── README.md                    # This file
```

## Installation:
1. Extract all files to your desired location
2. Configure your database credentials in the sample files
3. Ensure MySQL server is running
4. Run the application using the launcher

---
Password Generator v1.0 - Fixed Build
"""
    
    with open("dist_fixed/README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ Created fixed README")

def show_fixed_results():
    """Show results of the fixed build."""
    print("\n🎯 Fixed Build Results:")
    print("=" * 50)
    
    try:
        fixed_exe = "dist_fixed/PasswordGenerator/PasswordGenerator.exe"
        if os.path.exists(fixed_exe):
            size = os.path.getsize(fixed_exe)
            print(f"✅ Fixed executable: {size:,} bytes ({size/1024/1024:.1f} MB)")
            
            # Check for numpy files
            numpy_files = []
            for root, dirs, files in os.walk("dist_fixed/PasswordGenerator"):
                for file in files:
                    if 'numpy' in file.lower() or 'pandas' in file.lower():
                        numpy_files.append(file)
            
            print(f"📚 Numpy/Pandas files included: {len(numpy_files)}")
            print(f"📁 Total files in package: {sum(len(files) for _, _, files in os.walk('dist_fixed/PasswordGenerator'))}")
            
        else:
            print("❌ Fixed executable not found")
            
    except Exception as e:
        print(f"⚠️ Could not get build info: {e}")
    
    print("\n🔧 Next Steps:")
    print("1. Run 'Test_Application.bat' to verify the fix")
    print("2. If successful, use 'Start_PasswordGenerator.bat' to run normally")
    print("3. The numpy import error should now be resolved")

def main():
    """Main fixed build process."""
    print("🛠️ Password Generator - Fixed Build (Resolves Numpy Issues)")
    print("=" * 60)
    
    if not os.path.exists("main.py"):
        print("❌ main.py not found. Run from project root directory.")
        return False
    
    # Install proper dependencies
    install_dependencies()
    
    # Clean and build with fixes
    clean_build()
    create_fixed_spec()
    
    if not build_fixed():
        return False
    
    copy_files_fixed()
    create_test_script()
    create_simple_launcher()
    create_fixed_readme()
    show_fixed_results()
    
    print("\n🎉 Fixed Build Complete!")
    print("📁 Location: ./dist_fixed/")
    print("🧪 Test: Run Test_Application.bat")
    print("🚀 Use: Run Start_PasswordGenerator.bat")
    print("💡 The numpy import error should be resolved!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)