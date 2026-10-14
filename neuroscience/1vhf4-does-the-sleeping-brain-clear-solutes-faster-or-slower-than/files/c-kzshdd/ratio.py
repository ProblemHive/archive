# ratio.py - what kind of difference separates the two states in the photometry curves of Miao et al. 2024?
# Data: mean curves of Fig. 2d-g and Fig. 3b from the paper's source data (CC BY 4.0, doi:10.6084/m9.figshare.25483339).
# If the two states of a pair differ by a first-order loss rate (C falls as exp(-k t), k larger in the control),
# the ratio control/treated keeps falling: ratio(t) = exp(-dk t). If they differ by a constant factor (less dye
# took part, or a loss that was over early), the ratio is flat. The paper's own loss term, tau/(t + tau)
# (its equation 8), lies between the two; its prediction is printed from the paper's peak clearances.
# Needs numpy and xlsx_min.py (standard-library xlsx reader).
import numpy as np
from xlsx_min import sheets

BIN = 120.0   # seconds per bin

def load():
    out = {}
    for name, rows in sheets('src/Miao_et_al_Figure2.xlsx'):
        if name not in ('Figure2d', 'Figure2e', 'Figure2f', 'Figure2g'):
            continue
        head = rows[0][1]
        t = np.array([r.get('A', np.nan) for _, r in rows[1:]], float)
        for c in 'BD':
            y = np.array([r[c] if isinstance(r.get(c), float) else np.nan for _, r in rows[1:]], float)
            ok = np.isfinite(t) & np.isfinite(y)
            tb = np.floor(t[ok] / BIN).astype(int)
            n = np.bincount(tb); s = np.bincount(tb, y[ok])
            keep = n > 0
            out[(name, head[c].replace(' mean', ''))] = ((np.arange(len(n))[keep] + 0.5) * BIN / 3600, s[keep] / n[keep])
    return out

# percent clearance at peak, Extended Data Table 1 of the paper (control, treated)
TABLE = {'DEX': (74.9, 36.0), 'KX': (76.4, 39.8), 'PENTO': (81.5, 57.3), 'Sleep': (69.7, 52.8)}

if __name__ == '__main__':
    d = load()
    pairs = [('Figure2d', 'Saline', 'DEX'), ('Figure2e', 'Saline', 'KX'), ('Figure2f', 'Saline', 'PENTO'), ('Figure2g', 'Wake', 'Sleep')]
    print('1. MEAN CURVES (2-minute bins): peak, time of peak, end of record')
    pk = {}
    for fig, a, b in pairs:
        for s in (a, b):
            t, y = d[(fig, s)]
            i = np.argmax(y); pk[(fig, s)] = (t[i], y[i])
            print(f'  {fig} {s:6s} peak {y[i]:.3f} at {t[i]:.2f} h; record ends {t[-1]:.2f} h')
    hrs = np.array([0.5, 1, 1.5, 2, 2.5, 3, 4, 5.0])
    print()
    print('2. RATIO control/treated of the mean curves')
    print('   pair          ' + ' '.join(f'{h:>5g}h' for h in hrs) + ' | slope of log ratio per hour: 1-5 h, 2-5 h')
    for fig, a, b in pairs:
        ta, ya = d[(fig, a)]; tb, yb = d[(fig, b)]
        ra = np.interp(hrs, ta, ya) / np.interp(hrs, tb, yb)
        sl = []
        for lo in (1, 2):
            g = np.arange(lo, 5.0001, 1 / 30)
            sl.append(np.polyfit(g, np.log(np.interp(g, ta, ya) / np.interp(g, tb, yb)), 1)[0])
        print(f'   {a + "/" + b:13s} ' + ' '.join(f'{x:6.2f}' for x in ra) + f' | {sl[0]:+.3f}, {sl[1]:+.3f}')
    print()
    print('3. WHAT EACH ACCOUNT PREDICTS for the ratio at 2, 3, 4, 5 h, anchored to the observed ratio at 2 h')
    for fig, a, b in pairs:
        ta, ya = d[(fig, a)]; tb, yb = d[(fig, b)]
        obs = np.interp([2, 3, 4, 5], ta, ya) / np.interp([2, 3, 4, 5], tb, yb)
        tt = np.array([2, 3, 4, 5.0])
        dk = -np.log(obs[0]) / 2                       # first-order rate difference that gives the 2 h ratio from ratio 1 at t = 0
        first = np.exp(-dk * tt)
        ca, cb = TABLE[b]
        tau_a = pk[(fig, a)][0] * (100 - ca) / ca       # equation 9 of the paper: clearance = t/(t + tau) at the peak
        tau_b = pk[(fig, b)][0] * (100 - cb) / cb
        hyp = (tau_a / (tt + tau_a)) / (tau_b / (tt + tau_b))
        print(f'   {a + "/" + b:13s} observed      ' + ' '.join(f'{x:.2f}' for x in obs))
        print(f'   {"":13s} constant factor ' + ' '.join(f'{obs[0]:.2f}' for _ in tt))
        print(f'   {"":13s} first-order   ' + ' '.join(f'{x:.2f}' for x in first) + f'   (rate difference {dk:.2f} per hour)')
        print(f'   {"":13s} paper eq. 8   ' + ' '.join(f'{x:.2f}' for x in hyp) + f'   (tau {tau_a:.2f} h and {tau_b:.2f} h)')
    print()
    print('4. HISTOLOGY (Fig. 3b): dye summed over the anterior-posterior profile, whole-slice means, as a ratio to wake')
    for name, rows in sheets('src/Miao_et_al_Figure3.xlsx'):
        if name != 'Figure3b':
            continue
        head = rows[0][1]
        cols = {head[c]: np.array([r.get(c, np.nan) for _, r in rows[1:]], float) for c in 'ABCDEFG'}
        x = cols['Distance (mm)']
        print(f'   {len(x)} positions from {np.nanmin(x):.2f} to {np.nanmax(x):.2f} mm')
        tot = {k: np.nansum(v) for k, v in cols.items() if k != 'Distance (mm)'}
        for h in ('3h', '5h'):
            w = tot[f'Mean Wake {h}']
            print(f'   {h}: wake/sleep {w / tot[f"Mean Sleep {h}"]:.2f}   wake/KX {w / tot[f"Mean KX {h}"]:.2f}   (sums: wake {w:.2f}, sleep {tot[f"Mean Sleep {h}"]:.2f}, KX {tot[f"Mean KX {h}"]:.2f})')
        for s in ('Wake', 'Sleep', 'KX'):
            print(f'   {s}: 5 h sum / 3 h sum = {tot[f"Mean {s} 5h"] / tot[f"Mean {s} 3h"]:.2f}')
