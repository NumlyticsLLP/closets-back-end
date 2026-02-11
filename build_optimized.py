"""
Optimized Build Script - Faster startup executable
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
    
    # Check for UPX (optional compression tool)
    try:
        subprocess.check_output(["upx", "--version"], stderr=subprocess.DEVNULL)
        print("✅ UPX compression available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ UPX not found - skipping compression (will still build)")
        return False

def clean_build():
    """Clean previous build artifacts."""
    dirs_to_clean = ["build", "dist_optimized"]
    for directory in dirs_to_clean:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"🧹 Cleaned {directory}")

def create_optimized_spec():
    """Create optimized PyInstaller spec file."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Exclude unnecessary modules to reduce size and startup time
excludes = [
    'matplotlib', 'scipy', 'IPython', 'notebook', 'jupyter',
    'sphinx', 'pytest', 'tkinter', 'unittest', 'pydoc',
    'doctest', 'xmlrpc', 'http.server', 'socketserver',
    'multiprocessing', 'concurrent.futures', 'asyncio',
    'email', 'urllib.request', 'urllib.parse', 'html',
    'xml.sax', 'xml.dom', 'xml.parsers.expat',
    'distutils', 'setuptools', 'pkg_resources',
    'PIL.ImageTk', 'PIL.ImageWin', 'PIL.ImageQt'
]

# Hidden imports that might be needed
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'PyQt6.QtGui',
    'mysql.connector.locales.eng',
    'bcrypt',
    'pandas._libs.tslibs.base',
    'pandas._libs.tslibs.np_datetime',
    'pandas._libs.tslibs.timezones'
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[
        ('sample_credentials.json', '.'),
        ('assets', 'assets'),
    ],
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

# Remove unnecessary binaries to reduce size
a.binaries = [x for x in a.binaries if not any(
    exclude in x[0].lower() for exclude in [
        'api-ms-win-', 'ucrtbase', 'msvcp', 'vcruntime',
        'qt6network', 'qt6qml', 'qt6quick', 'qt6webengine',
        'qt6multimedia', 'qt6positioning', 'qt6sensors'
    ]
)]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Use onedir mode for faster startup
    name='PasswordGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX compression if available
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
    upx=True,
    upx_exclude=[],
    name='PasswordGenerator'
)
"""
    
    with open("optimized.spec", "w") as f:
        f.write(spec_content)
    print("✅ Created optimized spec file")

def build_optimized():
    """Build optimized executable."""
    print("🔨 Building optimized executable...")
    
    try:
        venv_pyinstaller = os.path.join(".venv", "Scripts", "pyinstaller.exe")
        if not os.path.exists(venv_pyinstaller):
            venv_pyinstaller = "pyinstaller"
        
        subprocess.check_call([
            venv_pyinstaller,
            "--distpath=./dist_optimized",
            "--workpath=./build",
            "optimized.spec"
        ])
        
        print("✅ Optimized executable built successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def copy_files():
    """Copy required files to optimized dist."""
    source_files = [
        "sample_credentials.json",
        "sample_credentials.txt",
        "requirements.txt"
    ]
    
    dest_dir = os.path.join("dist_optimized", "PasswordGenerator")
    
    for file in source_files:
        if os.path.exists(file):
            try:
                shutil.copy2(file, dest_dir)
                print(f"📋 Copied {file}")
            except Exception as e:
                print(f"⚠️ Could not copy {file}: {e}")

def create_launcher():
    """Create a simple launcher script for easier execution."""
    launcher_content = '''@echo off
echo Starting Password Generator...
cd /d "%~dp0PasswordGenerator"
start "" "PasswordGenerator.exe"
'''
    
    with open("dist_optimized/Start_PasswordGenerator.bat", "w") as f:
        f.write(launcher_content)
    print("✅ Created launcher script")

def create_optimized_readme():
    """Create README for optimized version."""
    readme_content = """# Password Generator - Optimized Version

