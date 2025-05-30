from flask import Flask, render_template, request, jsonify
import os
import logging
from datetime import datetime

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

// ... existing code ...

@app.route('/', methods=['GET', 'POST'])
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
    
    return render_template('index.html', result=result, error=error)

@app.route('/health')
def health():
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat(),
        'user_agent': request.headers.get('User-Agent', '')
    })

// ... existing code ...
