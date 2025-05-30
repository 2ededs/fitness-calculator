from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, NumberRange
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # 使用随机密钥
app.config['WTF_CSRF_ENABLED'] = False  # 禁用CSRF以简化微信访问

class CalculatorForm(FlaskForm):
    gender = SelectField('性别', 
                        choices=[('male', '男'), ('female', '女')],
                        validators=[DataRequired()])
    
    age = IntegerField('年龄',
                      validators=[DataRequired(), 
                                NumberRange(min=10, max=100)])
    
    weight = FloatField('负重重量(kg)',
                       validators=[DataRequired(),
                                 NumberRange(min=0, max=100)])
    
    reps = IntegerField('重复次数',
                       validators=[DataRequired(),
                                 NumberRange(min=1, max=20)])

def calculate_1rm(weight, reps):
    """
    使用Brzycki公式计算1RM
    1RM = 体重 × (36 / (37 - 重复次数))
    """
    if reps == 1:
        return weight
    return weight * (36 / (37 - reps))

def calculate_percentages(one_rm):
    """计算不同百分比的重量"""
    percentages = [100, 95, 90, 85, 80, 75, 70, 65, 60]
    return {f"{p}%": round(one_rm * p / 100, 1) for p in percentages}

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CalculatorForm()
    result = None
    
    if request.method == 'POST':  # 修改验证逻辑以适应微信环境
        weight = float(request.form.get('weight', 0))
        reps = int(request.form.get('reps', 1))
        gender = request.form.get('gender', 'male')
        age = int(request.form.get('age', 25))
        
        # 验证输入
        if not (0 <= weight <= 100 and 1 <= reps <= 20 and 10 <= age <= 100):
            return render_template('index.html', form=form, error="请输入有效的数值范围")
        
        # 计算1RM
        one_rm = calculate_1rm(weight, reps)
        
        # 计算不同百分比的重量
        percentages = calculate_percentages(one_rm)
        
        # 根据性别和年龄给出评估
        assessment = ""
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
    
    return render_template('index.html', form=form, result=result)

# 添加健康检查端点
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # 使用环境变量或默认值
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 