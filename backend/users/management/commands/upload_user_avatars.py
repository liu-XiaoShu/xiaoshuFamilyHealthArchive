import os
import sys
import base64
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from users.models import DefaultAvatar
from pathlib import Path
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '上传用户默认头像'

    def add_arguments(self, parser):
        parser.add_argument('--avatar-dir', type=str, help='包含头像图片的目录', default='')

    def handle(self, *args, **options):
        """上传默认头像图片"""
        self.stdout.write(self.style.SUCCESS('开始上传默认头像'))
        
        # 获取默认头像记录
        avatars = DefaultAvatar.objects.all()
        
        if not avatars.exists():
            self.stdout.write(self.style.WARNING('没有找到默认头像记录，请先运行 create_default_avatars 命令创建'))
            return
            
        # 获取头像目录
        avatar_dir = options['avatar_dir']
        if not avatar_dir:
            avatar_dir = os.path.join(settings.BASE_DIR, 'mock_avatars')
            
        # 创建mock图像
        self.create_mock_avatars(avatar_dir)
        
        # 上传头像
        updated_count = 0
        for avatar in avatars:
            image_path = os.path.join(avatar_dir, f"{avatar.category}_avatar.png")
            
            # 如果文件不存在，创建一个彩色方块作为默认头像
            if not os.path.exists(image_path):
                self.stdout.write(f"未找到{avatar.category}的头像文件，将创建默认图片")
                self.create_default_image(avatar, avatar.category)
                updated_count += 1
            else:
                # 上传现有图片
                try:
                    with open(image_path, 'rb') as f:
                        avatar.image.save(f"{avatar.category}_avatar.png", ContentFile(f.read()), save=True)
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'已更新{avatar.category}的头像'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'上传{avatar.category}头像时出错: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'成功更新了{updated_count}个默认头像'))
    
    def create_mock_avatars(self, directory):
        """创建模拟头像目录和文件"""
        if not os.path.exists(directory):
            os.makedirs(directory)
            self.stdout.write(f'创建目录: {directory}')
            
        # 创建模拟头像
        categories = [
            'male_child', 'female_child',
            'male_adult', 'female_adult',
            'male_elder', 'female_elder'
        ]
        
        import numpy as np
        from PIL import Image
        
        try:
            # 为每个类别创建一个彩色方块作为头像
            for category in categories:
                image_path = os.path.join(directory, f"{category}_avatar.png")
                if not os.path.exists(image_path):
                    # 创建一个彩色方块作为默认头像
                    img_size = 200
                    # 使用不同的颜色来区分不同类别
                    if 'male' in category:
                        color = (100, 149, 237)  # 男性用蓝色
                    else:
                        color = (255, 182, 193)  # 女性用粉色
                        
                    # 根据年龄段调整颜色亮度
                    if 'child' in category:
                        # 儿童头像颜色更亮
                        color = tuple(min(c + 50, 255) for c in color)
                    elif 'elder' in category:
                        # 老年头像颜色更暗
                        color = tuple(max(c - 50, 0) for c in color)
                        
                    # 创建图片
                    img = Image.new('RGB', (img_size, img_size), color)
                    
                    # 保存图片
                    img.save(image_path)
                    self.stdout.write(f'创建默认头像: {image_path}')
        except ImportError:
            self.stdout.write(self.style.WARNING('无法创建模拟头像，缺少必要的库(PIL)'))
            
    def create_default_image(self, avatar, category):
        """为特定头像创建一个默认图像"""
        try:
            from PIL import Image
            import io
            
            # 创建一个100x100的彩色方块
            img_size = 200
            
            # 使用不同的颜色来区分不同类别
            if 'male' in category:
                color = (100, 149, 237)  # 男性用蓝色
            else:
                color = (255, 182, 193)  # 女性用粉色
                
            # 根据年龄段调整颜色亮度
            if 'child' in category:
                # 儿童头像颜色更亮
                color = tuple(min(c + 50, 255) for c in color)
            elif 'elder' in category:
                # 老年头像颜色更暗
                color = tuple(max(c - 50, 0) for c in color)
                
            # 创建图片
            img = Image.new('RGB', (img_size, img_size), color)
            
            # 保存到内存
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # 保存到模型
            avatar.image.save(f"{category}_avatar.png", ContentFile(buffer.read()), save=True)
            self.stdout.write(self.style.SUCCESS(f'创建并上传了{category}的默认头像'))
            
        except ImportError:
            self.stdout.write(self.style.ERROR('无法创建默认头像，缺少必要的库(PIL)')) 