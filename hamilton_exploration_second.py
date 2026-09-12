import itertools, time, random

def build_remaining_table(n, edges):
    """
    残りの試合数テーブルを作成する関数
    ある試合の時点で、各チームが「あと何試合残っているか」を逆算して保持する。
    """
    m = len(edges)
    remaining_games = [[0] * n for _ in range(m + 1)]
    for i in range(m - 1, -1, -1):
        for node in range(n):
            remaining_games[i][node] = remaining_games[i + 1][node]
        u, v = edges[i]
        remaining_games[i][u] += 1
        remaining_games[i][v] += 1
    return remaining_games


def find_all_hamiltonian_cycles_1_based(adj, n):
    """
    1から始まるすべてのハミルトン閉路を探索する関数
    """
    all_cycles = []
    full_edges_union = 0  # 実際に通った(u * n + v)の位置をビットマスクで保存

    def backtrack(curr, path, visited_mask, path_bits):
        nonlocal full_edges_union
        if len(path) == n:
            if adj[curr] & 1:  # ノード0（チーム1）に戻るエッジがあるか確認
                all_cycles.append([v + 1 for v in path] + [1])
                full_edges_union |= path_bits | (1 << (curr * n + 0))
            return
        rem = adj[curr] & ~visited_mask
        while rem:
            nxt = (rem & -rem).bit_length() - 1
            rem &= rem - 1
            path.append(nxt)
            backtrack(nxt, path, visited_mask | (1 << nxt), path_bits | (1 << (curr * n + nxt)))
            path.pop()

    backtrack(0, [0], 1, 0)
    return all_cycles, full_edges_union


def find_all_paths_in_top_group(adj, n, target_degrees, end_degree):
    """
    上位グループ内でのすべてのパスを探索する関数
    """
    # 勝ち数が end_degree 以上のチームのインデックスを抽出
    top_group_indices = [i for i, d in enumerate(target_degrees) if d >= end_degree]
    top_set_mask = 0
    for i in top_group_indices:
        top_set_mask |= (1 << i)
    group_size = len(top_group_indices)
    # 勝ち数がちょうど end_degree であるチーム（ゴールのノード）
    end_nodes = {i for i, d in enumerate(target_degrees) if d == end_degree}
    all_paths = []
    edges_union = 0
    if not end_nodes:
        return all_paths, [i + 1 for i in top_group_indices], edges_union

    def dfs(curr, path, visited_mask, path_bits):
        nonlocal edges_union
        if len(path) == group_size:
            if curr in end_nodes:
                all_paths.append([x + 1 for x in path])
                edges_union |= path_bits
            return
        rem = adj[curr] & top_set_mask & ~visited_mask
        while rem:
            nxt = (rem & -rem).bit_length() - 1
            rem &= rem - 1
            path.append(nxt)
            dfs(nxt, path, visited_mask | (1 << nxt), path_bits | (1 << (curr * n + nxt)))
            path.pop()

    for start in top_group_indices:
        if start in end_nodes and group_size > 1:
            continue
        dfs(start, [start], 1 << start, 0)

    return all_paths, [i + 1 for i in top_group_indices], edges_union


def is_perfect_fast(adj, n, target_degrees, end_degree):
    """
    【高速判定用関数】
    負荷の低いチェックを先に実行：まずパスを探索（通常はこちらの方が小さく、枝刈りしやすいため）。
    パスが存在する場合のみ、ハミルトン閉路を計算する。
    「全てのパス」と「全ての閉路」を総当たりで比較する（O(パス数 × 閉路数)）のではなく、
    それぞれが使用したエッジの論理和（ビットマスク）同士を比較することで、数学的に同等の判定を瞬時に行う。
    """
    paths, _, path_edges = find_all_paths_in_top_group(adj, n, target_degrees, end_degree)
    if not paths:
        return False, None, None
    cycles, cycle_edges = find_all_hamiltonian_cycles_1_based(adj, n)
    if not cycles:
        return False, None, None
    # パスが使ったエッジと、閉路が使ったエッジが1つでも重複していれば不合格
    if path_edges & cycle_edges:
        return False, None, None
    return True, paths, cycles


