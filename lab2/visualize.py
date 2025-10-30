import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
from textwrap import dedent

# ------------------------------------------------------------
# Data (x[mm], y[mm], V[V])
# ------------------------------------------------------------
RAW = dedent(
    """
    x, y, V
    0,-80,1.58
    0,-70,1.7
    0,-60,1.99
    0,-50,2.21
    0,-40,2.67
    0,-30,2.77
    0,-20,3.78
    0,-10,4.17
    0, 0, 4.8
    0, 10,5.02
    0, 20,5.65
    0, 30,6.2
    0, 40,7.07
    0, 50,7.5
    0, 60,7.83
    0, 70,7.93
    0, 80,8.11
    10, -80,1.37
    10, -70,1.41
    10, -60,1.74
    10, -50,1.99
    10, -40,2.35
    10, -30,2.91
    10, -20,3.52
    10, -10,4.38
    10, 0,4.76
    10, 10,5.42
    10, 20,5.99
    10, 30,6.68
    10, 40,7.39
    10, 50,7.78
    10, 60,8.09
    10, 70,8.1
    10, 80,8.39
    20, -80,1.25
    20, -70,1.28
    20, -60,1.32
    20, -50,1.4
    20, -40,1.73
    20, -30,2.23
    20, -20,2.94
    20, -10,3.9
    20, 0,4.7
    20, 10,5.49
    20, 20,6.2
    20, 30,6.9
    20, 40,8.15
    20, 50,8.4
    20, 60,8.35
    20, 70,8.6
    20, 80,8.7
    40, -20,1.56
    40, -15,2.38
    40, -10,3.15
    40, -5,3.87
    40, 0,4.6
    40, 5,5.23
    40, 10,5.98
    40, 15,6.7
    40, 20,7.55
    110, -20,2.12
    110, -15,2.7
    110, -10,3.32
    110, -5,4.22
    110, 0,4.98
    110, 5,5.7
    110, 10,6.38
    110, 15,7.06
    110, 20,7.89
    150, -20,1.83
    150, -15,2.53
    150, -10,3.23
    150, -5,3.94
    150, 0,4.79
    150, 5,5.42
    150, 10,6.19
    150, 15,6.98
    150, 20,7.73
    """
).strip()


def parse_csv_like(text: str):
    xs, ys, vs = [], [], []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("x"):
            continue
        a, b, c = [p.strip() for p in line.split(",")]
        xs.append(float(a))
        ys.append(float(b))
        vs.append(float(c))
    return np.array(xs), np.array(ys), np.array(vs)


x_mm, y_mm, V = parse_csv_like(RAW)

# ------------------------------------------------------------
# Electrode geometry (mm): both start at x=30 now
# ------------------------------------------------------------
POS = dict(x0=30.0, x1=200.0, y0=25.0, y1=45.0)   # positive (top)
NEG = dict(x0=30.0, x1=200.0, y0=-45.0, y1=-25.0)  # negative (bottom)

# ------------------------------------------------------------
# Estimate electrode potentials from inside data (linear V(y))
# Extrapolate fits from y in [-20, 20] to y=±25 and take medians.
# You may override by setting VPLUS / VMINUS to numbers.
# ------------------------------------------------------------
VPLUS = None
VMINUS = None

inside_mask = x_mm >= 40.0
x_inside_unique = np.unique(x_mm[inside_mask])

def fit_line_at_x(x_target: float):
    m = (np.isclose(x_mm, x_target)) & (y_mm >= -20) & (y_mm <= 20)
    yy, vv = y_mm[m], V[m]
    A = np.column_stack([yy, np.ones_like(yy)])
    a, b = np.linalg.lstsq(A, vv, rcond=None)[0]  # V = a*y + b
    return a, b

if VPLUS is None or VMINUS is None:
    vpos_list, vneg_list = [], []
    for xx in x_inside_unique:
        a, b = fit_line_at_x(xx)
        vpos_list.append(a * 25.0 + b)   # y=+25
        vneg_list.append(a * (-25.0) + b)  # y=-25
    VPLUS_est = float(np.median(vpos_list))
    VMINUS_est = float(np.median(vneg_list))
    if VPLUS is None:
        VPLUS = VPLUS_est
    if VMINUS is None:
        VMINUS = VMINUS_est

print(
    f"Estimated electrode potentials: V+ ≈ {VPLUS:.2f} V, "
    f"V- ≈ {VMINUS:.2f} V, ΔV ≈ {VPLUS - VMINUS:.2f} V"
)

