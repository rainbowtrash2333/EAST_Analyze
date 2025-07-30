from flask import Flask, request, jsonify, send_file
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
from typing import Dict, Any, List, Tuple, Optional

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

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check() -> Dict[str, str]:
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': '后端API服务正常运行'})

@app.route('/api/upload', methods=['POST'])
def upload_file() -> Tuple[Dict[str, Any], int]:
    """流水分析文件上传接口"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'error': '请选择要上传的文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '请选择要上传的文件'}), 400
        
        # 检查文件格式
        if not file or not allowed_file(file.filename):
            return jsonify({'error': '只支持Excel文件格式(.xlsx, .xls)'}), 400
        
        # 检查文件大小
        if len(file.read()) > app.config['MAX_CONTENT_LENGTH']:
            return jsonify({'error': '文件过大，请上传小于16MB的文件'}), 400
        
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
            return jsonify({'error': '文件保存失败，请重试'}), 500
        
        # 处理文件并生成分析结果
        try:
            result = process_transaction_data(file_path, filename)
            
            # 转换结果为JSON可序列化格式
            response_data = {
                'message': '文件分析完成！',
                'filename': filename,
                'report_file': result['report_file'],
                'chart_files': result['chart_files'],
                'total_stats': result['total_stats'].to_dict('records'),
                'counterparty_stats': result['counterparty_stats'].head(10).to_dict('records'),
                'transaction_type_stats': result['transaction_type_stats'].to_dict('records'),
                'channel_stats': result['channel_stats'].to_dict('records'),
                'daily_transactions': result['daily_transactions'].to_dict('records'),
                'hourly_stats': result['hourly_stats'].to_dict('records')
            }
            
            return jsonify(response_data)
            
        except FileNotFoundError:
            return jsonify({'error': '找不到上传的文件，请重新上传'}), 404
        except pd.errors.EmptyDataError:
            return jsonify({'error': 'Excel文件为空或格式不正确'}), 400
        except (pd.errors.ParserError, ValueError) as e:
            if 'Excel' in str(e) or 'workbook' in str(e).lower():
                return jsonify({'error': 'Excel文件损坏或格式不正确'}), 400
            else:
                return jsonify({'error': f'数据格式错误: {str(e)}，请检查文件内容'}), 400
        except KeyError as e:
            return jsonify({'error': f'Excel文件缺少必要的列: {str(e)}，请检查文件格式'}), 400
        except Exception as e:
            return jsonify({'error': f'文件处理出现意外错误: {str(e)}'}), 500
        finally:
            # 清理临时文件
            try:
                if os.path.exists(file_path):   
                    os.remove(file_path)
            except:
                pass
                
    except Exception as e:
        return jsonify({'error': f'系统错误: {str(e)}'}), 500

@app.route('/api/upload_network', methods=['POST'])
def upload_network_files() -> Tuple[Dict[str, Any], int]:
    """网络分析文件上传接口"""
    try:
        # 检查是否有文件上传
        if 'files' not in request.files:
            return jsonify({'error': '请选择要上传的文件'}), 400
        
        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            return jsonify({'error': '请选择要上传的文件'}), 400
        
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
                return jsonify({'error': f'文件 {file.filename} 格式不支持，只支持Excel文件'}), 400
        
        if not saved_files:
            return jsonify({'error': '没有有效的Excel文件'}), 400
        
        # 处理网络数据
        try:
            result = process_network_data(temp_folder, f"network_{timestamp}")
            print(result)
            # 转换结果为JSON可序列化格式
            response_data = {
                'message': '网络图分析完成！',
                'html_file': result['html_file'],
                'node_count': result['node_count'],
                'edge_count': result['edge_count'],
                'filename': result['filename'],
                'stats': result['stats'],
                'network_analysis': result['network_analysis'],
                'uploaded_files': saved_files
            }
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({'error': f'网络图处理出现错误: {str(e)}'}), 500
        finally:
            # 清理临时文件夹
            try:
                import shutil
                if os.path.exists(temp_folder):
                    shutil.rmtree(temp_folder)
            except:
                pass
                
    except Exception as e:
        return jsonify({'error': f'系统错误: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def download_file(filename: str):
    """文件下载接口"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '请求的文件不存在'}), 404
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'文件下载失败: {str(e)}'}), 500

@app.route('/api/charts/<filename>')
def get_chart(filename: str):
    """获取图表文件"""
    try:
        file_path = os.path.join('static/charts', filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '请求的图表不存在'}), 404
        
        return send_file(file_path)
    except Exception as e:
        return jsonify({'error': f'图表获取失败: {str(e)}'}), 500

@app.route('/api/networks/<filename>')
def get_network(filename: str):
    """获取网络图文件"""
    try:
        file_path = os.path.join('static/networks', filename)
        if not os.path.exists(file_path):
            return jsonify({'error': '请求的网络图不存在'}), 404
        
        return send_file(file_path)
    except Exception as e:
        return jsonify({'error': f'网络图获取失败: {str(e)}'}), 500

@app.errorhandler(404)
def api_not_found(e) -> Tuple[Dict[str, str], int]:
    return jsonify({'error': 'API接口不存在'}), 404

@app.errorhandler(500)
def api_internal_error(e) -> Tuple[Dict[str, str], int]:
    return jsonify({'error': '服务器内部错误，请重试'}), 500

@app.errorhandler(413)
def api_file_too_large(e) -> Tuple[Dict[str, str], int]:
    return jsonify({'error': '文件过大，请上传小于16MB的文件'}), 413

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')