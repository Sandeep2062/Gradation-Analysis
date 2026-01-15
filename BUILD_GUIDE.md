# Gradation Analysis - Build & Deployment Guide

## Overview

This guide covers how to build, package, and deploy the Gradation Analysis application.

## Build Setup

### Prerequisites
- Python 3.11+
- PyInstaller
- All dependencies in `requirements.txt`

### Build Process

#### Option 1: Using the Spec File (Recommended)
```bash
pip install -r requirements.txt pyinstaller
pyinstaller GradationAnalysis.spec
```

The spec file (`GradationAnalysis.spec`) includes:
- Icon bundling from `assets/icon.ico`
- Configuration and material data inclusion
- Proper PyInstaller settings for a clean executable

#### Option 2: Direct Command
```bash
pyinstaller main.py --onefile --noconsole --name "GradationAnalysis" --icon=assets/icon.ico --add-data "assets:assets" --add-data "config:config"
```

## Assets Organization

### Assets Folder Structure
```
assets/
├── icon.ico      # Application icon (Windows executable)
└── icon.png      # Application icon (PNG format, for documentation)
```

### Icon Handling

**Development Environment:**
- Icon is loaded from `assets/icon.ico` using relative path
- Path resolution: `ui/app_window.py` → `../assets/icon.ico`

**Production (Bundled with PyInstaller):**
- Icon is embedded in the executable
- Assets are copied to the bundle using the spec file
- Runtime detection handles both environments via `sys.frozen`

### Code Reference (`ui/app_window.py`):
```python
def _set_icon(self):
    """
    Set window icon - works in both development and PyInstaller bundled environments
    """
    try:
        # Try development path first
        dev_icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
        
        # Try PyInstaller bundled path
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            bundled_icon_path = os.path.join(base_path, "assets", "icon.ico")
            if os.path.exists(bundled_icon_path):
                self.iconbitmap(bundled_icon_path)
                return
        
        if os.path.exists(dev_icon_path):
            self.iconbitmap(dev_icon_path)
            return
            
    except Exception as e:
        pass  # Silently fail if icon cannot be set
```

## GitHub Actions Workflow

### File: `.github/workflows/build.yml`

**Triggers:** Automatic build on any tag push (v*)

**Process:**
1. Checkout repository
2. Setup Python 3.11
3. Install dependencies
4. Run PyInstaller using spec file
5. Create GitHub Release with executable

**Usage:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

This automatically triggers the build and creates a release with `GradationAnalysis.exe`.

## Build Output

After building, the executable will be in:
```
dist/GradationAnalysis.exe
```

Size: Approximately 100-150 MB (includes Python runtime, matplotlib, numpy, customtkinter)

## Configuration Files

### `config/materials.py`
Contains material definitions:
- Fine Aggregate (10mm → Pan)
- Coarse Aggregate (40mm → Pan)
- Sub-Base (75mm → Pan)
- CRM for Base (45mm → Pan)

Each material includes:
- Sieve sizes (mm)
- Lower limits (%)
- Upper limits (%)
- Excel cell references for import

## Dependencies

See `requirements.txt`:
```
customtkinter     # Modern GUI framework
matplotlib        # Graphing and visualization
numpy             # Numerical computations
```

PyInstaller adds these as hidden imports in the spec file for proper bundling.

## Troubleshooting

### Icon Not Showing
- Ensure `assets/icon.ico` exists
- Icon must be 32x32 pixels minimum
- Check file permissions

### Missing Modules After Build
- Add to spec file's `hiddenimports` list
- PyInstaller sometimes misses dynamically imported modules
- Current spec includes common ones: `customtkinter`, `matplotlib.backends.backend_tkagg`, `numpy`

### Assets Not Found at Runtime
- Verify spec file includes `datas=[('assets', 'assets'), ('config', 'config')]`
- Check `sys._MEIPASS` path in bundled app
- Use the provided `_set_icon()` method pattern for other assets

## Best Practices

1. **Always use the spec file** for consistent, reliable builds
2. **Test the built executable** on a clean Windows machine
3. **Keep asset files in the `assets` folder** only
4. **Update spec file** if new assets are added
5. **Test both development and production** paths for asset loading

## Version Management

Versions are managed via Git tags:
- Format: `v#.#.#` (e.g., `v1.0.0`)
- Deploy script: `./deploy.sh` (creates tag and triggers build)

## Support

For issues with:
- **Build process**: Check PyInstaller documentation
- **Assets**: Verify folder structure and file existence
- **GitHub Actions**: Check workflow logs in Actions tab
