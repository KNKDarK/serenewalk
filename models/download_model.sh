#!/bin/bash

# Create models directory
mkdir -p models

# Download Phi-3 Mini 4K Instruct (Q4_K_M quantization - ~280MB)
echo "Downloading Phi-3 Mini model (~280MB)..."
curl -L -o models/phi-3-mini-4k-instruct-q4_0.gguf \
  https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4_0.gguf

echo "Model downloaded successfully to models/"
