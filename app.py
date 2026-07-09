from flask import Flask
from models import db
from appointment_routes import appointment_bp
from service import service_bp  # 新增：导入同学写的 service 蓝图

app = Flask(__name__)

# 配置数据库（建议与同学使用同一个数据库）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booking.db'  # 改为 booking.db，与同学保持一致
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 注册路由（你的预约接口 + 同学的服务接口）
app.register_blueprint(appointment_bp)
app.register_blueprint(service_bp)  # 新增：注册同学的服务蓝图

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
