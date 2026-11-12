import trimesh, numpy as np, csv, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import os; R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/'
rand=[(float(r['x_mm']),float(r['y_mm'])) for r in csv.DictReader(open(R+'data/lily58-pro-printrand.csv'))]
rand=[(x+6 if x>=223-158.6 else x,y) for x,y in rand]
def kc(x,y): return x-158.6, 46.21-y
fig,axs=plt.subplots(1,2,figsize=(18,8.5))
for ax,(z,parts,title) in zip(axs,[(8.3,['bak'],'bak, doorsnede z=8,3 (printhoogte)'),(13.3,['plaat','bak_top'],'plaat z=13,3 + kap z=20')]):
    for name,zz,col in [('helft_rechts_bak',z if 'bak' in parts else None,'#7a8794'),('helft_rechts_plaat',13.3 if 'plaat' in parts else None,'#33618f'),('helft_rechts_kap',20.0 if 'plaat' in parts else None,'#b5651d')]:
        if zz is None: continue
        m=trimesh.load(R+'behuizing/export/'+name+'.stl'); sec=m.section(plane_origin=(0,0,zz),plane_normal=(0,0,1))
        if sec is None: continue
        for e in sec.discrete: ax.plot(e[:,0],e[:,1],color=col,lw=1)
    xs,ys=zip(*(rand+[rand[0]])); ax.plot(xs,ys,'g--',lw=0.8,label='print')
    for nm,(x,y) in {'USB':kc(101,37),'TRRS':kc(87.9,37),'reset':kc(85,67.7),'J_NP':kc(229.4,81.75),'OLED-hdr':kc(100.5,74.6),'ProMicro':kc(101,56)}.items():
        ax.plot(x,y,'r+',ms=10); ax.annotate(nm,(x,y),fontsize=8,color='r',xytext=(3,3),textcoords='offset points')
    ax.add_patch(plt.Rectangle(kc(92,72.5),18,33,fill=False,ec='m',lw=0.8,ls=':'))  # Pro Micro 18x33
    ax.add_patch(plt.Rectangle((kc(100.5,0)[0]-6, kc(0,74.6)[1]+1),12,38,fill=False,ec='c',lw=0.8,ls=':'))  # OLED-module
    ax.set_aspect('equal'); ax.grid(alpha=0.3); ax.set_title(title); ax.legend(loc='lower right',fontsize=8)
plt.tight_layout(); plt.savefig(R+'behuizing/afbeeldingen/helft_doorsnede.png',dpi=95)
