from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
import os
import warnings
import pandas as pd
import zipfile
from datetime import datetime
from werkzeug.utils import secure_filename
from analysis import process_transaction_data
from network_analysis import process_network_data
import secrets

app = Flask(__name__)
CORS(app)  # 允许跨域请求
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传和输出目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('static/charts', exist_ok=True)
os.makedirs('static/networks', exist_ok=True)

warnings.filterwarnings('ignore')

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            flash('请选择要上传的文件', 'error')
            return redirect(url_for('index'))
        
        file = request.files['file']
        if file.filename == '':
            flash('请选择要上传的文件', 'error')
            return redirect(url_for('index'))
        
        # 检查文件格式
        if not file or not allowed_file(file.filename):
            flash('只支持Excel文件格式(.xlsx, .xls)', 'error')
            return redirect(url_for('index'))
        
        # 检查文件大小
        if len(file.read()) > app.config['MAX_CONTENT_LENGTH']:
            flash('文件过大，请上传小于16MB的文件', 'error')
            return redirect(url_for('index'))
        
        # 重置文件指针
        file.seek(0)
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            file.save(file_path)
        except Exception as e:
            flash('文件保存失败，请重试', 'error')
            return redirect(url_for('index'))
        
        # 处理文件并生成分析结果
        try:
            result = process_transaction_data(file_path, filename)
            flash('文件分析完成！', 'success')
            return render_template('results.html', result=result)
        except FileNotFoundError:
            flash('找不到上传的文件，请重新上传', 'error')
            return redirect(url_for('index'))
        except pd.errors.EmptyDataError:
            flash('Excel文件为空或格式不正确', 'error')
            return redirect(url_for('index'))
        except (pd.errors.ParserError, ValueError) as e:
            if 'Excel' in str(e) or 'workbook' in str(e).lower():
                flash('Excel文件损坏或格式不正确', 'error')
            else:
                flash(f'数据格式错误: {str(e)}，请检查文件内容', 'error')
            return redirect(url_for('index'))
        except KeyError as e:
            flash(f'Excel文件缺少必要的列: {str(e)}，请检查文件格式', 'error')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'文件处理出现意外错误: {str(e)}', 'error')
            return redirect(url_for('index'))
        finally:
            # 清理临时文件
            try:
                if os.path.exists(file_path):   
                    os.remove(file_path)
            except:
                pass
                
    except Exception as e:
        flash(f'系统错误: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/upload_network', methods=['POST'])
def upload_network_files():
    try:
        # 检查是否有文件上传
        if 'files' not in request.files:
            flash('请选择要上传的文件', 'error')
            return redirect(url_for('index'))
        
        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            flash('请选择要上传的文件', 'error')
            return redirect(url_for('index'))
        
        # 创建临时文件夹
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"network_{timestamp}")
        os.makedirs(temp_folder, exist_ok=True)
        
        # 保存所有文件
        saved_files = []
        for file in files:
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(temp_folder, filename)
                file.save(file_path)
                saved_files.append(filename)
            elif file.filename != '':
                flash(f'文件 {file.filename} 格式不支持，只支持Excel文件', 'error')
                return redirect(url_for('index'))
        
        if not saved_files:
            flash('没有有效的Excel文件', 'error')
            return redirect(url_for('index'))
        
        # 处理网络数据
        try:
            result = process_network_data(temp_folder, f"network_{timestamp}")
            flash('网络图分析完成！', 'success')
            return render_template('network_results.html', result=result)
        except Exception as e:
            flash(f'网络图处理出现错误: {str(e)}', 'error')
            return redirect(url_for('index'))
        finally:
            # 清理临时文件夹
            try:
                import shutil
                if os.path.exists(temp_folder):
                    shutil.rmtree(temp_folder)
            except:
                pass
                
    except Exception as e:
        flash(f'系统错误: {str(e)}', 'error')
        return redirect(url_for('index'))
@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(file_path):
            flash('请求的文件不存在', 'error')
            return redirect(url_for('index'))
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f'文件下载失败: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    flash('服务器内部错误，请重试', 'error')
    return render_template('index.html'), 500

@app.errorhandler(413)
def file_too_large(e):
    flash('文件过大，请上传小于16MB的文件', 'error')
    return render_template('index.html'), 413

if __name__ == '__main__':
    app.run(debug=True)