#!/bin/bash

echo "📦 Updating system and installing dependencies..."
# sudo apt update && sudo apt install -y python3 python3-pip python3-venv p7zip-full

echo "🚀 Setting up Python virtual environment..."
python3 -m venv myenv
source myenv/bin/activate

echo "📥 Installing Python dependencies..."
pip install imapclient email-validator requests tqdm

echo "✅ Installation complete! Run the script with manual mode:"
echo "python dumper.py --manual"
echo "Run the script with automatical mode after edit config.ini"
echo "nohup python dumper.py > log.txt 2>&1 &"