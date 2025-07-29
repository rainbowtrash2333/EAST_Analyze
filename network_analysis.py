import os
import pandas as pd
import networkx as nx
from pyvis.network import Network
import warnings
from datetime import datetime
try:
    from community import community_louvain
except ImportError:
    community_louvain = None

warnings.filterwarnings('ignore')

def process_network_data(folder_path, output_filename):
    """
    处理网络数据文件夹中的所有Excel文件，生成资金流向网络图
    限制节点数不超过150个
    """
    try:
        # 1. 读取所有xlsx文件
        all_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]
        if not all_files:
            raise ValueError("在指定文件夹中未找到Excel文件")
        
        df_list = []
        for file in all_files:
            file_path = os.path.join(folder_path, file)
            df = pd.read_excel(file_path)
            df_list.append(df)
        
        full_df = pd.concat(df_list, ignore_index=True)
        
        # 2. 数据预处理
        # 过滤掉无效的交易对手
        full_df.loc[full_df['对方户名'] == '', '对方户名'] = '取现'
        filtered_df = full_df.dropna(subset=['对方户名'])
        
        # 只保留借贷标志为"借"或"贷"的记录
        filtered_df = filtered_df[filtered_df['借贷标志'].isin(['借', '贷'])]
        
        # 3. 数据分组聚合
        limited = 200000  # 最低交易金额限制
        grouped = filtered_df.groupby(['账户名称', '借贷标志', '对方户名'])['交易金额'].sum().reset_index()
        grouped = grouped[grouped['交易金额'] >= limited]
        
        # 4. 限制节点数量不超过150个
        all_parties = set(grouped['账户名称'].unique()).union(set(grouped['对方户名'].unique()))
        
        # 如果节点数超过150，按交易金额排序，只保留前150个最重要的节点
        if len(all_parties) > 150:
            # 计算每个节点的总交易金额
            party_amounts = {}
            for party in all_parties:
                amount = grouped[
                    (grouped['账户名称'] == party) | (grouped['对方户名'] == party)
                ]['交易金额'].sum()
                party_amounts[party] = amount
            
            # 按金额排序，保留前150个
            top_parties = sorted(party_amounts.items(), key=lambda x: x[1], reverse=True)[:150]
            top_party_names = set([party[0] for party in top_parties])
            
            # 过滤数据，只保留前150个节点相关的交易
            grouped = grouped[
                (grouped['账户名称'].isin(top_party_names)) & 
                (grouped['对方户名'].isin(top_party_names))
            ]
            
            all_parties = top_party_names
        
        # 5. 创建网络图
        network_html = create_network_graph(grouped, all_parties)
        
        # 6. 保存HTML文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_filename = f"{timestamp}_{output_filename}_network.html"
        html_path = os.path.join('static/networks', html_filename)
        
        # 确保目录存在
        os.makedirs('static/networks', exist_ok=True)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(network_html)
        
        # 7. 生成统计数据
        stats = generate_network_stats(grouped, all_parties)
        
        # 8. 进行网络分析（如果数据格式支持）
        network_analysis_result = None
        try:
            network_analysis_result = perform_network_analysis(full_df)
        except Exception as e:
            print(f"网络分析出现错误: {e}")
            # 如果网络分析失败，继续执行其他功能
        
        return {
            'html_file': html_filename,
            'stats': stats,
            'network_analysis': network_analysis_result,
            'node_count': len(all_parties),
            'edge_count': len(grouped),
            'filename': output_filename
        }
        
    except Exception as e:
        raise e

def create_network_graph(grouped, all_parties):
    """
    创建网络图并返回HTML内容
    """
    # 创建网络图
    net = Network(
        directed=True, 
        height="800px",
        width="100%", 
        bgcolor="#222222", 
        font_color="white"
    )
    
    # 定义颜色方案
    COLOR_SCHEME = {
        '借': {'edge': '#FF6B6B', 'node': '#FFA8A8'},  # 红色系表示资金流出
        '贷': {'edge': '#51CF66', 'node': '#D8F5A2'}   # 绿色系表示资金流入
    }
    
    # 添加节点
    node_ids = {}
    node_counter = 0
    
    for party in all_parties:
        node_ids[party] = node_counter
        net.add_node(node_counter, label=party, title=party, color='#adb5bd')
        node_counter += 1
    
    # 添加交易边
    for _, row in grouped.iterrows():
        source_name = row['账户名称']
        target_name = row['对方户名']
        direction = row['借贷标志']
        
        # 确定方向
        if direction == '借':
            from_node = node_ids[source_name]
            to_node = node_ids[target_name]
            # 标记资金来源节点
            net.nodes[from_node]['color'] = COLOR_SCHEME['借']['node']
        else:  # 贷
            from_node = node_ids[target_name]
            to_node = node_ids[source_name]
            # 标记资金去向节点
            net.nodes[to_node]['color'] = COLOR_SCHEME['贷']['node']
        
        # 添加带金额的边
        amount = f"{row['交易金额']:,.0f}"
        net.add_edge(
            from_node, 
            to_node, 
            value=row['交易金额'],
            title=f"{amount}元",
            label=amount,
            color=COLOR_SCHEME[direction]['edge'],
            arrowStrikethrough=False
        )
    
    # 配置图参数
    net.set_options("""
    {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -80000,
          "centralGravity": 0.3,
          "springLength": 95
        },
        "minVelocity": 0.75
      },
      "nodes": {
        "font": {
          "size": 16,
          "face": "Microsoft YaHei"
        },
        "shape": "dot",
        "size": 20
      },
      "edges": {
        "smooth": {
          "type": "continuous"
        },
        "font": {
          "size": 12,
          "strokeWidth": 0
        },
        "color": {
          "inherit": true
        },
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 1.2
          }
        }
      }
    }
    """)
    
    # 生成HTML内容（不启动服务器）
    html_content = net.generate_html()
    
    # 修改HTML内容，使用本地资源或CDN
    html_content = html_content.replace(
        'https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/dist/',
        'https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/'
    )
    
    return html_content

