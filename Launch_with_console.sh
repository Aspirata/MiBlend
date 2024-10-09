#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BLEND_FILE="$SCRIPT_DIR/MiBlend.blend"

blender "$BLEND_FILE"
