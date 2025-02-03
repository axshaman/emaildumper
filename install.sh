#!/bin/bash

set -e  # Остановка скрипта при ошибке

echo "📦 Updating system and installing dependencies..."
# sudo apt update && sudo apt install -y python3 python3-pip python3-venv p7zip-full

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден! Установите Python3 и попробуйте снова."
    exit 1
fi

echo "🚀 Setting up Python virtual environment..."
if [ ! -d "myenv" ]; then
    python3 -m venv myenv
fi

# Активация виртуального окружения
source myenv/bin/activate

# Проверяем, активировалось ли окружение
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Ошибка активации виртуального окружения!"
    exit 1
fi

echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install imapclient email-validator requests tqdm

echo "✅ Installation complete!"
echo "Run the script in manual mode:"
echo "python dumper.py --manual"
echo ""
echo "Run the script in automatic mode after editing config.ini:"
echo "nohup python dumper.py > log.txt 2>&1 &"
echo ""
echo "If you want exit from current env mode please enter: deactivate"


