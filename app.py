from flask import Flask, render_template, request
import os

app = Flask(__name__)

def calculate_1rm(weight, reps):
    """计算1RM"""
    if reps == 1:
        return weight
    return weight * (36 / (37 - reps))

def calculate_percentages(one_rm):
    """计算不同百分比的重量"""
    percentages = [100, 95, 90, 85, 80, 75, 70, 65, 60]
    return {f"{p}%": round(one_rm * p / 100, 1) for p in percentages}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            weight = float(request.form.get('weight', 0))
            reps = int(request.form.get('reps', 1))
            gender = request.form.get('gender', 'male')
            age = int(request.form.get('age', 25))
            
            # 验证输入
            if not (0 <= weight <= 100 and 1 <= reps <= 20 and 10 <= age <= 100):
                error = "请输入有效的数值范围"
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
        except (ValueError, TypeError):
            error = "请输入有效的数值"
    
    return render_template('index.html', result=result, error=error)

@app.route('/health')
def health():
    return 'OK'
