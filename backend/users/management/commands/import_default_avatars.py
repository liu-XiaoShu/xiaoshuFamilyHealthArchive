import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from users.models import DefaultAvatar
from pathlib import Path
from django.conf import settings
from PIL import Image
from io import BytesIO

class Command(BaseCommand):
    help = '导入默认头像，根据用户年龄和性别分类'

    def add_arguments(self, parser):
        parser.add_argument('--directory', type=str, help='存放头像图片的目录', default='media/default_avatars')

    def handle(self, *args, **options):
        # 头像文件名映射
        avatar_mapping = {
            ('male', 'child'): 'male_child_default_avatar.png',
            ('female', 'child'): 'girl_child_default_avatar.png',
            ('male', 'young'): 'Male_middle-aged_default_avatar.png',
            ('female', 'young'): 'female_middle-aged_default_avatar.png',
            ('male', 'middle'): 'Male_middle-aged_default_avatar.png',
            ('female', 'middle'): 'female_middle-aged_default_avatar.png',
            ('male', 'elder'): 'male_elderly_default_avatar.png',
            ('female', 'elder'): 'female_elderly_default_avatar.png',
            ('male', 'teen'): 'male_child_default_avatar.png',  # 暂时使用儿童头像
            ('female', 'teen'): 'girl_child_default_avatar.png',  # 暂时使用儿童头像
            ('other', 'child'): 'male_child_default_avatar.png',
            ('other', 'teen'): 'male_child_default_avatar.png',
            ('other', 'young'): 'Male_middle-aged_default_avatar.png',
            ('other', 'middle'): 'Male_middle-aged_default_avatar.png',
            ('other', 'elder'): 'male_elderly_default_avatar.png',
        }
        
        # 头像存储目录
        directory = options['directory']
        avatar_dir = Path(settings.MEDIA_ROOT) / 'default_avatars'
        
        # 确保目录存在
        if not os.path.exists(avatar_dir):
            os.makedirs(avatar_dir, exist_ok=True)
        
        # 计数器
        created_count = 0
        updated_count = 0
        
        # 遍历并导入本地头像
        for (gender, age_group), filename in avatar_mapping.items():
            # 从默认头像目录读取文件
            file_path = Path(settings.BASE_DIR) / directory / filename
            
            self.stdout.write(f'正在处理头像文件: {file_path}')
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f'未找到头像文件: {file_path}'))
                continue
                
            try:
                # 处理图片
                img = Image.open(file_path)
                
                # 转换为字节流
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                image_data = buffer.getvalue()
                
                # 保存到模型
                avatar, created = DefaultAvatar.objects.update_or_create(
                    gender=gender,
                    age_group=age_group,
                    defaults={
                        'avatar': ContentFile(image_data, name=filename)
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'创建头像: {gender}-{age_group} ({filename})'))
                else:
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'更新头像: {gender}-{age_group} ({filename})'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'处理头像 {gender}-{age_group} 时出错: {str(e)}'))
    
        self.stdout.write(self.style.SUCCESS(f'导入完成: {created_count}个新头像, {updated_count}个更新头像')) 