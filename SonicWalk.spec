# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['C:\\Users\\rober\\Desktop\\MainFolder\\CodingProjects\\SonicWalk\\SonicWalk\\SonicWalk.py'],
    pathex=['C:\\Users\\rober\\Desktop\\MainFolder\\CodingProjects\\SonicWalk\\SonicWalk', 'C:\\Users\\rober\\miniconda3\\envs\\sonicwalk2\\Lib\\site-packages'],
    binaries=[],
    datas=[
        ('C:\\Users\\rober\\miniconda3\\envs\\sonicwalk2\\Lib\\site-packages\\xsensdeviceapi', 'xsensdeviceapi'),
    ],
    hiddenimports=['xsensdeviceapi', 'matplotlib.animation', 'scipy', 'scipy.ndimage'],
    hookspath=['C:\\Users\\rober\\miniconda3\\envs\\sonicwalk2\\Lib\\site-packages\\xsensdeviceapi'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SonicWalk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\rober\\Desktop\\MainFolder\\CodingProjects\\SonicWalk\\SonicWalk\\GUI\\icons\\SonicWalk_logo.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SonicWalk',
)