# Grid and anchors
# ------------------------------------------------------------
dx_mm = 1.0  # grid spacing; smaller = smoother but slower
XMAX = 160.0  # cutoff for domain and plot (set as you like)
# Or automatic: XMAX = max(x_mm) + 10.0
x_grid = np.arange(0.0, XMAX + dx_mm, dx_mm)
y_grid = np.arange(-80.0, 80.0 + dx_mm, dx_mm)
X, Y = np.meshgrid(x_grid, y_grid)
ny, nx = Y.shape

def nearest_idx(arr: np.ndarray, val: float) -> int:
    return int(np.argmin(np.abs(arr - val)))

fixed = np.zeros((ny, nx), dtype=bool)
val = np.zeros((ny, nx), dtype=float)

# Anchor all measurements (inside + outside)
for xi, yi, vi in zip(x_mm, y_mm, V):
    i = nearest_idx(x_grid, xi)
    j = nearest_idx(y_grid, yi)
    fixed[j, i] = True
    val[j, i] = vi

# Anchor electrodes as equipotential regions
pos_mask = (X >= POS["x0"]) & (X <= POS["x1"]) & (Y >= POS["y0"]) & (
    Y <= POS["y1"]
)
neg_mask = (X >= NEG["x0"]) & (X <= NEG["x1"]) & (Y >= NEG["y0"]) & (
    Y <= NEG["y1"]
)
fixed[pos_mask] = True
val[pos_mask] = VPLUS
fixed[neg_mask] = True
val[neg_mask] = VMINUS

# ------------------------------------------------------------
# Solve Laplace's equation ∇²V = 0 with:
# - Dirichlet at fixed nodes (measurements + electrodes)
# - Zero-flux (Neumann) on the outer box edges
# Discrete 5-point stencil.
# ------------------------------------------------------------
N = nx * ny
A = lil_matrix((N, N), dtype=np.float64)
b = np.zeros(N, dtype=np.float64)

def idx(i, j):
    return j * nx + i

for j in range(ny):
    for i in range(nx):
        k = idx(i, j)
        if fixed[j, i]:
            A[k, k] = 1.0
            b[k] = val[j, i]
            continue

        # neighbors: E, W, N, S (only if inside grid)
        neighbors = []
        if i + 1 < nx:
            neighbors.append((i + 1, j))
        if i - 1 >= 0:
            neighbors.append((i - 1, j))
        if j + 1 < ny:
            neighbors.append((i, j + 1))
        if j - 1 >= 0:
            neighbors.append((i, j - 1))

        Nnb = len(neighbors)
        A[k, k] = float(Nnb)
        sum_known = 0.0

        for ii, jj in neighbors:
            kk = idx(ii, jj)
            if fixed[jj, ii]:
                sum_known += val[jj, ii]
            else:
                A[k, kk] = -1.0

        b[k] = sum_known

V_flat = spsolve(A.tocsr(), b)
Vg = V_flat.reshape(ny, nx)

# ------------------------------------------------------------
# Plot
# ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 7))

cf = ax.contourf(
    X, Y, Vg, levels=28, cmap="viridis", antialiased=True
)
contours = ax.contour(X, Y, Vg, levels=14, colors="k", linewidths=0.7, alpha=0.7)
ax.clabel(contours, inline=True, fontsize=7, fmt="%.1f", colors="k")

plt.colorbar(cf, ax=ax, label="Potencjał V [V]")

# samples
ax.scatter(
    x_mm, y_mm, s=16, c="w", edgecolor="k", linewidth=0.5, zorder=3,
    label="pomiary"
)

# electrode overlays (truncate at XMAX for drawing)
width_pos = max(0.0, min(POS["x1"], XMAX) - POS["x0"])
pos_rect = Rectangle(
    (POS["x0"], POS["y0"]),
    width_pos,
    POS["y1"] - POS["y0"],
    linewidth=1.6,
    edgecolor="crimson",
    facecolor="crimson",
    alpha=0.25,
    label="elektroda dodatnia",
    zorder=4,
)

width_neg = max(0.0, min(NEG["x1"], XMAX) - NEG["x0"])
neg_rect = Rectangle(
    (NEG["x0"], NEG["y0"]),
    width_neg,
    NEG["y1"] - NEG["y0"],
    linewidth=1.6,
    edgecolor="royalblue",
    facecolor="royalblue",
    alpha=0.25,
    label="elektroda ujemna",
    zorder=4,
)
ax.add_patch(pos_rect)
ax.add_patch(neg_rect)

ax.set_title("Potencjał elektryczny")
ax.set_xlabel("x [mm]")
ax.set_ylabel("y [mm]")
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(0, XMAX)
ax.set_ylim(-80, 80)
ax.legend(loc="upper right", framealpha=0.95)

plt.tight_layout()
plt.show()
