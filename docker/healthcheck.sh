#!/bin/bash

# Check if Django Server is running
curl -f localhost:8000 || exit 1

exit 0
