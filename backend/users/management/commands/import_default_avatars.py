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
import requests

class Command(BaseCommand):
    help = '导入默认头像，根据用户年龄和性别分类'

    def add_arguments(self, parser):
        parser.add_argument('--directory', type=str, help='存放头像图片的目录', default='media/default_avatars')
        parser.add_argument('--source', type=str, help='头像来源：local(本地文件)或url(网址)', default='local')
        parser.add_argument('--data', type=str, help='头像数据，可以是本地路径或URL列表(逗号分隔)', default=None)
    
    def handle(self, *args, **options):
        # 使用模型中定义的头像文件名映射
        avatar_categories = {
            'male_child': DefaultAvatar.AVATAR_FILE_NAMES['male_child'],
            'female_child': DefaultAvatar.AVATAR_FILE_NAMES['female_child'],
            'male_adult': DefaultAvatar.AVATAR_FILE_NAMES['male_adult'],
            'female_adult': DefaultAvatar.AVATAR_FILE_NAMES['female_adult'],
            'male_elder': DefaultAvatar.AVATAR_FILE_NAMES['male_elder'],
            'female_elder': DefaultAvatar.AVATAR_FILE_NAMES['female_elder'],
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
        
        # 处理来源选项
        source = options['source']
        data = options['data']
        
        if source == 'url' and data:
            # 从URL导入头像
            urls = data.split(',')
            if len(urls) != len(avatar_categories):
                raise CommandError(f"URL数量({len(urls)})与头像类别数量({len(avatar_categories)})不匹配")
                
            # 使用提供的URL下载头像
            for i, (category, _) in enumerate(avatar_categories.items()):
                url = urls[i].strip()
                self.stdout.write(f"从 {url} 下载 {category} 头像...")
                
                try:
                    # 下载图片
                    response = requests.get(url, stream=True)
                    if response.status_code == 200:
                        # 保存为临时文件
                        img = Image.open(BytesIO(response.content))
                        
                        # 裁剪水印
                        width, height = img.size
                        crop_height = int(height * 0.95)  # 裁剪底部5%
                        img = img.crop((0, 0, width, crop_height))
                        
                        # 转换为字节流
                        buffer = BytesIO()
                        img.save(buffer, format="PNG")
                        image_data = buffer.getvalue()
                        
                        # 保存到模型
                        avatar, created = DefaultAvatar.objects.update_or_create(
                            category=category,
                            defaults={
                                'description': f"默认{dict(DefaultAvatar.AVATAR_CATEGORIES).get(category)}头像"
                            }
                        )
                        
                        # 更新图片文件
                        avatar.image.save(avatar_categories[category], ContentFile(image_data), save=True)
                        
                        if created:
                            created_count += 1
                            self.stdout.write(self.style.SUCCESS(f'创建头像: {category}'))
                        else:
                            updated_count += 1
                            self.stdout.write(self.style.SUCCESS(f'更新头像: {category}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'下载失败，状态码: {response.status_code}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'处理头像 {category} 时出错: {str(e)}'))
                    
        else:
            # 遍历并导入本地头像
            for category, filename in avatar_categories.items():
                # 从默认头像目录读取文件
                file_path = Path(settings.BASE_DIR) / directory / filename
                
                self.stdout.write(f'正在处理头像文件: {file_path}')
                
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    self.stdout.write(self.style.WARNING(f'未找到头像文件: {file_path}'))
                    continue
                    
                # 处理图片，去除水印
                try:
                    img = Image.open(file_path)
                    # 裁剪底部水印部分 (假设水印在底部5%区域)
                    width, height = img.size
                    crop_height = int(height * 0.95)  # 裁剪底部5%
                    img = img.crop((0, 0, width, crop_height))
                    
                    # 转换为字节流
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    image_data = buffer.getvalue()
                    
                    # 保存到模型
                    avatar, created = DefaultAvatar.objects.update_or_create(
                        category=category,
                        defaults={
                            'description': f"默认{dict(DefaultAvatar.AVATAR_CATEGORIES).get(category)}头像"
                        }
                    )
                    
                    # 更新图片文件，使用原始文件名
                    avatar.image.save(filename, ContentFile(image_data), save=True)
                    
                    if created:
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f'创建头像: {category} ({filename})'))
                    else:
                        updated_count += 1
                        self.stdout.write(self.style.SUCCESS(f'更新头像: {category} ({filename})'))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'处理头像 {category} 时出错: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'导入完成: {created_count}个新头像, {updated_count}个更新头像')) 