import networkx as nx
import matplotlib.pyplot as plt

# --- パラメータ計算（前回と同じ） ---
#　ここにやりたい色数を指定します
cloer = 6   
cloer_nuber = (cloer * (cloer - 1)) / 2
p = cloer_nuber + 1
if p % 2 == 1:
    p += 1
p /= 2
p = int(p)
# ------------------------------------

# 1. 元のグラフ（直線部分）の作成
G = nx.path_graph(p)
# 元のノードリストを取得しておきます（0 から p-1 まで）
original_nodes = list(G.nodes())

# 2. 各頂点に対して新しい頂点と辺を追加
# 元の各ノード i に対して、新しいノード (i + p) を追加し、辺を結びます
for i in original_nodes:
    new_node_id = i + p  # 既存のIDと被らないように p を足す
    G.add_node(new_node_id)
    G.add_edge(i, new_node_id)

# 3. 配置（レイアウト）の計算
spering = 2
pos = {}
node_colors = [] # ノードの色を区別するためのリスト

for node in G.nodes():
    if node < p:
        # 元のノードは横一列 (y=0) に配置
        pos[node] = (node * spering, 0)
        node_colors.append('lightblue') # 元のノードは水色
    else:
        # 新しく追加したノードは、対応する元のノードの真上 (y=1) に配置
        # node - p が元のノードのIDに対応します
        pos[node] = ((node - p) * spering, 0.25)
        node_colors.append('lightblue') # 新しいノードは薄緑色

# 4. 描画
# 縦方向の情報が増えるので、少し縦幅を広げます
plt.figure(figsize=(50, 20))
ax = plt.gca()

nx.draw(G, pos, with_labels=False, node_color=node_colors,
        node_size=500,  ax=ax)

# 見た目の調整
plt.axis('off')
# 上下のノードが切れないように表示範囲を少し広めに設定
plt.ylim(-0.5, 1.5)

# 画像として保存
plt.savefig('comb_graph_output.png', dpi=150, bbox_inches='tight')
plt.show()