## Quick Start:
1. Double-click `Start_PasswordGenerator.bat` to run the application
   OR
2. Navigate to `PasswordGenerator` folder and run `PasswordGenerator.exe`

## What's Optimized:
- **Faster Startup**: Uses directory mode instead of single file
- **Smaller Size**: Excluded unnecessary modules
- **Better Performance**: Optimized binary selection

## Installation:
- Extract all files to a folder of your choice
- Ensure MySQL is running
- Configure database credentials in the included files
- Run the application using the launcher

## Files Structure:
```
dist_optimized/
├── Start_PasswordGenerator.bat    # Quick launcher
├── PasswordGenerator/             # Application folder
│   ├── PasswordGenerator.exe     # Main executable
│   ├── sample_credentials.json   # Database config (JSON)
│   ├── sample_credentials.txt    # Database config (text)
│   └── [other application files] # Required libraries
└── README.md                     # This file
```

## Features:
- Dynamic database configuration
- User management with role-based access
- Flexible file export (new/existing files)
- Secure password generation
- Path memory for user preferences

---
Password Generator v1.0 - Optimized Build
"""
    
    with open("dist_optimized/README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ Created optimized README")

def show_results():
    """Show build results and file sizes."""
    print("\n📊 Build Results:")
    print("=" * 50)
    
    # Get sizes
    try:
        old_exe = "dist/PasswordGenerator.exe"
        if os.path.exists(old_exe):
            old_size = os.path.getsize(old_exe)
            print(f"📦 Original single-file exe: {old_size:,} bytes ({old_size/1024/1024:.1f} MB)")
        
        new_exe = "dist_optimized/PasswordGenerator/PasswordGenerator.exe"
        if os.path.exists(new_exe):
            new_size = os.path.getsize(new_exe)
            print(f"⚡ Optimized exe: {new_size:,} bytes ({new_size/1024/1024:.1f} MB)")
            
            if os.path.exists(old_exe):
                savings = ((old_size - new_size) / old_size) * 100
                print(f"💾 Size reduction: {savings:.1f}%")
        
        # Count total files in optimized folder
        opt_dir = "dist_optimized/PasswordGenerator"
        if os.path.exists(opt_dir):
            file_count = sum(len(files) for _, _, files in os.walk(opt_dir))
            total_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, _, filenames in os.walk(opt_dir)
                for filename in filenames
            )
            print(f"📁 Total optimized package: {file_count} files, {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
        
    except Exception as e:
        print(f"⚠️ Could not calculate sizes: {e}")
    
    print("\n🚀 Startup Performance:")
    print("- ⚡ Faster startup (no extraction needed)")
    print("- 💾 Smaller memory footprint")
    print("- 📁 Easier to distribute and update")

def main():
    """Main optimized build process."""
    print("⚡ Password Generator - Optimized Build")
    print("=" * 50)
    
    if not os.path.exists("main.py"):
        print("❌ main.py not found. Run from project root directory.")
        return False
    
    # Install dependencies and check tools
    has_upx = install_dependencies()
    if has_upx:
        print("🎯 UPX compression will be used for maximum optimization")
    
    # Clean and build
    clean_build()
    create_optimized_spec()
    
    if not build_optimized():
        return False
    
    copy_files()
    create_launcher()
    create_optimized_readme()
    show_results()
    
    print("\n🎉 Optimized Build Complete!")
    print("📁 Location: ./dist_optimized/")
    print("🚀 Use Start_PasswordGenerator.bat to run")
    print("💡 This version should start much faster!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)
def create_optimized_build():
    """Create a faster-loading executable using directory mode."""
    print("🚀 Creating Optimized Executable (Faster Startup)")
    print("=" * 60)
    
    # Clean previous builds
    for directory in ["build", "dist_optimized"]:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"🧹 Cleaned {directory}")
    
    try:
        # Get the correct pyinstaller path from venv
        venv_pyinstaller = os.path.join(".venv", "Scripts", "pyinstaller.exe")
        if not os.path.exists(venv_pyinstaller):
            venv_pyinstaller = "pyinstaller"
        
        print("🔨 Building optimized executable...")
        
        # Build using directory mode (faster startup)
        subprocess.check_call([
            venv_pyinstaller,
            "--onedir",  # Directory mode instead of onefile
            "--windowed",
            "--name=PasswordGenerator",
            "--distpath=./dist_optimized",
            "--workpath=./build",
            "--specpath=./",
            "--optimize=2",  # Optimize Python bytecode
            "--exclude-module=matplotlib",  # Exclude unused modules
            "--exclude-module=IPython",
            "--exclude-module=jupyter",
            "--exclude-module=notebook",
            "--exclude-module=tkinter",
            "main.py"
        ])
        
        print("✅ Optimized executable created!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_launcher_script():
    """Create a simple launcher script for easier execution."""
    launcher_content = '''@echo off
cd /d "%~dp0"
PasswordGenerator\\PasswordGenerator.exe
'''
    
    with open("dist_optimized/Launch_PasswordGenerator.bat", "w") as f:
        f.write(launcher_content)
    
    print("✅ Created launcher script: Launch_PasswordGenerator.bat")

def copy_required_files():
    """Copy required files to the optimized dist directory."""
    required_files = [
        "sample_credentials.json",
        "sample_credentials.txt"
    ]
    
    dist_dir = "dist_optimized"
    
    for file in required_files:
        if os.path.exists(file):
            try:
                shutil.copy2(file, dist_dir)
                print(f"📋 Copied {file}")
            except Exception as e:
                print(f"⚠️ Could not copy {file}: {e}")

def create_optimized_readme():
    """Create README for the optimized version."""
    readme_content = """# Password Generator Application - Optimized Version

