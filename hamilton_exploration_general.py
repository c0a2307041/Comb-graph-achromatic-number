import itertools

# =====================================================================
# 1. 出次数を満たす「すべてのトーナメント」を生成するロジック
# =====================================================================
def generate_all_tournaments(degrees):
    """ 指定された出次数シーケンスを持つすべてのトーナメント行列を全探索で生成する """
    n = len(degrees)
    all_matrices = []
    
    # 総当たり戦のペアをすべてリストアップ (全15試合)
    edges = list(itertools.combinations(range(n), 2))
    
    # 現在の各ノードの出次数カウント
    current_degrees = [0] * n
    # 初期空行列
    matrix = [[0] * n for _ in range(n)]
    
    def backtrack(edge_idx):
        if edge_idx == len(edges):
            if current_degrees == degrees:
                all_matrices.append([row[:] for row in matrix])
            return
        
        u, v = edges[edge_idx]
        
        # パターン1: u が v に勝つ (u -> v)
        if current_degrees[u] < degrees[u]:
            matrix[u][v] = 1
            matrix[v][u] = 2
            current_degrees[u] += 1
            backtrack(edge_idx + 1)
            current_degrees[u] -= 1
            matrix[u][v] = 0
            matrix[v][u] = 0
            
        # パターン2: v が u に勝つ (v -> u)
        if current_degrees[v] < degrees[v]:
            matrix[u][v] = 2
            matrix[v][u] = 1
            current_degrees[v] += 1
            backtrack(edge_idx + 1)
            current_degrees[v] -= 1
            matrix[u][v] = 0
            matrix[v][u] = 0

    backtrack(0)
    return all_matrices


# =====================================================================
# 2. ハミルトンサイクル探索・上位グループパス探索
# =====================================================================
def find_all_hamiltonian_cycles_1_based(matrix):
    n = len(matrix)
    all_cycles = []
    
    def backtrack(curr, path, visited):
        if len(path) == n:
            if matrix[curr][0] == 1:
                cycle_1_based = [v + 1 for v in path] + [1]
                all_cycles.append(cycle_1_based)
            return
        for nxt in range(n):
            if not visited[nxt] and matrix[curr][nxt] == 1:
                visited[nxt] = True
                path.append(nxt)
                backtrack(nxt, path, visited)
                path.pop()
                visited[nxt] = False

    visited = [False] * n
    visited[0] = True
    backtrack(0, [0], visited)
    return all_cycles

def find_all_paths_in_top_group(matrix, target_degrees, end_degree=3):
    n = len(matrix)
    all_paths = []
    top_group_indices = [i + 1 for i, deg in enumerate(target_degrees) if deg >= end_degree]
    group_size = len(top_group_indices)
    end_nodes = [i + 1 for i, deg in enumerate(target_degrees) if deg == end_degree]
    if not end_nodes:
        return [], top_group_indices
    top_group_set = {idx - 1 for idx in top_group_indices}
    
    def dfs(curr_node, path, visited):
        if len(path) == group_size:
            if (curr_node + 1) in end_nodes:
                all_paths.append(list(path))
            return
        for next_node in range(n):
            if next_node in top_group_set and not visited[next_node]:
                if matrix[curr_node][next_node] == 1:
                    visited[next_node] = True
                    path.append(next_node + 1)
                    dfs(next_node, path, visited)
                    path.pop()
                    visited[next_node] = False

    for start_node_1based in top_group_indices:
        start_node = start_node_1based - 1
        if start_node_1based in end_nodes and group_size > 1:
            continue
        visited = [False] * n
        visited[start_node] = True
        path = [start_node_1based]
        dfs(start_node, path, visited)
        
    return all_paths, top_group_indices


