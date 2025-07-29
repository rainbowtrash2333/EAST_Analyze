import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties, fontManager
import matplotlib.ticker as ticker
import warnings
from datetime import datetime
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.figsize'] = (25, 10)
warnings.filterwarnings('ignore')

def process_transaction_data(file_path, filename):
    """
    处理银行流水数据并生成分析结果
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 检查文件是否为空
        if df.empty:
            raise ValueError("Excel文件为空")
        
        # 检查必要的列是否存在
        required_columns = ['交易借贷标志', '交易金额', '对方户名', '对方账号', '对方行名', 
                          '现转标志', '交易类型', '交易渠道', '核心交易日期', '核心交易时间']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(f"缺少必要的列: {', '.join(missing_columns)}")
        
        # 数据预处理
        df = preprocess_data(df)
        
        # 执行各项分析
        counterparty_stats = analyze_counterparties(df)
        total_stats = calculate_total_stats(df)
        transaction_type_stats = analyze_transaction_types(df)
        channel_stats = analyze_channels(df)
        daily_transactions = analyze_daily_trends(df)
        hourly_stats = analyze_hourly_trends(df)
        
        # 生成可视化图表
        chart_files = generate_charts(df, counterparty_stats, transaction_type_stats, 
                                     channel_stats, daily_transactions, hourly_stats, filename)
        
        # 生成Excel报告
        report_file = generate_excel_report(counterparty_stats, total_stats, 
                                          transaction_type_stats, channel_stats, 
                                          daily_transactions, hourly_stats, filename)
        
        return {
            'counterparty_stats': counterparty_stats,
            'total_stats': total_stats,
            'transaction_type_stats': transaction_type_stats,
            'channel_stats': channel_stats,
            'daily_transactions': daily_transactions,
            'hourly_stats': hourly_stats,
            'chart_files': chart_files,
            'report_file': report_file,
            'filename': filename
        }
    except Exception as e:
        # 重新抛出异常以便上层处理
        print(f'文件处理出现意外错误: {str(e)}')
        raise e

def preprocess_data(df):
    """
    数据预处理
    """
    # 交易金额正负转换（贷为正，借为负）
    df['交易金额_正负'] = np.where(df['交易借贷标志'] == '贷', df['交易金额'], -df['交易金额'])
    
    # 现转标志处理
    df.loc[df['现转标志']=='现','对方行名']='取现'
    
    # 转换对方账号为字符串
    df['对方账号'] = df['对方账号'].astype(str)
    
    # 转换日期时间格式
    df['核心交易日期'] = pd.to_datetime(df['核心交易日期'], format='%Y%m%d')
    df['交易时间'] = pd.to_datetime(df['核心交易日期'].astype(str) + ' ' + 
                                 df['核心交易时间'].astype(str).str.zfill(6), 
                                 format='%Y-%m-%d %H%M%S')
    df['交易小时'] = df['交易时间'].dt.hour
    
    return df

def analyze_counterparties(df):
    """
    分析交易对手
    """
    counterparty_stats = df.groupby('对方户名').agg(
        对方账号 = ('对方账号', lambda x: '-'.join(x.unique().astype(str))),
        对方行名 = ('对方行名', lambda x: '-'.join(x.unique().astype(str))),
        交易次数=('交易金额_正负', 'count'),
        总交易金额=('交易金额_正负', 'sum'),
        总收入=('交易金额', lambda x: x[df['交易借贷标志'] == '贷'].sum()),
        总支出=('交易金额', lambda x: x[df['交易借贷标志'] == '借'].sum()),
        收入次数=('交易借贷标志', lambda x: (x == '贷').sum()),
        支出次数=('交易借贷标志', lambda x: (x == '借').sum()),
        平均收入=('交易金额', lambda x: x[df['交易借贷标志'] == '贷'].mean()),
        平均支出=('交易金额', lambda x: x[df['交易借贷标志'] == '借'].mean()),
        最大交易=('交易金额_正负', 'max'),
        最小交易=('交易金额_正负', 'min')
    ).reset_index().sort_values('交易次数', ascending=False)
    
    # 处理NaN值
    counterparty_stats['平均收入'] = counterparty_stats['平均收入'].fillna(0)
    counterparty_stats['平均支出'] = counterparty_stats['平均支出'].fillna(0)
    
    # 添加净收支方向列
    counterparty_stats['净方向'] = np.where(
        counterparty_stats['总交易金额'] > 0, '净收入', 
        np.where(counterparty_stats['总交易金额'] < 0, '净支出', '平衡')
    )
    
    # 添加收支比例列
    counterparty_stats['收入占比'] = counterparty_stats['收入次数'] / counterparty_stats['交易次数']
    counterparty_stats['支出占比'] = counterparty_stats['支出次数'] / counterparty_stats['交易次数']
    
    return counterparty_stats

def calculate_total_stats(df):
    """
    计算整体统计
    """
    total_stats = pd.DataFrame({
        '统计指标': ['总交易次数', '总收入', '总支出', '净收入', '平均交易额'],
        '数值': [
            len(df),
            df[df['交易借贷标志'] == '贷']['交易金额'].sum(),
            df[df['交易借贷标志'] == '借']['交易金额'].sum(),
            df['交易金额_正负'].sum(),
            df['交易金额'].mean()
        ]
    })
    return total_stats

def analyze_transaction_types(df):
    """
    分析交易类型
    """
    transaction_type_stats = df.groupby('交易类型').agg(
        交易次数=('交易金额', 'count'),
        总金额=('交易金额_正负', 'sum')
    ).reset_index().sort_values('交易次数', ascending=False)
    return transaction_type_stats

def analyze_channels(df):
    """
    分析交易渠道
    """
    channel_stats = df.groupby('交易渠道').agg(
        交易次数=('交易金额', 'count'),
        总金额=('交易金额_正负', 'sum')
    ).reset_index().sort_values('交易次数', ascending=False)
    return channel_stats

def analyze_daily_trends(df):
    """
    分析每日交易趋势
    """
    daily_transactions = df.groupby('核心交易日期').agg(
        交易次数=('交易金额', 'count'),
        净流量=('交易金额_正负', 'sum')
    ).reset_index()
    return daily_transactions

def analyze_hourly_trends(df):
    """
    分析每小时交易趋势
    """
    hourly_stats = df.groupby('交易小时').agg(
        总收入=('交易金额', lambda x: x[df['交易借贷标志'] == '贷'].sum()),
        总支出=('交易金额', lambda x: x[df['交易借贷标志'] == '借'].sum()),
        收入次数=('交易借贷标志', lambda x: (x == '贷').sum()),
        支出次数=('交易借贷标志', lambda x: (x == '借').sum())
    ).reset_index()
    
    # 补全24小时
    all_hours = pd.DataFrame({'交易小时': range(24)})
    hourly_stats = all_hours.merge(hourly_stats, on='交易小时', how='left').fillna(0)
    
    # 计算净流量
    hourly_stats['净流量'] = hourly_stats['总收入'] - hourly_stats['总支出']
    
    return hourly_stats

def generate_charts(df, counterparty_stats, transaction_type_stats, channel_stats, 
                   daily_transactions, hourly_stats, filename):
    """
    生成所有图表
    """
    chart_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 主要分析图表
    fig, axes = plt.subplots(3, 2, figsize=(20, 18))
    
    # 交易对手金额分布（前10）
    top_counterparties = counterparty_stats.head(10)
    colors = ['green' if x > 0 else 'red' for x in top_counterparties['总交易金额']]
    sns.barplot(x='总交易金额', y='对方户名', data=top_counterparties, 
                palette=colors, ax=axes[0, 0])
    axes[0, 0].set_title('TOP10交易对手净交易金额')
    
    # 交易类型分布
    sns.barplot(x='交易次数', y='交易类型', data=transaction_type_stats.head(5), ax=axes[0, 1])
    axes[0, 1].set_title('TOP5交易类型次数')
    
    # 每日交易趋势
    axes[1, 0].plot(daily_transactions['核心交易日期'], daily_transactions['净流量'], 'b-o')
    axes[1, 0].set_title('每日资金净流量趋势')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{x/10000:.1f}万'))
    axes[1, 0].grid(True, linestyle='--', alpha=0.7)
    
    # 交易渠道分布
    sns.barplot(x='交易次数', y='交易渠道', data=channel_stats.head(5), ax=axes[1, 1])
    axes[1, 1].set_title('TOP5交易渠道使用次数')
    
    # 借贷分布
    debit_credit = df['交易借贷标志'].value_counts()
    axes[2, 0].pie(debit_credit, labels=debit_credit.index, autopct='%1.1f%%',
                   colors=['#ff9999','#66b3ff'], startangle=90)
    axes[2, 0].set_title('借贷交易比例')
    
    # 金额分布直方图
    sns.histplot(df['交易金额_正负'], bins=30, kde=True, ax=axes[2, 1])
    axes[2, 1].set_title('交易金额分布')
    axes[2, 1].axvline(0, color='r', linestyle='--')
    
    plt.tight_layout()
    chart1_file = f'{timestamp}_{filename}_main_analysis.png'
    chart1_path = os.path.join('static/charts', chart1_file)
    plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
    plt.close()
    chart_files.append(chart1_file)
    
    # 2. 每小时分析图表
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 金额堆叠柱状图
    axes[0, 0].bar(hourly_stats['交易小时'], hourly_stats['总收入'], 
                   color='#66c2a5', label='收入')
    axes[0, 0].bar(hourly_stats['交易小时'], -hourly_stats['总支出'], 
                   color='#fc8d62', label='支出')
    axes[0, 0].axhline(0, color='black', linewidth=0.5)
    axes[0, 0].set_title('各小时收入支出金额对比')
    axes[0, 0].legend()
    axes[0, 0].grid(axis='y', linestyle='--', alpha=0.7)
    
    # 净流量趋势线
    axes[0, 1].plot(hourly_stats['交易小时'], hourly_stats['净流量'], 
                    'b-o', linewidth=2, markersize=6)
    axes[0, 1].axhline(0, color='red', linestyle='--')
    axes[0, 1].set_title('各小时资金净流量')
    axes[0, 1].grid(True, linestyle='--', alpha=0.5)
    
    # 交易次数柱状图
    axes[1, 0].bar(hourly_stats['交易小时'], hourly_stats['收入次数'], 
                   color='#8da0cb', alpha=0.7, label='收入次数')
    axes[1, 0].bar(hourly_stats['交易小时'], hourly_stats['支出次数'], 
                   color='#e78ac3', alpha=0.7, label='支出次数', 
                   bottom=hourly_stats['收入次数'])
    axes[1, 0].set_title('各小时交易次数分布')
    axes[1, 0].legend()
    axes[1, 0].grid(axis='y', linestyle='--', alpha=0.5)
    
    # 全天收入支出对比
    total_income = hourly_stats['总收入'].sum()
    total_expense = hourly_stats['总支出'].sum()
    axes[1, 1].pie([total_income, total_expense], 
                   labels=[f'总收入\n{total_income:,.2f}', f'总支出\n{total_expense:,.2f}'],
                   colors=['#66c2a5', '#fc8d62'], autopct='%1.1f%%')
    axes[1, 1].set_title('全天收入支出总额对比')
    
    plt.tight_layout()
    chart2_file = f'{timestamp}_{filename}_hourly_analysis.png'
    chart2_path = os.path.join('static/charts', chart2_file)
    plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
    plt.close()
    chart_files.append(chart2_file)
    
    return chart_files

def generate_excel_report(counterparty_stats, total_stats, transaction_type_stats, 
                         channel_stats, daily_transactions, hourly_stats, filename):
    """
    生成Excel报告
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f'{timestamp}_{filename}_report.xlsx'
    report_path = os.path.join('outputs', report_file)
    
    with pd.ExcelWriter(report_path) as writer:
        counterparty_stats.to_excel(writer, sheet_name='交易对手统计', index=False)
        total_stats.to_excel(writer, sheet_name='整体统计', index=False)
        transaction_type_stats.to_excel(writer, sheet_name='交易类型分析', index=False)
        channel_stats.to_excel(writer, sheet_name='交易渠道分析', index=False)
        daily_transactions.to_excel(writer, sheet_name='每日交易趋势', index=False)
        hourly_stats.to_excel(writer, sheet_name='每小时分析', index=False)
    
    return report_file
    
if __name__ == '__main__':
    file_path = r'uploads\20250729_113709_-.xlsx'
    filename = '-.xlsx'
    result = process_transaction_data(file_path, filename)
    print(result)