def search(target_degrees, end_degree, time_budget=None, progress_every=2_000_000, stop_at_first=True):
    """
    系統的（網羅的）な探索を行う関数（DFSによるバックトラック）
    """
    n = len(target_degrees)
    edges = list(itertools.combinations(range(n), 2))
    m = len(edges)
    remaining_games = build_remaining_table(n, edges)

    current_degrees = [0] * n
    adj = [0] * n  # 隣接ビットマスク: adj[u] の bit v が 1 なら「u が v に勝利」を意味する

    stats = {'calls': 0, 'candidates': 0, 'found': []}
    start_t = time.time()

    def backtrack(edge_idx):
        stats['calls'] += 1
        if progress_every and stats['calls'] % progress_every == 0:
            elapsed = time.time() - start_t
            print(f"  ...進捗: 呼び出し回数={stats['calls']:,} チェックした候補数={stats['candidates']:,} 経過時間={elapsed:.1f}秒", flush=True)
            if time_budget and elapsed > time_budget:
                raise TimeoutError

        if edge_idx == m:
            stats['candidates'] += 1
            ok, paths, cycles = is_perfect_fast(adj, n, target_degrees, end_degree)
            if ok:
                stats['found'].append((adj[:], paths, cycles))
                if stop_at_first:
                    raise StopIteration
            return

        u, v = edges[edge_idx]
        needed_u = target_degrees[u] - current_degrees[u]
        needed_v = target_degrees[v] - current_degrees[v]
        rem_u_after = remaining_games[edge_idx + 1][u]
        rem_v_after = remaining_games[edge_idx + 1][v]

        # パターン1: u が v に勝つ場合
        if 0 <= needed_u - 1 <= rem_u_after and needed_v <= rem_v_after:
            adj[u] |= (1 << v)
            current_degrees[u] += 1
            backtrack(edge_idx + 1)
            current_degrees[u] -= 1
            adj[u] &= ~(1 << v)

        # パターン2: v が u に勝つ場合
        if 0 <= needed_v - 1 <= rem_v_after and needed_u <= rem_u_after:
            adj[v] |= (1 << u)
            current_degrees[v] += 1
            backtrack(edge_idx + 1)
            current_degrees[v] -= 1
            adj[v] &= ~(1 << u)

    try:
        backtrack(0)
        status = "探索完了（全ルートチェック済）"
    except StopIteration:
        status = "最初の1つを発見"
    except TimeoutError:
        status = "タイムアウト"

    elapsed = time.time() - start_t
    print(f"\nステータス={status} 総呼び出し回数={stats['calls']:,} チェックした候補数={stats['candidates']:,} "
          f"発見した完全トーナメント数={len(stats['found'])} 経過時間={elapsed:.1f}秒")
    return stats, status