# =====================================================================
# 3. コアロジック（すべてのサイクルに「完全に内包されるパス」があるか判定）
# =====================================================================
def get_fully_embedded_paths(paths, cycles):
    """
    上位グループパスのうち、『すべてのハミルトンサイクルに完全に含まれている』
    （＝パスのすべての辺がサイクルの辺の集合のサブセットになっている）パスを抽出する。
    """
    if not paths or not cycles:
        return []

    embedded_paths = []
    
    for p in paths:
        # パスを構成するすべての有向辺のセット
        path_edges = set((p[i], p[i+1]) for i in range(len(p) - 1))
        
        is_embedded_in_all = True
        for c in cycles:
            # サイクルを構成するすべての有向辺のセット
            cycle_edges = set((c[i], c[i+1]) for i in range(len(c) - 1))
            
            # パスの「すべての辺」が、サイクルの辺に含まれているかをチェック
            # 1つでも含まれていないサイクルがあれば、そのパスは完全内包ではない
            if not path_edges.issubset(cycle_edges):
                is_embedded_in_all = False
                break
        
        # すべてのハミルトンサイクルに完全に含まれていた場合、リストに追加
        if is_embedded_in_all:
            embedded_paths.append(p)
            
    return embedded_paths


# --- メイン処理実行 ---
# ユーザー様が例示された6ノード（全80通り）の出次数シーケンスを設定
target_degrees = [4,4,4,3,2,2,2]
end_degree = 3

print(f"【ステップ 1】出次数シーケンス {target_degrees} を満たす全トーナメントを生成中...")
all_tournaments = generate_all_tournaments(target_degrees)
total_count = len(all_tournaments)
print(f"-> 条件に適合するラベル付きトーナメントは全部で {total_count} 通り見つかりました。\n")

print("【ステップ 2】全通りを検証し、上位パスがすべてのサイクルに完全内包されるトーナメントを探索中...")
matched_tournaments = []

for idx, tournament in enumerate(all_tournaments, 1):
    paths, _ = find_all_paths_in_top_group(tournament, target_degrees, end_degree=end_degree)
    cycles = find_all_hamiltonian_cycles_1_based(tournament)
    
    # すべてのハミルトンサイクルに丸ごと含まれてしまっているパスを取得
    embedded_paths = get_fully_embedded_paths(paths, cycles)
    
    if embedded_paths:
        matched_tournaments.append({
            'index': idx,
            'matrix': tournament,
            'paths': paths,
            'embedded_paths': embedded_paths,
            'cycles': cycles
        })

print(f"-> 検証完了。条件を満たすトーナメントの数: {len(matched_tournaments)} / {total_count}\n")

# --- 結果の出力 ---
if matched_tournaments:
    print("=====================================================")
    print("★ 目的のパターン（ハミルトンサイクルに完全内包されるパスを持つ）のトーナメントを表示します ★")
    print("=====================================================")
    
    # 条件を満たすすべてのトーナメントの情報を出力
    for target in matched_tournaments:
        print(f"\n■ 発見したトーナメント行列 (全{total_count}通り中の {target['index']} 番目):")
        print("[")
        for row in target['matrix']:
            print(f"  {row},")
        print("]")
        
        print(f" └─ 存在する上位グループの有向パス ({len(target['paths'])}通り):")
        for i, p in enumerate(target['paths'], 1):
            print(f"    パス {i}: {' -> '.join(map(str, p))}")
            
        print(f" └─ 🚨 すべてのハミルトンサイクルに完全に含まれている（内包される）パス:")
        for i, p in enumerate(target['embedded_paths'], 1):
            print(f"    内包パス {i}: {' -> '.join(map(str, p))}")
            
        print(f" └─ 存在するハミルトンサイクル ({len(target['cycles'])}通り):")
        for i, c in enumerate(target['cycles'], 1):
            print(f"    サイクル {i}: {' -> '.join(map(str, c))}")
        print("-" * 60)
        
    print(f"\n以上の {len(matched_tournaments)} 通りのトーナメントでは、指定された『内包パス』がすべてのハミルトンサイクルの一部となってしまっているため、ハミルトンサイクルを避けながら独立した上位グループの有向パスを作ることができません。")
else:
    print("=====================================================")
    print(" 検索結果: 条件を満たすトーナメントは存在しませんでした。")
    print("=====================================================")