def generate_network_stats(grouped, all_parties):
    """
    生成网络统计数据
    """
    # 计算各种统计指标
    total_amount = grouped['交易金额'].sum()
    avg_amount = grouped['交易金额'].mean()
    
    # 按借贷标志统计
    borrow_stats = grouped[grouped['借贷标志'] == '借'].agg({
        '交易金额': ['sum', 'count', 'mean']
    }).round(2)
    
    lend_stats = grouped[grouped['借贷标志'] == '贷'].agg({
        '交易金额': ['sum', 'count', 'mean']
    }).round(2)
    
    # TOP账户统计
    account_stats = grouped.groupby('账户名称').agg({
        '交易金额': 'sum',
        '对方户名': 'count'
    }).rename(columns={'对方户名': '交易次数'}).sort_values('交易金额', ascending=False).head(10)
    
    # TOP交易对手统计
    counterparty_stats = grouped.groupby('对方户名').agg({
        '交易金额': 'sum',
        '账户名称': 'count'
    }).rename(columns={'账户名称': '交易次数'}).sort_values('交易金额', ascending=False).head(10)
    
    return {
        'total_amount': total_amount,
        'avg_amount': avg_amount,
        'node_count': len(all_parties),
        'edge_count': len(grouped),
        'borrow_stats': {
            'total': float(borrow_stats[('交易金额', 'sum')]) if not borrow_stats.empty else 0,
            'count': int(borrow_stats[('交易金额', 'count')]) if not borrow_stats.empty else 0,
            'avg': float(borrow_stats[('交易金额', 'mean')]) if not borrow_stats.empty else 0
        },
        'lend_stats': {
            'total': float(lend_stats[('交易金额', 'sum')]) if not lend_stats.empty else 0,
            'count': int(lend_stats[('交易金额', 'count')]) if not lend_stats.empty else 0,
            'avg': float(lend_stats[('交易金额', 'mean')]) if not lend_stats.empty else 0
        },
        'top_accounts': account_stats.to_dict('index'),
        'top_counterparties': counterparty_stats.to_dict('index')
    }

def perform_network_analysis(df):
    """
    使用NetworkX进行深度网络分析
    """
    try:
        # 检查是否有证件号码列，如果没有则跳过此分析
        if '证件号码' not in df.columns:
            return None
            
        # 创建有向图
        G = nx.DiGraph()
        
        # 添加节点：所有唯一的"证件号码"和"对方户名"
        all_nodes = set(df['证件号码'].dropna()).union(set(df['对方户名'].dropna()))
        G.add_nodes_from(all_nodes)
        
        # 添加边：根据"交易借贷标志"确定方向
        for index, row in df.iterrows():
            if pd.isna(row['证件号码']) or pd.isna(row['对方户名']):
                continue
                
            if row['借贷标志'] == '借':  # 借：资金流入，边从"对方户名"到"证件号码"
                G.add_edge(row['对方户名'], row['证件号码'], weight=row['交易金额'])
            elif row['借贷标志'] == '贷':  # 贷：资金流出，边从"证件号码"到"对方户名"
                G.add_edge(row['证件号码'], row['对方户名'], weight=row['交易金额'])
        
        # 如果图为空，返回None
        if G.number_of_nodes() == 0:
            return None
        
        # 分析1：连通分量
        connected_components = list(nx.weakly_connected_components(G))
        
        # 分析2：度中心性
        degree_centrality = nx.degree_centrality(G)
        sorted_dc = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
        
        # 分析3：介数中心性
        try:
            betweenness_centrality = nx.betweenness_centrality(G)
            sorted_bc = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)
        except:
            # 如果计算失败（可能由于图太大），使用空列表
            sorted_bc = []
        
        # 分析4：社区检测
        communities = {}
        community_info = []
        try:
            if community_louvain is not None:
                G_undirected = G.to_undirected()
                partition = community_louvain.best_partition(G_undirected)
                
                for node, community_id in partition.items():
                    if community_id not in communities:
                        communities[community_id] = []
                    communities[community_id].append(node)
                
                # 转换为列表格式便于显示
                for cid, nodes in communities.items():
                    community_info.append({
                        'id': cid,
                        'size': len(nodes),
                        'nodes': nodes[:10] if len(nodes) > 10 else nodes  # 只显示前10个节点
                    })
        except Exception as e:
            print(f"社区检测失败: {e}")
        
        # 分析5：聚类系数
        clustering_info = {}
        try:
            G_undirected = G.to_undirected()
            clustering_coeff = nx.clustering(G_undirected)
            sorted_clustering = sorted(clustering_coeff.items(), key=lambda x: x[1], reverse=True)
            avg_clustering = nx.average_clustering(G_undirected)
            
            clustering_info = {
                'average': avg_clustering,
                'top_nodes': sorted_clustering[:10]
            }
        except Exception as e:
            print(f"聚类系数计算失败: {e}")
        
        return {
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'connected_components_count': len(connected_components),
            'connected_components_sizes': [len(comp) for comp in connected_components],
            'degree_centrality_top10': sorted_dc[:10],
            'betweenness_centrality_top10': sorted_bc[:10],
            'communities': community_info,
            'clustering': clustering_info,
            'is_directed': G.is_directed(),
            'density': nx.density(G) if G.number_of_nodes() > 0 else 0
        }
        
    except Exception as e:
        print(f"网络分析出现错误: {e}")
        return None