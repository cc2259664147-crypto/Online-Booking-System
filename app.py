from flask import Flask
from models import db
from appointment_routes import appointment_bp

app = Flask(__name__)

# 配置数据库（使用SQLite，文件在本地）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appointments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 注册路由（你的5个接口）
app.register_blueprint(appointment_bp)

# 创建所有表（首次运行自动生成）
with app.app_context():
    db.create_all()
    print("✅ 数据库创建成功！")

# 根路径测试
@app.route('/')
def hello():
    return '预约系统API运行中！访问 /api/appointments 测试'

# 启动服务
if __name__ == '__main__':
    app.run(debug=True, port=5000)