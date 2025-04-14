#!/bin/bash
find src -name "*.vue" -type f -exec sed -i "s/import \* \+from/import * as recordsApi from/g" {} \;
echo "完成修复import语句"
