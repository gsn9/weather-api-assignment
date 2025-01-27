#!/bin/bash

# Variables
LAMBDA_ZIP="lambda_function.zip"
LAYER_ZIP="lambda_layer.zip"
APP_DIR="app"
LAYER_DIR="python"
REQUIREMENTS_FILE="requirements.txt"
PYTHON_VERSION="python3.9"

# Clean up existing files
echo "Cleaning up old deployment artifacts..."
rm -f $LAMBDA_ZIP $LAYER_ZIP
rm -rf $LAYER_DIR

# Step 1: Package Lambda Function Code
echo "Packaging Lambda function code..."
cd $APP_DIR || exit
zip -r ../$LAMBDA_ZIP . -x "__pycache__/*" "*.DS_Store"
cd - || exit
echo "Lambda function packaged as $LAMBDA_ZIP"

# Step 2: Package Lambda Layer
echo "Creating Lambda layer package..."
mkdir -p $LAYER_DIR/lib/$PYTHON_VERSION/site-packages
pip install -r $REQUIREMENTS_FILE -t $LAYER_DIR/lib/$PYTHON_VERSION/site-packages
zip -r $LAYER_ZIP $LAYER_DIR
rm -rf $LAYER_DIR
echo "Lambda layer packaged as $LAYER_ZIP"

echo "Build process completed!"
