"""
加密文件存储模块
用于安全存储敏感文件
"""

from django.core.files.storage import FileSystemStorage
from django.conf import settings
from cryptography.fernet import Fernet
import os
import base64
from pathlib import Path

class EncryptedFileStorage(FileSystemStorage):
    """
    加密文件存储类
    使用Fernet对称加密算法加密文件内容
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 从环境变量获取或生成加密密钥
        key = os.getenv('FILE_ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            os.environ['FILE_ENCRYPTION_KEY'] = key.decode()
        else:
            key = key.encode()
        self.fernet = Fernet(key)
        
    def _save(self, name, content):
        """
        重写保存方法，在保存前加密文件内容
        """
        # 读取文件内容
        content.seek(0)
        file_content = content.read()
        
        # 加密内容
        encrypted_content = self.fernet.encrypt(file_content)
        
        # 构建加密文件路径
        encrypted_name = name + '.encrypted'
        
        # 创建目标目录（如果不存在）
        path = Path(self.path(encrypted_name)).parent
        path.mkdir(parents=True, exist_ok=True)
        
        # 保存加密文件
        with open(self.path(encrypted_name), 'wb') as f:
            f.write(encrypted_content)
            
        return encrypted_name
        
    def _open(self, name, mode='rb'):
        """
        重写打开方法，在读取时解密文件内容
        """
        # 读取加密文件
        with open(self.path(name), 'rb') as f:
            encrypted_content = f.read()
            
        # 解密内容
        decrypted_content = self.fernet.decrypt(encrypted_content)
        
        # 创建类文件对象
        import io
        return io.BytesIO(decrypted_content)

    def get_available_name(self, name, max_length=None):
        """
        重写文件名生成方法，处理加密文件扩展名
        """
        if name.endswith('.encrypted'):
            name = name[:-10]  # 移除.encrypted后缀
        return super().get_available_name(name, max_length)

    def exists(self, name):
        """
        重写文件存在检查方法，考虑加密文件扩展名
        """
        if not name.endswith('.encrypted'):
            name = name + '.encrypted'
        return super().exists(name)

    def size(self, name):
        """
        重写获取文件大小方法
        """
        if not name.endswith('.encrypted'):
            name = name + '.encrypted'
        return super().size(name)

    def url(self, name):
        """
        重写URL生成方法，移除加密文件扩展名
        """
        if name.endswith('.encrypted'):
            name = name[:-10]
        return super().url(name) 