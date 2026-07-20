import json
U = json.load(open('/tmp/club_uris.json'))

HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Winner's Bag — Ryan Fox — The 154th Open 2026</title>
<style>
  :root{
    --ink:#0e1116; --panel:#161b22; --line:#2a313c;
    --gold:#c9a24b; --gold-2:#e7c877; --text:#f4f1ea; --muted:#9aa4b2;
    --fw:1080px; --fh:1350px;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#000;font-family:"Helvetica Neue",Arial,sans-serif;color:var(--text);-webkit-font-smoothing:antialiased;}
  .frame{
    width:var(--fw);height:var(--fh);position:relative;overflow:hidden;
    background:radial-gradient(120% 85% at 50% -5%,#1e2732 0%,var(--ink) 55%,#05080c 100%);
    margin:0 auto 44px;padding:74px 74px 92px;display:flex;flex-direction:column;
  }
  .frame::after{content:"";position:absolute;inset:26px;border:1px solid rgba(201,162,75,.28);border-radius:6px;pointer-events:none;}
  .brandbar{display:flex;align-items:center;gap:16px;letter-spacing:.2em;font-size:21px;text-transform:uppercase;color:var(--muted);z-index:1;}
  .brandbar .x{color:var(--gold);font-size:24px;}
  .brandbar .sp{margin-left:auto;}
  .kicker{color:var(--gold);letter-spacing:.34em;text-transform:uppercase;font-size:25px;margin-top:14px;font-weight:700;}
  h1{font-size:108px;line-height:.92;font-weight:800;margin:12px 0 10px;letter-spacing:-1px;}
  h2{font-size:56px;line-height:1.02;font-weight:800;margin:2px 0;}
  .event{font-size:27px;color:var(--muted);letter-spacing:.02em;line-height:1.4;}
  .gold{color:var(--gold);}
  img.club{display:block;height:100%;width:auto;max-width:100%;object-fit:contain;
           filter:drop-shadow(0 26px 34px rgba(0,0,0,.6));}

  /* cover: three standing clubs */
  .cover-clubs{flex:1;display:grid;grid-template-columns:repeat(3,1fr);align-items:end;justify-items:center;gap:20px;margin-top:18px;min-height:0;}
  .cc{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:16px;min-height:0;}
  .cc .imgwrap{flex:1;min-height:0;display:flex;align-items:flex-end;}
  .cc .cap{font-size:20px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);}

  /* twin woods */
  .duo{flex:1;display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:6px;min-height:0;}
  .duo .col{display:flex;flex-direction:column;align-items:center;gap:14px;min-height:0;}
  .duo .imgwrap{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;}
  .duo .nm{font-size:31px;font-weight:800;text-align:center;line-height:1.05;}
  .duo .sub{font-size:22px;color:var(--gold);text-align:center;margin-top:-4px;}

  /* single hero (irons) */
  .hero{flex:1;display:grid;grid-template-columns:44% 56%;gap:30px;align-items:center;min-height:0;margin-top:6px;}
  .hero .art{height:100%;display:flex;align-items:center;justify-content:center;min-height:0;}
  .specs{display:flex;flex-direction:column;justify-content:center;gap:20px;}
  .spec{border-top:1px solid var(--line);padding-top:13px;}
  .spec .label{color:var(--muted);letter-spacing:.18em;text-transform:uppercase;font-size:19px;}
  .spec .value{font-size:36px;font-weight:700;margin-top:4px;line-height:1.08;}
  .spec .value small{font-size:23px;color:var(--muted);font-weight:600;}

  /* wedges + putter */
  .f4{flex:1;display:flex;flex-direction:column;gap:20px;margin-top:12px;min-height:0;}
  .wedges{flex:1.5;display:grid;grid-template-columns:repeat(3,1fr);gap:14px;min-height:0;justify-items:center;}
  .wcell{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:8px;min-height:0;}
  .wcell .imgwrap{flex:1;min-height:0;display:flex;align-items:flex-end;}
  .wcell .nm{font-size:22px;font-weight:700;text-align:center;}
  .wcell .sub{font-size:22px;color:var(--gold);font-weight:800;}
  .putter-row{flex:1;display:grid;grid-template-columns:26% 74%;gap:24px;align-items:center;
              background:rgba(21,27,35,.6);border:1px solid var(--line);border-radius:16px;padding:16px 30px;min-height:0;}
  .putter-row .imgwrap{height:100%;display:flex;align-items:center;justify-content:center;min-height:0;}
  .putter-row .nm{font-size:42px;font-weight:800;}
  .putter-row .sub{font-size:23px;color:var(--muted);margin-top:8px;line-height:1.4;}

  /* ball centered, text underneath */
  .ballwrap{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;min-height:0;margin-top:6px;}
  .ballwrap .art{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;}
  .ballwrap .art img{height:100%;width:auto;max-width:80%;object-fit:contain;filter:drop-shadow(0 24px 34px rgba(0,0,0,.6));}
  .balltext{text-align:center;}
  .balltext h2{font-size:52px;}
  .balltext .sub{font-size:26px;color:var(--gold);margin-top:6px;letter-spacing:.02em;}
  .stat-row{display:flex;gap:24px;margin-top:8px;}
  .stat{flex:1;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px;text-align:center;}
  .stat .n{font-size:50px;font-weight:800;color:var(--gold);line-height:1;}
  .stat .l{font-size:18px;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;margin-top:9px;}

  .footer{margin-top:auto;padding-top:20px;display:flex;justify-content:space-between;align-items:center;color:var(--muted);font-size:21px;letter-spacing:.06em;z-index:1;}
  .swipe{color:var(--gold);font-weight:700;}
  .cta{margin:auto 0;text-align:center;}
  .cta h2{font-size:78px;margin-bottom:20px;}
  .cta p{font-size:29px;color:var(--muted);line-height:1.55;}
</style>
</head>
<body>

<!-- FRAME 1 — COVER -->
<section class="frame" id="f1">
  <div class="brandbar"><span>Ernest Performance</span><span class="x">&times;</span><span>Dialled In Pod</span></div>
  <div class="kicker">Winner's Bag</div>
  <h1>Ryan<br>Fox</h1>
  <div class="event">The 154th Open &middot; Royal Birkdale &middot; <span class="gold">270 (&minus;10)</span> &middot; maiden major</div>
  <div class="cover-clubs">
    <div class="cc"><div class="imgwrap"><img class="club" src="__driver__" alt="Srixon ZXi LS driver"></div><span class="cap">Driver</span></div>
    <div class="cc"><div class="imgwrap"><img class="club" src="__wedge__" alt="Cleveland RTZ wedge"></div><span class="cap">Wedges</span></div>
    <div class="cc"><div class="imgwrap"><img class="club" src="__putter__" alt="Ping Anser 2D putter"></div><span class="cap">Putter</span></div>
  </div>
  <div class="footer"><span>What's In The Bag</span><span class="swipe">Swipe &rarr;</span></div>
</section>

<!-- FRAME 2 — OFF THE TEE -->
<section class="frame" id="f2">
  <div class="brandbar"><span>Ernest &times; Dialled In Pod</span><span class="sp">Winner's Bag</span></div>
  <div class="kicker">Off The Tee</div>
  <div class="duo">
    <div class="col"><div class="imgwrap"><img class="club" src="__driver__" alt="Srixon ZXi LS driver"></div>
      <div class="nm">Srixon ZXi LS</div><div class="sub">Driver &middot; 10.5&deg;</div></div>
    <div class="col"><div class="imgwrap"><img class="club" src="__fairway__" alt="Srixon ZXi fairway wood"></div>
      <div class="nm">Srixon ZXi</div><div class="sub">3-Wood &middot; 15&deg;</div></div>
  </div>
  <div class="spec" style="margin-top:16px"><div class="label">Shafts &amp; Grip</div><div class="value" style="font-size:27px">Fujikura Ventus Black 7 TX / Ventus Black &middot; Golf Pride Z-Grip Cord</div></div>
  <div class="footer"><span>1 / 6</span><span class="swipe">Swipe &rarr;</span></div>
</section>

<!-- FRAME 3 — THE IRONS -->
<section class="frame" id="f3">
  <div class="brandbar"><span>Ernest &times; Dialled In Pod</span><span class="sp">Winner's Bag</span></div>
  <div class="kicker">The Irons</div>
  <div class="hero">
    <div class="art"><img class="club" src="__irons__" alt="Srixon ZXi7 iron"></div>
    <div class="specs">
      <h2>Srixon<br>ZXi7 &amp; ZXi5</h2>
      <div class="spec"><div class="label">Driving iron</div><div class="value">Srixon ZXi5+ 3-iron <small>&middot; 20&deg;</small></div></div>
      <div class="spec"><div class="label">Set</div><div class="value">ZXi5 (4&ndash;5) &middot; ZXi7 (6&ndash;PW)</div></div>
      <div class="spec"><div class="label">Shaft &amp; Grip</div><div class="value" style="font-size:28px">True Temper Dynamic Gold Tour Issue X100 &middot; Golf Pride Z-Grip Cord</div></div>
    </div>
  </div>
  <div class="footer"><span>2 / 6</span><span class="swipe">Swipe &rarr;</span></div>
</section>

<!-- FRAME 4 — WEDGES & PUTTER -->
<section class="frame" id="f4">
  <div class="brandbar"><span>Ernest &times; Dialled In Pod</span><span class="sp">Winner's Bag</span></div>
  <div class="kicker">Wedges &amp; Putter</div>
  <div class="f4">
    <div class="wedges">
      <div class="wcell"><div class="imgwrap"><img class="club" src="__wedge__" alt="Cleveland RTZ 50"></div><div class="nm">Cleveland RTZ</div><div class="sub">50&deg;</div></div>
      <div class="wcell"><div class="imgwrap"><img class="club" src="__wedge__" alt="Cleveland RTZ 56"></div><div class="nm">Cleveland RTZ</div><div class="sub">56&deg;</div></div>
      <div class="wcell"><div class="imgwrap"><img class="club" src="__wedge__" alt="Cleveland RTZ 60"></div><div class="nm">Cleveland RTZ</div><div class="sub">60&deg;</div></div>
    </div>
    <div class="putter-row">
      <div class="imgwrap"><img class="club" src="__putter__" alt="Ping Anser 2D putter" style="height:100%"></div>
      <div class="txt"><div class="nm">Ping Anser 2D</div><div class="sub">SuperStroke Zenergy grip &middot; the blade that holed the winning putt on 18</div></div>
    </div>
  </div>
  <div class="footer"><span>3 / 6</span><span class="swipe">Swipe &rarr;</span></div>
</section>

<!-- FRAME 5 — BALL & NUMBERS -->
<section class="frame" id="f5">
  <div class="brandbar"><span>Ernest &times; Dialled In Pod</span><span class="sp">Winner's Bag</span></div>
  <div class="kicker">The Ball &amp; The Numbers</div>
  <div class="ballwrap">
    <div class="art"><img src="__ball__" alt="Srixon Z-Star XV golf ball"></div>
    <div class="balltext">
      <h2>Srixon Z-Star XV</h2>
      <div class="sub">Pure White &middot; Srixon &middot; Cleveland &middot; Ping &mdash; tee to green</div>
    </div>
  </div>
  <div class="stat-row">
    <div class="stat"><div class="n">62</div><div class="l">Saturday Round</div></div>
    <div class="stat"><div class="n">&minus;10</div><div class="l">Winning Total</div></div>
    <div class="stat"><div class="n">1st</div><div class="l">Major Title</div></div>
  </div>
  <div class="footer"><span>4 / 6</span><span class="swipe">Swipe &rarr;</span></div>
</section>

<!-- FRAME 6 — OUTRO -->
<section class="frame" id="f6">
  <div class="brandbar"><span>Ernest Performance</span><span class="x">&times;</span><span>Dialled In Pod</span></div>
  <div class="cta">
    <div class="kicker">Winner's Bag</div>
    <h2>Dialled In?</h2>
    <p>The full breakdown &amp; this week's talking points<br>are on the Dialled In Pod.<br><br><span class="gold">Follow @ernestperformance</span> for next week's Winner's Bag.</p>
  </div>
  <div class="footer"><span>5 / 6</span><span>@dialledinpod</span></div>
</section>

</body>
</html>
'''
for k,v in U.items():
    HTML = HTML.replace(f'__{k}__', v)
open('project/builds/2026-07-19-the-open-fox.html','w').write(HTML)
print('wrote build', len(HTML), 'chars')
