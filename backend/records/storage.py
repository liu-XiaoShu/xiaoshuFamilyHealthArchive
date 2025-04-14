"""
加密文件存储模块
用于安全存储敏感文件
"""

from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from cryptography.fernet import Fernet
import os
from django.conf import settings
from django.utils.deconstruct import deconstructible

@deconstructible
class EncryptedFileStorage(FileSystemStorage):
    """
    加密文件存储类
    使用Fernet对称加密算法对敏感文件进行加密存储
    """
    def __init__(self, location=None, base_url=None):
        super().__init__(location, base_url)
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)

    def _validate_file_type(self, file):
        """验证文件类型"""
        allowed_types = [
            'application/pdf',
            'image/jpeg',
            'image/png',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        if file.content_type not in allowed_types:
            raise ValidationError('不支持的文件类型')

    def _get_encrypted_name(self, name):
        """生成加密文件名"""
        return f"{name}.enc"

    def _save(self, name, content):
        """保存加密文件"""
        self._validate_file_type(content)
        
        # 获取原始文件扩展名
        ext = os.path.splitext(name)[1]
        
        # 加密文件内容
        encrypted_content = self.cipher_suite.encrypt(content.read())
        
        # 创建加密文件
        encrypted_name = self._get_encrypted_name(name)
        encrypted_path = self.path(encrypted_name)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(encrypted_path), exist_ok=True)
        
        # 写入加密文件
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_content)
            
        return encrypted_name

    def _open(self, name, mode='rb'):
        """打开加密文件"""
        encrypted_path = self.path(name)
        if not os.path.exists(encrypted_path):
            raise FileNotFoundError(f"文件不存在: {name}")
            
        with open(encrypted_path, 'rb') as f:
            encrypted_content = f.read()
            
        # 解密文件内容
        decrypted_content = self.cipher_suite.decrypt(encrypted_content)
        return decrypted_content

    def exists(self, name):
        """检查文件是否存在"""
        encrypted_name = self._get_encrypted_name(name)
        return super().exists(encrypted_name)

    def url(self, name):
        """生成文件URL"""
        encrypted_name = self._get_encrypted_name(name)
        return super().url(encrypted_name)

    def size(self, name):
        """获取文件大小"""
        encrypted_name = self._get_encrypted_name(name)
        return super().size(encrypted_name)

    def delete(self, name):
        """删除文件"""
        encrypted_name = self._get_encrypted_name(name)
        super().delete(encrypted_name) 