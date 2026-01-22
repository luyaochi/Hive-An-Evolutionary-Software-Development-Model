---

# Foundations — 形式化規格

**版本：v1.0.0**

**狀態：** Stable
**範圍：** 單一儲存庫、以 agent 驅動、以路徑隔離的演化式開發
**讀者對象：** 系統設計者、核心貢獻者、agent／控制器實作者

---

## 0. 版本政策（Versioning Policy）

本文件遵循 **語意化版本控制（Semantic Versioning）**：

* **MAJOR（主版號）**：核心數學模型或保證性質的變更
* **MINOR（次版號）**：新增限制、角色或可選擴充
* **PATCH（修訂版號）**：說明補充、符號修正、範例新增

向後相容性僅適用於**定理與保證**，不適用於敘述文字。

---

## 1. 形式模型（Formal Model）

### 1.1 狀態空間（State Space）

令：

* ( \mathcal{F} ) 為檔案路徑集合
* ( \Sigma^* ) 為檔案內容的所有可能字串集合

一個工作空間狀態定義為部分函數：

[
s: \mathcal{F} \rightharpoonup \Sigma^*
]

表示：某些路徑存在對應內容，其餘路徑未定義。

---

### 1.2 相依圖（Dependency Graph，圖論結構）

定義一個有向圖：

[
G = (V, E)
]

* ( V )：模組（cells）集合
* ( (u, v) \in E )：表示模組 (u) 依賴模組 (v)

每一個 cell (c \in V) 擁有其**唯一且排他的寫入領域**：

[
P(c) \subseteq \mathcal{F}
]

**隔離約束（Isolation Constraint）：**

[
c \neq d \Rightarrow P(c) \cap P(d) = \varnothing
]

即：不同 cell 之間不得有重疊的寫入路徑。

---

### 1.3 外部契約（Canonical Summary）

每個 cell 對外暴露一個**標準化契約（canonical contract）**：

[
\text{sum}*c : s|*{P(c)} \rightarrow \mathcal{K}_c
]

其中 ( \mathcal{K}_c ) 為該 cell 的契約空間（例如 API、invariants、事件定義等）。

**下游相依模組只能依賴 ( \mathcal{K}_c )，不得依賴原始檔案內容。**

---

## 2. 狀態控制（有限狀態機，FSM）

### 2.1 Cell 狀態

每個 cell (c) 具有一個狀態：

[
q_c \in Q = {\text{OPEN}, \text{IN_PROGRESS}, \text{CLOSED}, \text{LOCKED}}
]

---

### 2.2 具防護條件的狀態轉移（Guarded Transitions）

一個狀態轉移表示為：

[
(q_c, s) \rightarrow (q_c', s')
]

僅在以下條件成立時才允許轉移：

[
\text{Gate}_c(q_c \rightarrow q_c', s') = \text{true}
]

Gate（驗證閘門）代表所有必要的驗證條件已通過。

---

## 3. 演化動力學（離散動力系統）

### 3.1 Agent 更新算子（Agent Update Operator）

對 cell (c)，一次 agent 更新定義為：

[
U_c : s \rightarrow s'
]

並必須滿足**路徑局部性（path locality）**：

[
s'|*{\mathcal{F} \setminus P(c)} = s|*{\mathcal{F} \setminus P(c)}
]

即：agent 僅能修改屬於該 cell 的路徑範圍。

---

### 3.2 義務集合與驗證（Obligations & Verification）

定義一個**有限義務集合**：

[
O_c = O_c^{code} \cup O_c^{tests} \cup O_c^{spec} \cup O_c^{lists}
]

定義一個**外部驗證器**：

[
V_c(s) \subseteq O_c
]

> 注意：
> TASKS、CHECKS、RESULTS 等完成清單檔案**不具權威性**。
> 是否完成，僅由 (V_c) 的外部驗證結果決定。

---

### 3.3 Lyapunov 勢能函數（Lyapunov Potential）

定義：

[
U_c(s) = O_c \setminus V_c(s)
\quad,\quad
\Phi_c(s) = |U_c(s)|
]

其中 ( \Phi_c ) 為系統的 **Lyapunov-like 勢能函數**，表示未完成義務的數量。

---

### 3.4 接受規則（單調性閘門）

一次更新被接受，若且唯若：

[
\text{Accept}_c(s \rightarrow s') \iff V_c(s') \supseteq V_c(s)
]

即：**不得破壞任何已完成的義務**。

---

## 4. 核心定理（Core Theorems）

---

### 定理 1 — Cell 層級的有限時間收斂

**假設：**

1. (O_c) 為有限集合
2. 僅接受符合 Accept 規則的更新
3. 若 ( \Phi_c(s) > 0 )，則存在一個被接受的更新，使 ( \Phi_c ) 嚴格下降

**結論：**

存在 ( T \le |O_c| )，使得在 (T) 次被接受的更新後：

[
\Phi_c(s_T) = 0
]

**詮釋：**
每一個 cell 皆在有限次迭代內收斂。

---

### 定理 2 — 核心模組的相容性保持性

定義全域相容性：

[
\text{Compat}(s) \iff \forall (u,v)\in E,
\text{Compat}_{u \leftarrow v}(\text{sum}_u(s), \text{sum}_v(s))
]

**假設：**

* 初始狀態 ( s^{(0)} ) 滿足 ( \text{Compat} )
* 核心模組的每次更新皆為**時間序列化**，並通過相容性閘門

**結論：**

[
\forall t,\ \text{Compat}(s^{(t)})
]

**詮釋：**
時間序列化的演化能在整個過程中保持所有下游不變量。

---

## 5. 設計含意（規範性）

* 僅在**沒有共享不變量**的情況下允許平行演化
* 任何具有下游相依的 cell **必須以時間序列方式演化**
* Agent 是最佳化算子，**不是權威來源**
* 收斂性是系統性質，而非模型或 agent 能力的性質

---

## 6. 穩定性保證（v1.0.0）

本版本保證：

* 每個 cell 皆可有限時間收斂
* 具相依關係之核心模組不變量可被保持
* 系統不依賴 agent 的誠實性或完整性
* 接受／拒絕語義具決定性（deterministic）

---

# 附錄 A — 版本路線圖（非規範性）

### v1.1（次版）

* 多 agent 仲裁策略
* 機率式驗證容忍度
* 義務集合的部分排序

### v2.0（主版）

* 跨 cell 的 Lyapunov 耦合
* 循環相依的處理機制
* 連續時間近似模型

---


