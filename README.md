# HomeHealth
家庭健康档案系统

# 小树家庭健康档案系统

小树家庭健康档案系统是一个全面的健康记录管理平台，帮助家庭成员记录和管理各种健康信息。

## 主要功能

- 用户管理与认证
- 家庭成员关系管理
- 健康记录管理（就医记录、药物记录、疫苗接种记录、体检记录）
- 健康数据统计与分析
- 文件加密存储
- 提醒与通知

## 技术栈

### 后端
- Django
- Django REST Framework
- PostgreSQL
- JWT认证
- Cryptography (文件加密)

### 前端
- Vue 3
- TypeScript
- Element Plus
- Pinia
- Axios
- Echarts

## 设置与启动

### 后端设置

1. 创建虚拟环境并安装依赖:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

2. 设置数据库:
```bash
python manage.py migrate
```

3. 创建超级用户:
```bash
python manage.py createsuperuser
```

4. 初始化默认头像:
```bash
python manage.py initialize_default_avatars
```

5. 启动开发服务器:
```bash
python manage.py runserver
```

### 前端设置

1. 安装依赖:
```bash
cd frontend/health-frontend
npm install
```

2. 启动开发服务器:
```bash
npm run dev
```

## 默认头像功能

系统提供根据用户性别和年龄自动分配默认头像的功能:

### 默认头像类别

系统根据不同的用户特征提供不同的默认头像：

1. 性别分组: 男性、女性、未知
2. 年龄分组: 儿童（12岁以下）、成人（12-49岁）、长者（50岁及以上）

### 管理默认头像

管理员可以通过以下方式管理默认头像:

1. 使用Django管理界面: `/admin/users/defaultavatar/`
2. 使用命令行初始化/更新默认头像:
   ```bash
   python manage.py initialize_default_avatars  # 初始化
   python manage.py initialize_default_avatars --force  # 强制更新所有
   ```

3. 通过API:
   - 获取所有默认头像: `GET /api/users/default-avatars/`
   - 获取特定类别头像: `GET /api/users/default-avatars/by_category/?category=male_adult`
   - 根据年龄和性别获取头像: `GET /api/users/default-avatars/get_by_age_gender/?age=25&gender=male`

默认头像文件应存放在 `backend/static/default_avatars/` 目录，命名格式遵循 `{gender}_{age_group}.png` 格式，如：
- `male_child.png`
- `female_adult.png`
- `unknown_elder.png`
