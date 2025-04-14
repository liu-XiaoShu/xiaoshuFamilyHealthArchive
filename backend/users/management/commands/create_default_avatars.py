import os
import sys
import base64
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from users.models import DefaultAvatar
from pathlib import Path
from django.conf import settings
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '创建默认头像记录'

    def handle(self, *args, **options):
        """创建默认头像记录"""
        self.stdout.write(self.style.SUCCESS('开始创建默认头像记录'))
        
        # 定义头像类别
        categories = [
            'male_child', 'female_child',
            'male_adult', 'female_adult',
            'male_elder', 'female_elder'
        ]
        
        # 创建或更新默认头像记录
        created_count = 0
        updated_count = 0
        
        for category in categories:
            avatar, created = DefaultAvatar.objects.get_or_create(
                category=category,
                defaults={
                    'display_name': self.get_display_name(category),
                    'description': self.get_description(category),
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'创建了新的头像记录: {category}'))
            else:
                updated_count += 1
                self.stdout.write(f'头像记录已存在: {category}')
        
        summary = f'成功创建了{created_count}个新头像记录，找到{updated_count}个现有记录'
        self.stdout.write(self.style.SUCCESS(summary))
        
        # 提示下一步操作
        self.stdout.write('\n要上传头像图片，请运行: python manage.py upload_user_avatars')
    
    def get_display_name(self, category):
        """根据类别获取显示名称"""
        display_names = {
            'male_child': '男孩头像',
            'female_child': '女孩头像',
            'male_adult': '男性头像',
            'female_adult': '女性头像',
            'male_elder': '老年男性头像',
            'female_elder': '老年女性头像'
        }
        return display_names.get(category, f'{category}头像')
    
    def get_description(self, category):
        """根据类别获取描述"""
        descriptions = {
            'male_child': '适用于0-14岁男孩的默认头像',
            'female_child': '适用于0-14岁女孩的默认头像',
            'male_adult': '适用于15-64岁男性的默认头像',
            'female_adult': '适用于15-64岁女性的默认头像',
            'male_elder': '适用于65岁以上老年男性的默认头像',
            'female_elder': '适用于65岁以上老年女性的默认头像'
        }
        return descriptions.get(category, f'{category}的默认头像')
