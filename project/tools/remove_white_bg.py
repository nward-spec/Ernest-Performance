from PIL import Image, ImageFilter
import os, glob, collections

SRC='project/assets/products/stack'
OUT='project/assets/products/cutout'
os.makedirs(OUT, exist_ok=True)

def remove_white_bg(path, thr=38):
    im=Image.open(path).convert('RGB')
    w,h=im.size
    px=im.load()
    # BFS flood fill from border, marking background (near-white & connected to edge)
    bg=bytearray(w*h)  # 0 unknown,1 bg
    from collections import deque
    dq=deque()
    def seed(x,y):
        r,g,b=px[x,y]
        if r>255-thr and g>255-thr and b>255-thr and not bg[y*w+x]:
            bg[y*w+x]=1; dq.append((x,y))
    for x in range(w):
        seed(x,0); seed(x,h-1)
    for y in range(h):
        seed(0,y); seed(w-1,y)
    while dq:
        x,y=dq.popleft()
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx,ny=x+dx,y+dy
            if 0<=nx<w and 0<=ny<h and not bg[ny*w+nx]:
                r,g,b=px[nx,ny]
                if r>255-thr and g>255-thr and b>255-thr:
                    bg[ny*w+nx]=1; dq.append((nx,ny))
    # build alpha
    a=Image.new('L',(w,h),255)
    ap=a.load()
    for y in range(h):
        row=y*w
        for x in range(w):
            if bg[row+x]: ap[x,y]=0
    # feather edges slightly to kill white halo
    a=a.filter(ImageFilter.GaussianBlur(0.6))
    out=im.convert('RGBA'); out.putalpha(a)
    return out

for f in sorted(glob.glob(f'{SRC}/*.jpg')):
    key=os.path.splitext(os.path.basename(f))[0]
    im=remove_white_bg(f)
    # trim to alpha bbox
    bb=im.split()[-1].getbbox()
    if bb: im=im.crop(bb)
    op=os.path.join(OUT,f'{key}.png')
    im.save(op)
    print(key, im.size, os.path.getsize(op)//1024,'KB')
