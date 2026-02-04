import PyInstaller.__main__
import shutil
import os
import live2d

# Define paths
base_dir = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(base_dir, 'dist')
build_dir = os.path.join(base_dir, 'build')
output_dir = os.path.join(dist_dir, 'LuoTianyiClient')

# Get live2d package path
live2d_path = os.path.dirname(live2d.__file__)
# We need to copy the whole live2d package to get shaders.
# Format: "source_path;dest_path" (on Windows)
add_data_live2d = f'{live2d_path};live2d'

# Clean previous build
if os.path.exists(dist_dir):
    shutil.rmtree(dist_dir)
if os.path.exists(build_dir):
    shutil.rmtree(build_dir)

# Run PyInstaller
print("Starting PyInstaller...")

PyInstaller.__main__.run([
    'main.py',
    '--name=LuoTianyiClient',
    '--onedir',
    '--noconfirm',
    '--console',  # Keep console for debug. Change to --windowed (or -w) to hide console.
    '--clean',
    # # Add hidden imports if necessary
    # '--hidden-import=PySide6',
    # '--hidden-import=live2d',
    # '--hidden-import=queue', # sometimes needed
    
    # Exclude heavy packages not used in the client
    '--exclude-module=torch',
    '--exclude-module=torchaudio',
    '--exclude-module=torchvision',
    '--exclude-module=funasr',
    '--exclude-module=modelscope',
    '--exclude-module=transformers',
    '--exclude-module=onnxruntime',
    '--exclude-module=matplotlib', # Usually only needed for plotting
    '--exclude-module=scipy.stats', # Sometimes large if not needed
    # '--exclude-module=numpy', # Needed
    # '--exclude-module=scipy', # Needed by librosa

    # Icon
    '--icon=res/gui/icon.ico',

    # Add live2d data
    f'--add-data={add_data_live2d}',
    
    # We do not bundle config and res using --add-data because we want them to remain external/editable.
    # The main.py logic handles finding them in the application directory.
])


# Copy resources to dist folder
print("Copying resources...")

# Copy config
config_src = os.path.join(base_dir, 'config')
config_dst = os.path.join(output_dir, 'config')
shutil.copytree(config_src, config_dst)
print(f"Copied config to {config_dst}")

# Copy res
res_src = os.path.join(base_dir, 'res')
res_dst = os.path.join(output_dir, 'res')
shutil.copytree(res_src, res_dst)
print(f"Copied res to {res_dst}")

# Create temp dir in output
temp_dst = os.path.join(output_dir, 'temp')
os.makedirs(temp_dst, exist_ok=True)
os.makedirs(os.path.join(temp_dst, 'tts_outputs'), exist_ok=True)
print(f"Created temp directories at {temp_dst}")

# Copy library files if needed (e.g. if live2d needs specific dlls not picked up)
# Usually PyInstaller picks up DLLs from site-packages.

print("Build complete. Executable is at:", os.path.join(output_dir, 'LuoTianyiClient.exe'))
