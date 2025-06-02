source ~/fl_venv/bin/activate
export QT_QPA_PLATFORM_PLUGIN_PATH=$VIRTUAL_ENV/lib/python3.10/site-packages/PyQt5/Qt5/plugins/platforms
pyinstaller main.spec
