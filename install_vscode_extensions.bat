@echo off
echo Installing VS Code Extensions for Machine Learning Development...
echo.

echo Installing Hex Editor (for binary files)...
code --install-extension ms-vscode.hexeditor

echo Installing Python Extension...
code --install-extension ms-python.python

echo Installing Jupyter Extension...
code --install-extension ms-toolsai.jupyter

echo Installing JSON Extension...
code --install-extension ms-vscode.vscode-json

echo Installing YAML Extension...
code --install-extension redhat.vscode-yaml

echo.
echo All extensions installed successfully!
echo.
echo You can now:
echo 1. Open VS Code
echo 2. Open your project folder
echo 3. View model files with Hex Editor
echo 4. Use Python for model inspection
echo.
pause
