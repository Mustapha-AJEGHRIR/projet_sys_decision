We have $k$ classes and $k-1$ frontiers (profiles) between classes :
$$
b^1, b^2, \dots, b^h, \dots, b^{k-1}
$$
Lets denote $K = \{ 1, 2, \dots ,k \}$ and  $K_{no\_end} = \{ 1, 2, \dots ,k-1 \}$ and $K_{no\_no\_end} = \{ 1, 2, \dots ,k-2 \}$




$$
\left\{
\begin{split}
Maximize& \quad \alpha \\
subject\ to& \sum_{i \in N} c_{ij}^h + x_j + \epsilon = \lambda &\quad \forall a_j \in A^{*h} , \forall h \in K_{no\_end} \\

& \sum_{i \in N} c_{ij}^{h-1} = \lambda + y_j &\quad \forall a_j \in A^{*h}, \forall h \in \{2, \dots, k\} \\


& \alpha \le x_j , \alpha\le y_j  &\quad  \forall a_j \in A^{*} \\

& c_{ij}^l \le w_i   &\quad \forall i \in N, \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end}\\

& c_{ij}^l \le \delta_{ij}^l   &\quad \forall i \in N, \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end} \\

& c_{ij}^l \ge \delta_{ij}^l -1 + w_i   &\quad  \forall i \in N, \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end}\\

& M \delta_{ij}^l + \epsilon  \ge g_i(a_j) - b_i^l   &\quad \forall i \in N,  \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end}\\

& M(\delta_{ij}^l -1 ) \le g_i(a_j) -b_i^l   &\quad  \forall i \in N, \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end}\\

& \sum_{i\in N} w_i = 1, \quad \lambda\in [0.5, 1] \\

& w_i \in [0, 1] &\quad \forall i \in N \\

& c_{ij}^l, \delta_{ij}^l \in \{ 0, 1\} &\quad \forall i \in N, \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end} \\

& x_j, y_j \in \mathbb R &\quad \forall a_j \in A^* \\

&\alpha \in \mathbb R

\end{split}
\right.
$$




To have the ability of cancelling noise :

$$
\left\{
\begin{split}
Maximize& \quad \sum_{a_j \in A^*} \gamma_j \\
subject\ to& \sum_{i \in N} c_{ij}^h+ \epsilon \le \lambda +M(1-\gamma_j) &\quad \forall a_j \in A^{*h} , \forall h \in K_{no\_end} \\

& \sum_{i \in N} c_{ij}^{h-1} \ge \lambda -M(1-\gamma_j) &\quad \forall a_j \in A^{*h}, \forall h \in \{2, \dots, k\} \\

& c_{ij}^l \le w_i   &\quad \forall i \in N, \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end}\\

& c_{ij}^l \le \delta_{ij}^l   &\quad \forall i \in N, \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end} \\

& c_{ij}^l \ge \delta_{ij}^l -1 + w_i   &\quad  \forall i \in N, \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end}\\

& M \delta_{ij}^l + \epsilon  \ge g_i(a_j) - b_i^l   &\quad \forall i \in N,  \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end}\\

& M(\delta_{ij}^l -1 ) \le g_i(a_j) -b_i^l   &\quad  \forall i \in N, \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end}\\

& b_i^{h +1 } \ge b_i^{h} &\quad \forall i \in N, \forall h \in K_{no\_no\_end} \\

& \sum_{i\in N} w_i = 1, \quad \lambda\in [0.5, 1] \\

& w_i \in [0, 1] &\quad \forall i \in N \\

& c_{ij}^l, \delta_{ij}^l \in \{ 0, 1\} &\quad \forall i \in N, \forall a_j \in A^{*h}, \forall h \in K, \forall l \in \{h, h-1\} \cap K_{no\_end} \\

& x_j, y_j \in \mathbb R &\quad \forall a_j \in A^* \\


\end{split}
\right.
$$
