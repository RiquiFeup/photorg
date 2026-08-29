# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Photorg."""

a = Analysis(
    ['photorg/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'photorg.core',
        'photorg.ui',
        'pillow_heif',
        'transformers',
        'torch'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Photorg',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
