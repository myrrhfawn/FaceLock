#!/bin/bash
set -e

APP_NAME="FaceLock"
INSTALL_DIR="/opt/facelock"
ICON_PATH="/usr/share/icons/facelock.png"
DESKTOP_ENTRY="/usr/share/applications/facelock.desktop"
MIME_XML="/usr/share/mime/packages/facelock.xml"
BIN_LINK="/usr/local/bin/facelock"

echo "Installing $APP_NAME..."

sudo mkdir -p "$INSTALL_DIR"
sudo cp ./dist/main "$INSTALL_DIR/$APP_NAME"
sudo chmod +x "$INSTALL_DIR/$APP_NAME"
sudo cp ./components/src/app_icon.png "$ICON_PATH"

echo "Writing .desktop entry..."
cat <<EOF | sudo tee "$DESKTOP_ENTRY"
[Desktop Entry]
Type=Application
Name=$APP_NAME
Exec=$INSTALL_DIR/$APP_NAME %f
Icon=$ICON_PATH
Terminal=false
Categories=Utility;Security;
StartupNotify=true
MimeType=application/x-facelock;
EOF

echo "Linking binary to /usr/local/bin..."
sudo ln -sf "$INSTALL_DIR/$APP_NAME" "$BIN_LINK"

echo "Registering custom MIME type..."
cat <<EOF | sudo tee "$MIME_XML"
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns='http://www.freedesktop.org/standards/shared-mime-info'>
  <mime-type type="application/x-facelock">
    <comment>FaceLock Encrypted File</comment>
    <glob pattern="*.fl"/>
  </mime-type>
</mime-info>
EOF

sudo update-mime-database /usr/share/mime
sudo update-desktop-database

echo "Done. You can now open .fl files with $APP_NAME!"