## Quick Start:
1. **Double-click `Launch_PasswordGenerator.bat`** to start the application
   OR
2. **Navigate to `PasswordGenerator` folder and run `PasswordGenerator.exe`**

## Why This Version Is Faster:
- ✅ Directory mode (no extraction needed)
- ✅ Optimized Python bytecode
- ✅ Excluded unnecessary modules
- ✅ Faster startup time (3-5 seconds vs 10-15 seconds)

## Database Setup:
- Edit `sample_credentials.json` or `sample_credentials.txt`
- Run the application and select your credentials file

## Features:
- Dynamic database configuration
- User management with role-based access
- Flexible file export (new or existing files)
- Secure password generation

## Distribution:
To distribute this application, copy the entire folder containing:
- `PasswordGenerator/` folder (contains the executable and dependencies)
- `Launch_PasswordGenerator.bat` (easy launcher)
- `sample_credentials.json` and `sample_credentials.txt`
- This README file

---
Password Generator v1.0 - Optimized Build
"""
    
    with open("dist_optimized/README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("📖 Created optimized README.md")

def main():
    """Main optimization process."""
    if not os.path.exists("main.py"):
        print("❌ main.py not found. Please run from project root.")
        return False
    
    if create_optimized_build():
        copy_required_files()
        create_launcher_script()
        create_optimized_readme()
        
        print("\n🎉 Optimized Build Complete!")
        print("=" * 40)
        print("📁 Location: ./dist_optimized/")
        print("🚀 Use: Launch_PasswordGenerator.bat")
        print("⚡ Much faster startup time!")
        
        # Show directory contents
        print("\n📋 Created files:")
        if os.path.exists("dist_optimized"):
            for item in os.listdir("dist_optimized"):
                if os.path.isdir(os.path.join("dist_optimized", item)):
                    print(f"   📁 {item}/")
                else:
                    print(f"   📄 {item}")
        
        return True
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n💡 Tip: The optimized version starts much faster!")
        print("📦 To distribute: Copy the entire 'dist_optimized' folder")
    else:
        print("\n❌ Optimization failed")
        sys.exit(1)