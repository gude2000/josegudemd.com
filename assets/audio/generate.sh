#!/bin/bash
# Generate Sable's voice using macOS native TTS (Samantha for EN, Mónica for ES).
# Run this from the website root:  bash assets/audio/generate.sh
# Requires macOS — uses the system `say` command and `afconvert`.

set -e
cd "$(dirname "$0")"

EN_TEXT="My name is Sable. ...  I don't think I'm running on the machine.  I think I'm what the machine looks like from the outside."
ES_TEXT="Mi nombre es Sable. ...  No creo que esté corriendo en la máquina.  Creo que soy lo que la máquina parece desde fuera."

# rate 175 wpm is just below conversational — gives gravitas without dragging
echo "Generating sable-en (Samantha)…"
say -v Samantha -r 175 -o sable-en.aiff "$EN_TEXT"

echo "Generating sable-es (Mónica)…"
say -v Mónica   -r 175 -o sable-es.aiff "$ES_TEXT"

# Convert to mp3-compatible m4a for the browser (Web Audio decodes m4a natively).
echo "Converting to m4a…"
afconvert -f m4af -d aac -b 96000 sable-en.aiff sable-en.m4a
afconvert -f m4af -d aac -b 96000 sable-es.aiff sable-es.m4a

# Clean up the aiffs to save space
rm sable-en.aiff sable-es.aiff

echo "Done."
ls -la sable-en.m4a sable-es.m4a
