import os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from users.models import DefaultAvatar
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '初始化系统默认头像'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', 
            action='store_true', 
            help='强制重新初始化所有默认头像'
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        # 默认头像目录
        default_avatar_dir = os.path.join(settings.STATIC_ROOT, 'default_avatars')
        
        # 检查目录是否存在
        if not os.path.exists(default_avatar_dir):
            os.makedirs(default_avatar_dir, exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f'创建默认头像目录: {default_avatar_dir}'))
        
        # 默认头像配置 
        avatars = [
            {
                'category': 'male_child',
                'description': '男孩默认头像',
                'file_path': os.path.join(settings.BASE_DIR, 'static', 'default_avatars', 'male_child.png')
            },
            {
                'category': 'female_child',
                'description': '女孩默认头像',
                'file_path': os.path.join(settings.BASE_DIR, 'static', 'default_avatars', 'female_child.png')
            },
            {
                'category': 'male_adult',
                'description': '成年男性默认头像',
                'file_path': os.path.join(settings.BASE_DIR, 'static', 'default_avatars', 'male_adult.png')
            },
            {
                'category': 'female_adult',
                'description': '成年女性默认头像',
                'file_path': os.path.join(settings.BASE_DIR, 'static', 'default_avatars', 'female_adult.png')
            },
            {
                'category': 'male_elder',
                'description': '老年男性默认头像',
                'file_path': os.path.join(settings.BASE_DIR, 'static', 'default_avatars', 'male_elder.png')
            },
            {
                'category': 'female_elder',
                'description': '老年女性默认头像',
                'file_path': os.path.join(settings.BASE_DIR, 'static', 'default_avatars', 'female_elder.png')
            },
            {
                'category': 'unknown_child',
                'description': '儿童通用默认头像',
                'file_path': os.path.join(settings.BASE_DIR, 'static', 'default_avatars', 'unknown_child.png')
            },
            {
                'category': 'unknown_adult',
                'description': '成人通用默认头像',
                'file_path': os.path.join(settings.BASE_DIR, 'static', 'default_avatars', 'unknown_adult.png')
            },
            {
                'category': 'unknown_elder',
                'description': '老年通用默认头像',
                'file_path': os.path.join(settings.BASE_DIR, 'static', 'default_avatars', 'unknown_elder.png')
            },
        ]
        
        avatars_created = 0
        avatars_updated = 0
        avatars_skipped = 0
        errors = 0
        
        for avatar_config in avatars:
            category = avatar_config['category']
            description = avatar_config['description']
            file_path = avatar_config['file_path']
            
            # 检查头像文件是否存在
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f'头像文件不存在: {file_path}'))
                errors += 1
                continue
                
            # 检查数据库中是否已有此类别的头像
            try:
                avatar, created = DefaultAvatar.objects.get_or_create(
                    category=category,
                    defaults={'description': description}
                )
                
                # 如果头像已存在且不强制更新，则跳过
                if not created and not force and avatar.image:
                    self.stdout.write(f'已跳过现有头像: {category}')
                    avatars_skipped += 1
                    continue
                
                # 读取头像文件
                with open(file_path, 'rb') as f:
                    image_content = f.read()
                
                # 保存头像
                filename = os.path.basename(file_path)
                avatar.image.save(filename, ContentFile(image_content), save=True)
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'已创建默认头像: {category}'))
                    avatars_created += 1
                else:
                    self.stdout.write(self.style.SUCCESS(f'已更新默认头像: {category}'))
                    avatars_updated += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'处理头像 {category} 时出错: {str(e)}'))
                logger.error(f'处理头像 {category} 时出错: {str(e)}')
                errors += 1
        
        # 输出总结
        self.stdout.write(self.style.SUCCESS(
            f'默认头像初始化完成: '
            f'创建 {avatars_created}, '
            f'更新 {avatars_updated}, '
            f'跳过 {avatars_skipped}, '
            f'错误 {errors}'
        )) 