def random_search(target_degrees, end_degree, time_budget=30, progress_every=200):
    """
    【代替戦略：ランダム探索】
    指定された勝ち数を満たすトーナメントの選択肢は、探索ツリー上で非常に高密度に存在します（数百万通り以上）。
    そのため、条件を満たすランダムなトーナメントを1つずつ作成して（1回あたり数分の1ミリ秒と非常に高速）、
    それが『完全（Perfect）』であるかを繰り返し検証します。
    空間全体を網羅しようとせずに、「完全なトーナメントが簡単に見つかるか、それとも難しいか」を素早く把握するのに適しています。
    """
    n = len(target_degrees)
    edges = list(itertools.combinations(range(n), 2))
    m = len(edges)
    remaining_games = build_remaining_table(n, edges)

    def random_valid_tournament():
        """条件（各チームの勝ち数）を満たすトーナメントをランダムに1つ構築する"""
        current_degrees = [0] * n
        adj = [0] * n

        def backtrack(edge_idx):
            if edge_idx == m:
                return current_degrees == target_degrees
            u, v = edges[edge_idx]
            needed_u = target_degrees[u] - current_degrees[u]
            needed_v = target_degrees[v] - current_degrees[v]
            rem_u_after = remaining_games[edge_idx + 1][u]
            rem_v_after = remaining_games[edge_idx + 1][v]
            opts = []
            if 0 <= needed_u - 1 <= rem_u_after and needed_v <= rem_v_after:
                opts.append('u')
            if 0 <= needed_v - 1 <= rem_v_after and needed_u <= rem_u_after:
                opts.append('v')
            random.shuffle(opts)  # 勝敗の選択肢をランダムにシャッフル
            for o in opts:
                if o == 'u':
                    adj[u] |= (1 << v); current_degrees[u] += 1
                    if backtrack(edge_idx + 1):
                        return True
                    current_degrees[u] -= 1; adj[u] &= ~(1 << v)
                else:
                    adj[v] |= (1 << u); current_degrees[v] += 1
                    if backtrack(edge_idx + 1):
                        return True
                    current_degrees[v] -= 1; adj[v] &= ~(1 << u)
            return False

        backtrack(0)
        return adj[:]

    tested = 0
    start_t = time.time()
    while time.time() - start_t < time_budget:
        adj = random_valid_tournament()
        tested += 1
        ok, paths, cycles = is_perfect_fast(adj, n, target_degrees, end_degree)
        if tested % progress_every == 0:
            print(f"  ...{tested:,} 個のランダム・トーナメントを検証済、経過時間={time.time()-start_t:.1f}秒", flush=True)
        if ok:
            print(f"\n【発見】 {tested:,} 個のランダムサンプルを検証後、完全トーナメントが見つかりました！ "
                  f"({time.time()-start_t:.1f}秒)")
            return adj, paths, cycles
    print(f"\n指定された時間制限（{time_budget}秒）内に、{tested:,} 個のサンプルから完全トーナメントは見つかりませんでした。")
    return None, None, None


if __name__ == "__main__":
    target_degrees = [6,6,6,6,6,5,4,4,4,4,4]
    
    # 注意: target_degrees の中に「3以上のチーム（上位グループ）」をパス探索の対象にしようとしていますが、
    # 条件の組み合わせ上、パスの検索結果が常に空になり、完全なトーナメントが絶対にみつからない状態になっています。
    # 本来意図されていた挙動を再現するには、ここを 4 (出現する最小の勝ち数) に変更してください。
    # 3のままにすると、結果が「見つからない」状態ですぐに終了します。
    end_degree = 4

    # モード設定: 
    # "random" = 高速な確率的探索（探索空間が膨大なため推奨）
    # "systematic" = 枝刈り付きの網羅的DFS（数十億の候補があるため、このチーム数設定では終わりません）
    MODE = "random"  

    if MODE == "random":
        adj, paths, cycles = random_search(target_degrees, end_degree, time_budget=600, progress_every=50)
        stats = {'found': [(adj, paths, cycles)] if adj else []}
    else:
        stats, status = search(target_degrees, end_degree, time_budget=600, progress_every=1_000_000, stop_at_first=True)

    if stats['found']:
        adj, paths, cycles = stats['found'][0]
        n = len(target_degrees)
        print("\n隣接行列 (1 = 行のチームが列のチームに勝利):")
        for u in range(n):
            row = [1 if (adj[u] >> v) & 1 else (2 if (adj[v] >> u) & 1 else 0) for v in range(n)]
            print(" ", row)
        print(f"\n検出されたパス ({len(paths)} 個):")
        for p in paths:
            print("  " + " -> ".join(map(str, p)))
        print(f"\n検出された閉路（サイクル） ({len(cycles)} 個):")
        for c in cycles:
            print("  " + " -> ".join(map(str, c)))