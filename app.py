from flask import Flask, render_template, request, jsonify, make_response
import os
import logging
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_cors_headers(response):
    """添加CORS和安全相关的响应头"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, Accept'
    response.headers['X-Frame-Options'] = 'ALLOW-FROM https://mp.weixin.qq.com/'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://mp.weixin.qq.com/"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    return response

@app.after_request
def after_request(response):
    """每个响应后添加必要的头信息"""
    return add_cors_headers(response)

def handle_options_request(f):
    """处理OPTIONS请求的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            response = make_response()
            response = add_cors_headers(response)
            return response
        return f(*args, **kwargs)
    return decorated_function

// ... existing code ...

@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
@handle_options_request
def index():
    result = None
    error = None
    
    # 记录访问信息
    user_agent = request.headers.get('User-Agent', '')
    logger.info(f"Access from User-Agent: {user_agent}")
    logger.info(f"Request headers: {dict(request.headers)}")
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            weight = float(request.form.get('weight', 0))
            reps = int(request.form.get('reps', 1))
            gender = request.form.get('gender', 'male')
            age = int(request.form.get('age', 25))
            
            # 记录表单提交数据
            logger.info(f"Form data: weight={weight}, reps={reps}, gender={gender}, age={age}")
            
            # 验证输入
            if not (0 <= weight <= 100 and 1 <= reps <= 20 and 10 <= age <= 100):
                error = "请输入有效的数值范围"
                logger.warning(f"Invalid input values: weight={weight}, reps={reps}, age={age}")
            else:
                # 计算1RM
                one_rm = calculate_1rm(weight, reps)
                
                # 计算不同百分比的重量
                percentages = calculate_percentages(one_rm)
                
                # 根据性别和年龄给出评估
                if gender == 'male':
                    if one_rm >= 50:
                        assessment = "优秀"
                    elif one_rm >= 40:
                        assessment = "良好"
                    elif one_rm >= 30:
                        assessment = "一般"
                    else:
                        assessment = "需要提高"
                else:  # female
                    if one_rm >= 35:
                        assessment = "优秀"
                    elif one_rm >= 25:
                        assessment = "良好"
                    elif one_rm >= 15:
                        assessment = "一般"
                    else:
                        assessment = "需要提高"
                        
                result = {
                    'one_rm': round(one_rm, 1),
                    'percentages': percentages,
                    'assessment': assessment
                }
                logger.info(f"Calculation result: {result}")
        except (ValueError, TypeError) as e:
            error = "请输入有效的数值"
            logger.error(f"Error processing form: {str(e)}")

    response = make_response(render_template('index.html', result=result, error=error))
    return response

@app.route('/health')
def health():
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat(),
        'user_agent': request.headers.get('User-Agent', '')
    })

if __name__ == '__main__':
    # 使用环境变量或默认值
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, ssl_context='adhoc')  # 添加SSL支持
