#!/bin/bash

# Set global character limit for truncated output files
CHAR_LIMIT=1000

# Clean up previous test artifacts
sudo rm -rf data stdout.txt tmp

# Set up directories
bash setup_dirs.sh > stdout.txt

echo "-------------------TESTING-------------------" >> stdout.txt

# Run the test command which will now include summarization
bash run.sh test >> stdout.txt

# Check if summaries were created
echo "-------------------SUMMARY CHECK-------------------" >> stdout.txt
find data/output/summaries -type f -name "*.summary.txt" | wc -l >> stdout.txt 2>&1
find data/output/summaries -type f -name "*.summary.txt" | head -n 5 >> stdout.txt 2>&1

# NEW STEP: Enhance dependencies with summaries
echo "-------------------ENHANCING DEPENDENCIES-------------------" >> stdout.txt
# Create enhanced dependencies directory
mkdir -p data/output/enhanced_dependencies

# Find the most recent minimal dependency file
DEPS_MIN_FILE=$(find data/output/dependencies -name "deps_min_*.json" | sort | tail -n 1)

# Run the enhancement script from the libs directory
TIMESTAMP=$(date +%s)
ENHANCED_DEPS_FILE="data/output/enhanced_dependencies/deps_enhanced_${TIMESTAMP}.json"
bash run.sh python -c "import sys; sys.path.insert(0, 'libs'); import enhance_dependencies; enhance_dependencies.enhance_dependencies('$DEPS_MIN_FILE', 'data/output/summaries', '$ENHANCED_DEPS_FILE')" >> stdout.txt 2>&1

echo "Enhanced dependencies saved to $ENHANCED_DEPS_FILE" >> stdout.txt

# Create temp directory for file copies
echo "-------------------PREPARING TMP DIRECTORY-------------------" >> stdout.txt
rm -rf tmp
mkdir -p tmp

# 1. Copy and truncate files from data/output/*/* (dependencies, abbreviations, summaries)
# NOTE: Only these files are truncated to the character limit
echo "Copying and truncating output files..." >> stdout.txt
find data/output -path "data/output/*/*" -type f | while read file; do
  # Replace path separators with underscores for the destination filename
  dest_file=$(echo "$file" | sed 's/\//_/g')
  
  # TRUNCATE: Apply character limit to output files
  head -c $CHAR_LIMIT "$file" > "tmp/$dest_file"
  
  echo "Copied and truncated: $file -> tmp/$dest_file" >> stdout.txt
done

# 2. Copy .py and .sql files from libs/ (excluding libs/prompts/)
# NOTE: These files are copied in full, without truncation
echo "Copying library files (no truncation)..." >> stdout.txt
find libs \( -name "*.py" -o -name "*.sql" \) | grep -v "libs/prompts" | while read file; do
  # Replace path separators with underscores for the destination filename
  dest_file=$(echo "$file" | sed 's/\//_/g')
  
  # NO TRUNCATION: Copy the complete file
  cp "$file" "tmp/$dest_file"
  
  echo "Copied (full): $file -> tmp/$dest_file" >> stdout.txt
done

# 3. Copy .md, .txt, .sh, .py files from root directory
# NOTE: These files are copied in full, without truncation
echo "Copying root files (no truncation)..." >> stdout.txt
find . -maxdepth 1 \( -name "*.md" -o -name "*.txt" -o -name "*.sh" -o -name "*.py" \) | while read file; do
  # Get just the filename (remove ./ prefix)
  filename=$(basename "$file")
  
  # NO TRUNCATION: Copy the complete file
  cp "$file" "tmp/$filename"
  
  echo "Copied (full): $file -> tmp/$filename" >> stdout.txt
done

echo "All files copied to tmp/ directory" >> stdout.txt
echo "Total files in tmp/: $(ls tmp | wc -l)" >> stdout.txt
echo "Truncation only applied to data/output/*/* files (limit: $CHAR_LIMIT chars)" >> stdout.txt