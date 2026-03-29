#!/bin/bash

echo "Installing Backend Dependencies..."
cd src/backend || exit
pip install -r requirements.txt
cd ../..

echo "Installing Frontend Dependencies..."
cd frontend || exit
npm install
cd ..

echo "Installation Complete!"
