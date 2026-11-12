import trimesh, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import sys
def render(parts, fn, elev=35, azim=-60, title=''):
    fig = plt.figure(figsize=(12, 8)); ax = fig.add_subplot(111, projection='3d')
    allv = []
    for path, color, dz in parts:
        m = trimesh.load(path); m.apply_translation((0, 0, dz))
        m = m.simplify_quadric_decimation(face_count=min(len(m.faces), 25000)) if len(m.faces) > 25000 else m
        tri = m.vertices[m.faces]
        n = m.face_normals; light = np.clip(n @ np.array([0.3, -0.4, 0.85]), 0.15, 1)
        c = np.array(matplotlib.colors.to_rgb(color)); fc = np.outer(light, c)
        pc = Poly3DCollection(tri, facecolors=fc, edgecolors='none'); ax.add_collection3d(pc); allv.append(m.vertices)
    v = np.vstack(allv); mn, mx = v.min(0), v.max(0); c = (mn + mx) / 2; r = (mx - mn).max() / 2
    ax.set_xlim(c[0]-r, c[0]+r); ax.set_ylim(c[1]-r, c[1]+r); ax.set_zlim(c[2]-r*0.5, c[2]+r*0.5)
    ax.set_box_aspect((1, 1, 0.5)); ax.view_init(elev, azim); ax.set_axis_off(); ax.set_title(title)
    plt.tight_layout(); plt.savefig(fn, dpi=110); plt.close()
import os; os.chdir(os.path.dirname(os.path.abspath(__file__))); E='export/'
render([(E+'helft_rechts_bak.stl','#9aa3ad',0),(E+'helft_rechts_plaat.stl','#5d6670',25),(E+'helft_rechts_kap.stl','#3d444b',45)], 'afbeeldingen/helft_3d.png', title='helft rechts: bak, plaat, kap (uit elkaar)')
render([(E+'helft_rechts_bak.stl','#9aa3ad',0),(E+'helft_rechts_plaat.stl','#5d6670',0),(E+'helft_rechts_kap.stl','#3d444b',0)], 'afbeeldingen/helft_3d_gemonteerd.png', elev=30, azim=-110, title='helft rechts, gemonteerd (achterkant: USB/TRRS)')
render([(E+'numpad_bak.stl','#9aa3ad',0),(E+'numpad_plaat.stl','#5d6670',25)], 'afbeeldingen/numpad_3d.png', title='numpad: bak en plaat')
