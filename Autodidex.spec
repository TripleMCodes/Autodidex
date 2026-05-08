# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect data files for packages that need them
datas = []

# Collect PySide6 data
datas += collect_data_files('PySide6')

# Collect nltk data
datas += collect_data_files('nltk')

# Add your project's data files/directories
datas += [
    ('Icons', 'Icons'),
    ('cirillo files', 'cirillo files'),
    ('dashboard files', 'dashboard files'),
    ('habit tracker files', 'habit tracker files'),
    ('noteworthy files', 'noteworthy files'),
    ('calendar files', 'calendar files'),
    ('v tab files', 'v tab files'),
    ('spaceinvader', 'spaceinvader'),
    ('themes files', 'themes files'),
    ('cache dir', 'cache dir'),
]

# Collect hidden imports
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'pygame',
    'nltk',
    'spellchecker',
    'markdown',
    'pyspellchecker',
    'matplotlib',
    'matplotlib.backends.backend_qt5agg',
]

a = Analysis(
    ['v_tabs.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=['PyQt5', 'PyQt6', 'tkinter'],
    win_private_assemblies=False,
    win_no_prefer_redirects=False,
    cipher=None,
    noarchive=False,
    excludes=[
    "PyQt5",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
]
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Autodidex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Icons/icons8-brain-64.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Autodidex',
)
