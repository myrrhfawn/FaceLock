# -*- mode: python ; coding: utf-8 -*-

import os, sys
from PyQt5.QtCore import QLibraryInfo

project_root = os.path.abspath(os.path.dirname(sys.argv[0]))
app_path = os.path.join(project_root, 'app')
icon_path = os.path.join(project_root, 'components', 'src', 'app_icon.png')


a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
            ("detector/models/shape_predictor_68_face_landmarks.dat", "detector/models"),
            ("detector/models/dlib_face_recognition_resnet_model_v1.dat", "detector/models"),
            ("components/src/app_icon.png", "components/src/file_icons"),
            ("components/src/file_icons/file.png", "components/src/file_icons"),
            ("components/src/file_icons/not-found.png", "components/src/file_icons"),
            ("components/src/file_icons/encrypted-file.png", "components/src/file_icons"),
            ("components/src/file_icons/image-file.png", "components/src/file_icons"),
            ("components/src/file_icons/txt-file.png", "components/src/file_icons"),
            ("components/src/file_icons/pdf-file.png", "components/src/file_icons"),
            ("components/src/file_icons/archive-file.png", "components/src/file_icons"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
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
    icon=icon_path,
)
