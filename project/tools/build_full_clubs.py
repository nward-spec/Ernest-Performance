"""Full-club composites: keep the real head+shaft, straighten so the shaft is
vertical, extend the club's own shaft, cap with a rendered grip. One flat PNG."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os, math, statistics

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

SRC='project/assets/products/cutout'
OUT='project/assets/products/fullclub'
os.makedirs(OUT, exist_ok=True)

# edge the real shaft exits (before straighten); ext/grip lengths (x head-image H)
CFG={
 'driver':  dict(edge='bottom', ext=0.85, grip=0.40, label='VENTUS BLACK'),
 'fairway': dict(edge='bottom', ext=0.90, grip=0.42, label='VENTUS BLACK'),
 'wedge':   dict(edge='bottom', ext=0.85, grip=0.40, label='DYNAMIC GOLD'),
 'irons':   dict(edge='bottom', ext=0.80, grip=0.40, label='DYNAMIC GOLD'),
 'putter':  dict(edge='bottom', ext=0.62, grip=0.40, shaft_scale=0.55, grip_scale=1.6, grip_cap=1.7, ext_mul=2.7),
}

def _load_grip(name):
    try: return Image.open(f'{os.path.dirname(SRC)}/raw/{name}').convert('RGBA')
    except Exception: return None
_GP=_load_grip('grip-golfpride.png'); _SS=_load_grip('grip-superstroke.png')
GRIP_MAP={'driver':_GP,'fairway':_GP,'irons':_GP,'wedge':_GP,'putter':_SS}  # Golf Pride / SuperStroke
_GRA=_load_grip('shaft-graphite.png'); _STL=_load_grip('shaft-steel.png')
SHAFT_MAP={'driver':_GRA,'fairway':_GRA,'irons':_STL,'wedge':_STL}  # real shaft photos (putter=synthetic dark)

def runs(alpha,y,w,thr=50):
    out=[];s=None
    for x in range(w):
        on=alpha[x,y]>thr
        if on and s is None: s=x
        if (not on) and s is not None: out.append((s,x-1));s=None
    if s is not None: out.append((s,w-1))
    return out

def shaft_run(alpha,y,w):
    r=runs(alpha,y,w)
    return min(r,key=lambda t:t[1]-t[0]) if r else None

def axis_at(im,edge):
    w,h=im.size; al=im.split()[-1].load()
    yb = h-3 if edge=='bottom' else 2
    yi = h-3-int(h*0.28) if edge=='bottom' else 2+int(h*0.28)
    r0=shaft_run(al,yb,w); r1=shaft_run(al,yi,w)
    if not r0 or not r1: return None
    c0=(r0[0]+r0[1])/2; c1=(r1[0]+r1[1])/2
    vx=c0-c1; vy=(yb-yi); L=math.hypot(vx,vy) or 1
    return (c0,yb,vx/L,vy/L,max(8,r0[1]-r0[0]+1))

def trim(im):
    bb=im.split()[-1].getbbox(); return im.crop(bb) if bb else im

def trim_stub(im, frac=0.20, keep=0.05):
    """Crop the baked shaft stub off the bottom of a head image, keeping the head
    + a short hosel, so the composited real shaft starts right at the hosel."""
    al=im.split()[-1].load(); w,h=im.size
    widths=[max((b-a+1 for a,b in runs(al,y,w)),default=0) for y in range(h)]
    hw=max(widths) if widths else w
    yb=0
    for y in range(h):
        if widths[y] > frac*hw: yb=y      # last row still 'head/hosel wide'
    cut=min(h, yb+int(hw*keep))
    return trim(im.crop((0,0,w,cut)))

def straighten(im,edge):
    a=axis_at(im,edge)
    if not a: return im
    _,_,ux,uy,_=a
    if abs(ux)<=0.02: return im   # already near-vertical (force wedges etc. straight)
    # brute-force the rotation that makes the shaft most vertical (robust to sign)
    best=(abs(ux), 0, im)
    for deg in range(-90,91,4):
        cand=trim(im.rotate(deg, expand=True, resample=Image.BICUBIC))
        aa=axis_at(cand,edge)
        if not aa: continue
        score=abs(aa[2])
        # require outward pointing the right way (up for top, down for bottom)
        good = (aa[3]<0) if edge=='top' else (aa[3]>0)
        if good and score<best[0]:
            best=(score,deg,cand)
    return best[2]

def build(key,cfg):
    im=trim(Image.open(f'{SRC}/{key}.png').convert('RGBA'))
    if cfg.get('rotate'): im=trim(im.rotate(cfg['rotate'],expand=True,resample=Image.BICUBIC))
    if cfg.get('auto_straighten',True): im=straighten(im,cfg['edge'])
    w,h=im.size; px=im.load()
    a=axis_at(im,cfg['edge'])
    if not a:
        im.save(f'{OUT}/{key}.png'); return f'{key}: no shaft'
    c0,yb,ux,uy,sw=a
    sw_det=sw
    al=im.split()[-1].load()
    ys=yb+(-1 if cfg['edge']=='bottom' else 1)*int(h*0.06); ys=max(0,min(h-1,ys))
    rr=shaft_run(al,ys,w) or (int(c0-sw/2),int(c0+sw/2))
    cols=[px[x,ys][:3] for x in range(rr[0],rr[1]+1) if px[x,ys][3]>60] or [(120,124,132)]
    base=tuple(int(statistics.median(c[i] for c in cols)) for i in range(3))
    def shade(f):
        edge=1-1.5*abs(f); hi=math.exp(-((f+0.14)**2)/(2*0.05))
        k=0.5+0.55*max(0.0,edge)+0.65*hi
        return tuple(max(0,min(255,int(base[i]*k))) for i in range(3))
    prof=[shade((j/8)-0.5) for j in range(9)]
    # head width = widest opaque run (drives absolute shaft/grip sizing)
    head_w=0
    for yy in range(0,h,4):
        for r in runs(al,yy,w):
            head_w=max(head_w,r[1]-r[0]+1)
    head_w=max(head_w,60)
    # find the hosel (top of the baked shaft stub) and crop that stub off the head
    # so the real shaft starts right at the hosel (shorter shaft, more grip in frame)
    hosel_y=yb
    if cfg.get('edge')=='bottom' and cfg.get('trim_stub',True):
        thr=max(2.0*sw_det, 0.13*head_w)
        for y in range(h-1,-1,-1):
            wd=max((b-a2+1 for a2,b in runs(al,y,w)),default=0)
            if wd>thr: hosel_y=y; break
    hy=min(h, hosel_y+int(head_w*0.05))
    head_img=im.crop((0,0,w,hy))
    # measure the hosel width at the hosel transition, so the shaft matches it
    hr=shaft_run(al, min(h-1,hosel_y), w)
    if hr: hosel_w=hr[1]-hr[0]+1; c0=(hr[0]+hr[1])/2.0
    else:  hosel_w=sw
    shaft_scale=cfg.get('shaft_scale',1.0); grip_scale=cfg.get('grip_scale',1.0)
    sw=max(sw, int(head_w*0.064))            # shaft render width floor (match hosel/woods)
    grip_w0=head_w*0.10*grip_scale; grip_w1=head_w*0.150*grip_scale # grips
    ext_len=head_w*cfg.get('ext_mul',2.7); grip_len=head_w*0.95
    ex=c0+ux*(ext_len+grip_len); ey=yb+uy*(ext_len+grip_len)
    pad=int(sw*2+24)
    minx=min(0,ex)-pad;maxx=max(w,ex)+pad;miny=min(0,ey)-pad;maxy=max(h,ey)+pad
    W=int(maxx-minx);H=int(maxy-miny);ox=-int(minx);oy=-int(miny)
    canvas=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(canvas)
    sx=c0+ox; sy=hosel_y+oy; pxv,pyv=-uy,ux; half=sw*shaft_scale/2
    # real shaft photo (graphite / chrome steel, with its own markings), else synthetic
    shaft_src=SHAFT_MAP.get(key)
    if shaft_src is not None:
        shw=max(8,int(hosel_w*shaft_scale))   # match the shaft width to the hosel
        sh=shaft_src.resize((shw,int(ext_len)),Image.LANCZOS)
        canvas.alpha_composite(sh,(int(sx-shw/2),int(sy)))
    else:
        for i in range(int(ext_len)+1):
            cxp=sx+ux*i; cyp=sy+uy*i; hw=half*(1-0.05*i/ext_len)
            d.line([cxp-pxv*hw,cyp-pyv*hw,cxp+pxv*hw,cyp+pyv*hw],fill=prof[4]+(255,),width=1)
            for j in range(len(prof)):
                frac=(j/(len(prof)-1))-0.5
                d.point((cxp+pxv*frac*2*hw,cyp+pyv*frac*2*hw),fill=prof[j]+(255,))
    gx0=sx+ux*ext_len; gy0=sy+uy*ext_len; gw0=grip_w0; gw1=grip_w1
    grip_src=GRIP_MAP.get(key)
    if grip_src is not None:
        # real grip photo (logo visible), condensed to fit
        canvas=canvas.filter(ImageFilter.GaussianBlur(0.4))   # soften drawn shaft only
        gw=max(8,int(grip_w1*1.4))
        gh=min(int(grip_src.height*gw/grip_src.width), int(head_w*cfg.get('grip_cap',1.15)))  # keep grip shorter than shaft
        gimg=grip_src.resize((gw,gh),Image.LANCZOS)
        canvas.alpha_composite(gimg,(int(gx0-gw/2), int(gy0-gh*0.03)))
    else:
        for i in range(int(grip_len)+1):
            f=i/grip_len; cxp=gx0+ux*(grip_len*f); cyp=gy0+uy*(grip_len*f); hw=(gw0+(gw1-gw0)*f)/2
            base_l=int(20+13*f); d.line([cxp-pxv*hw,cyp-pyv*hw,cxp+pxv*hw,cyp+pyv*hw],fill=(base_l,base_l,base_l+3,255),width=2)
        for off,shade2 in ((-0.32,(95,97,105,150)),(0.34,(6,6,9,150))):
            ax=gx0+pxv*gw0*off; ay=gy0+pyv*gw0*off
            bx=gx0+ux*grip_len+pxv*gw1*off; by=gy0+uy*grip_len+pyv*gw1*off
            d.line([ax,ay,bx,by],fill=shade2,width=max(2,int(sw*0.4)))
        gx1=gx0+ux*grip_len; gy1=gy0+uy*grip_len; r=gw1/2
        d.ellipse([gx1-r,gy1-r,gx1+r,gy1+r],fill=(30,30,34,255))
        canvas=canvas.filter(ImageFilter.GaussianBlur(0.4))
    canvas.alpha_composite(head_img,(ox,oy))
    canvas=trim(canvas); canvas.save(f'{OUT}/{key}.png')
    return f'{key}: edge={cfg["edge"]} sw={sw} axis=({ux:.2f},{uy:.2f}) -> {canvas.size}'

for k,c in CFG.items():
    print(build(k,c))
