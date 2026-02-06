#!/bin/bash

# Set the log file
LOG_FILE="log.txt"
exec > >(tee -a "$LOG_FILE") 2>&1  # Redirect both stdout and stderr to log.txt

# Log start time
echo "==============================="
echo "Script started at: $(date)"
echo "==============================="

# Activate the Conda environment
echo "Activating Conda environment 'lty'..."
source D:/Anaconda/etc/profile.d/conda.sh  # Adjust the path if necessary
conda activate lty_c

if [ $? -ne 0 ]; then
    echo "Failed to activate Conda environment. Exiting."
    exit 1
fi

# Empty the target folder in the parent directory
TARGET_FOLDER="./bin"
echo "Clearing contents of '$TARGET_FOLDER'..."

if [ -d "$TARGET_FOLDER" ]; then
    rm -rf "$TARGET_FOLDER"/*
    echo "Contents of '$TARGET_FOLDER' have been removed."
else
    echo "Error: Folder '$TARGET_FOLDER' does not exist. Creating it..."
    mkdir -p "$TARGET_FOLDER"
fi

# Run the PyInstaller command with the -y option to force output directory removal
echo "Running PyInstaller..."
# pyinstaller -i res/app_icon.ico -n "Tac3D Desktop" -D -y Tac3D_Desktop.py
pyinstaller -i res/gui/icon.ico -n "Chat with Luotianyi" -D -y main.py --add-data="D:\Anaconda\envs\lty_c\lib\site-packages\live2d;live2d"

# Check if the PyInstaller command was successful
if [ $? -ne 0 ]; then
    echo "PyInstaller command failed. Exiting."
    exit 1
fi

# Define the source folder
DIST_FOLDER="dist/Chat with Luotianyi"

# Verify that the source folder exists
if [ ! -d "$DIST_FOLDER" ]; then
    echo "Error: '$DIST_FOLDER' does not exist. Exiting."
    exit 1
fi

# Copy required files and folders to the target folder
echo "Copying files and folders to '$TARGET_FOLDER'..."
cp -r "$DIST_FOLDER/_internal" "$TARGET_FOLDER/"
cp "$DIST_FOLDER/Chat with Luotianyi.exe" "$TARGET_FOLDER/"

# Copy config and res folders if they exist
if [ -d "config" ]; then
    cp -r "config" "$TARGET_FOLDER/"
fi  
if [ -d "res" ]; then
    cp -r "res" "$TARGET_FOLDER/"
fi

# Log completion time
echo "==============================="
echo "Script finished at: $(date)"
echo "==============================="
