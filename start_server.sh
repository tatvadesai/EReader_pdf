#!/bin/bash

# Create a copy of index.html with API key injected
cp index.html index_with_api.html
sed -i "s/GEMINI_API_KEY_PLACEHOLDER/$GEMINI_API_KEY/g" index_with_api.html

# Start simple HTTP server
python3 -m http.server 5000 --bind 0.0.0.0