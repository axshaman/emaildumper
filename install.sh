#!/bin/bash

echo "📦 Updating system and installing dependencies..."
sudo apt update && sudo apt install -y python3 python3-pip python3-venv p7zip-full

echo "🚀 Setting up Python virtual environment..."
python3 -m venv myenv
source myenv/bin/activate

echo "📥 Installing Python dependencies..."
pip install imapclient email-validator requests tqdm

echo "📂 Cloning or downloading the script..."
# If hosted on GitHub:
git clone https://github.com/axshaman/emaildumper.git
cd emaildumper

echo "✅ Installation complete! Run the script with:"
echo "   python dumper.py"