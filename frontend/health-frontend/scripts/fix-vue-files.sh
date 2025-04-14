#!/bin/bash

# 查找所有Vue文件
find src -name "*.vue" -type f | while read -r file; do
  echo "Processing $file"
  
  # 替换 <script setup lang="ts"> 为 <script setup>
  sed -i 's/<script setup lang="ts">/<script setup>/g' "$file"
  
  # 替换 import type 语句
  sed -i 's/import type/\/\/ import type/g' "$file"
  
  # 删除类型注解 (简单替换，可能不能处理所有情况)
  sed -i 's/: string//g' "$file"
  sed -i 's/: number//g' "$file"
  sed -i 's/: boolean//g' "$file"
  sed -i 's/: any//g' "$file"
  sed -i 's/: Record<[^>]*>//g' "$file"
  sed -i 's/: \[[^\]]*\]//g' "$file"
  sed -i 's/: Array<[^>]*>//g' "$file"
  sed -i 's/as [^, )]*//g' "$file"
  
  # 替换泛型ref声明
  sed -i 's/ref<[^>]*>(/ref(/g' "$file"
  sed -i 's/reactive<[^>]*>(/reactive(/g' "$file"
done
