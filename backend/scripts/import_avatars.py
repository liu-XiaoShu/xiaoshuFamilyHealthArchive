#!/usr/bin/env python
"""
从媒体目录导入默认头像并处理水印
"""

import os
import sys
import django
from pathlib import Path

# 设置Django环境
# 调整路径，确保能导入Django配置
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from PIL import Image
from io import BytesIO
from django.conf import settings
from users.models import DefaultAvatar
from django.core.files.base import ContentFile

def import_avatars():
    """导入默认头像"""
    # 头像类别与文件名映射
    avatar_mapping = DefaultAvatar.AVATAR_FILE_NAMES
    
    # 头像源目录
    source_dir = Path(settings.BASE_DIR) / 'media' / 'default_avatars'
    
    if not source_dir.exists():
        print(f"找不到头像源目录: {source_dir}")
        return
    
    # 统计信息
    created = 0
    updated = 0
    errors = 0
    
    for category, filename in avatar_mapping.items():
        file_path = source_dir / filename
        
        if not file_path.exists():
            print(f"警告: 找不到文件 {filename}")
            continue
        
        try:
            # 打开并处理图片
            img = Image.open(file_path)
            
            # 裁剪底部水印部分
            width, height = img.size
            crop_height = int(height * 0.95)  # 裁剪底部5%
            img = img.crop((0, 0, width, crop_height))
            
            # 转换为字节流
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            image_data = buffer.getvalue()
            
            # 保存到模型
            avatar, is_created = DefaultAvatar.objects.update_or_create(
                category=category,
                defaults={
                    'description': f"默认{dict(DefaultAvatar.AVATAR_CATEGORIES).get(category)}头像"
                }
            )
            
            # 更新图片文件
            avatar.image.save(filename, ContentFile(image_data), save=True)
            
            if is_created:
                created += 1
                print(f"创建头像: {category} ({filename})")
            else:
                updated += 1
                print(f"更新头像: {category} ({filename})")
                
        except Exception as e:
            errors += 1
            print(f"错误: 处理头像 {category} 时出错: {str(e)}")
    
    print(f"\n导入完成: {created} 个新头像, {updated} 个更新头像, {errors} 个错误")

if __name__ == "__main__":
    print("开始导入默认头像...")
    import_avatars()
    print("导入完成。")
