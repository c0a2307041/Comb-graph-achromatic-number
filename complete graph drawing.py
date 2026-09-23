import numpy as np
import networkx as nx

import matplotlib.pyplot as plt

def draw_complete_graph(n):
    # 完全グラフを作成
    G = nx.complete_graph(n)
    
    # 頂点を円形に配置
    # nが大きいほど円の半径を大きくして頂点同士の距離を増やす
    radius = max(1, n / 3)
    pos = {}
    for i in range(n):
        angle = 2 * np.pi * i / n
        pos[i] = (radius * np.cos(angle), radius * np.sin(angle))
    
    # グラフを描画
    plt.figure(figsize=(10, 10))
    
    # エッジを描画
    nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.5)
    
    # ノードを描画
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                          node_size=500, edgecolors='black')
    
    # ノードのラベル（1からnまで）を描画
    labels = {i: str(i + 1) for i in range(n)}
    nx.draw_networkx_labels(G, pos, labels, font_size=10)
    
    plt.title(f"Complete Graph K_{n}")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# 使用例
n = int(input("頂点の数nを入力してください: "))
draw_complete_graph(n)