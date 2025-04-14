#!/bin/bash

# 定义要替换的模式
PATTERN1='const props = defineProps<{'
REPLACE1='const props = defineProps({'

# 查找并修复所有Vue文件中的defineProps泛型语法
find src -name "*.vue" -type f | while read -r file; do
  if grep -q "$PATTERN1" "$file"; then
    echo "修复文件: $file"
    sed -i "s/$PATTERN1/$REPLACE1/g" "$file"
    sed -i 's/}>\(\s*\)(/}: {}\1(/g' "$file"
  fi
done

echo "完成修复defineProps语句"
