# VS Code Setup for Machine Learning Model Files

## 🔧 Extensions to Install

### Required Extensions for Model Files:
```bash
# Install these extensions in VS Code:
code --install-extension ms-vscode.hexeditor
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
```

### Recommended Extensions:
```bash
# Additional helpful extensions:
code --install-extension ms-vscode.vscode-json
code --install-extension redhat.vscode-yaml
code --install-extension ms-vscode.powershell
```

## 📁 File Associations Added

The following file types are now properly configured in `.vscode/settings.json`:

### Model Files:
- `*.joblib` → Binary format
- `*.pkl` → Binary format  
- `*.pickle` → Binary format
- `*.model` → Binary format
- `*.h5` → Binary format
- `*.pb` → Binary format
- `*.onnx` → Binary format
- `*.pt` → Binary format
- `*.pth` → Binary format

## 🔍 Model Inspector Tool

### Usage:
```bash
# Run the model inspector:
python model_inspector.py

# Or with virtual environment:
cd venv/Scripts
python ../../model_inspector.py
```

### Features:
- ✅ Finds all model files automatically
- ✅ Inspects model metadata
- ✅ Generates model information JSON
- ✅ Creates readable summary markdown
- ✅ Shows file sizes and formats

## 📊 Found Model Files

The inspector found **9 model files** in your project:

1. `dropout_model_simple.joblib` - Dropout prediction model
2. `dropout_scaler_simple.joblib` - Feature scaler for dropout model
3. `model_fixed.joblib` - Fixed compatibility model
4. `my_model.joblib` - Custom trained model
5. `scaler_fixed.joblib` - Fixed compatibility scaler
6. `models/classification_model.joblib` - Classification model
7. `models/dropout_model.joblib` - Dropout model
8. `models/regression_model.joblib` - Regression model
9. `models/scaler.joblib` - Feature scaler

## 🛠️ VS Code Configuration

### Settings Added:
- File associations for binary model files
- Python interpreter path
- Jupyter integration
- File nesting for related files
- Search exclusions for venv and cache

### File Nesting:
- `*.py` → nests with `*.pyc`, `*.pyi`, `__pycache__/`
- `*.joblib` → nests with `*.joblib.meta`
- `*.pkl` → nests with `*.pkl.meta`

## 📖 How to View Model Files

### Method 1: Hex Editor Extension
1. Right-click on `.joblib` or `.pkl` file
2. Select "Open with Hex Editor"
3. View binary content safely

### Method 2: Model Inspector Tool
1. Run `python model_inspector.py`
2. Choose detailed inspection option
3. Get structured model information

### Method 3: Python Script
```python
import joblib
model = joblib.load('your_model.joblib')
print(model)
```

## ⚠️ Important Notes

### Binary File Handling:
- Never edit binary files directly in text editor
- Use proper tools for inspection
- Backup models before modifications

### Version Compatibility:
- Models trained with older scikit-learn may show warnings
- Use fixed versions (`*_fixed.joblib`) for compatibility
- Retrain models if needed for current environment

## 🚀 Quick Start

1. **Install Extensions:**
   ```bash
   code --install-extension ms-vscode.hexeditor
   code --install-extension ms-python.python
   ```

2. **Open Project:**
   ```bash
   code .
   ```

3. **Run Model Inspector:**
   ```bash
   python model_inspector.py
   ```

4. **View Model Files:**
   - Right-click → "Open with Hex Editor"
   - Or use the inspector tool

## 📞 Support

If you encounter issues:
1. Check VS Code extensions are installed
2. Ensure Python interpreter is correctly set
3. Run model inspector for diagnostics
4. Check file permissions

---

**🎉 Your VS Code is now configured for machine learning model development!**
