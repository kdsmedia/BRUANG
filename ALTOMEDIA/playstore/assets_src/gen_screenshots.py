#!/usr/bin/env python3
"""Generate Play Store screenshot mockups (1080x1920) for BERUANG.

Renders phone-frame mockups of key app screens using the app's amber/brown bear
theme. Output PNGs are ready for Play Console store listing screenshots.
"""
import os

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    os.system("pip install Pillow -q")
    from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "..", "screenshots")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920
AMBER = (234, 179, 8)
AMBER_DK = (180, 83, 9)
AMBER_LT = (253, 230, 138)
BG_DARK = (30, 41, 59)
BG = (248, 250, 252)
INK = (30, 41, 59)
MUT = (148, 163, 184)
WHITE = (255, 255, 255)
RED = (239, 68, 68)
PURPLE = (109, 40, 217)
LINE = (226, 232, 240)

def font(sz, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()

def rrect(d, box, r, fill=None, outline=None, w=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=w)

def text(d, xy, s, f, fill=INK, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def phone_frame(img):
    """Draw dark phone bezel inset."""
    d = ImageDraw.Draw(img)
    m = 40
    rrect(d, [m, m, W-m, H-m], 60, fill=BG_DARK)
    rrect(d, [m+12, m+12, W-m-12, H-m-12], 48, fill=BG)
    return m+12

def header(d, x0, y0, x1, title, red_dot=False):
    rrect(d, [x0, y0, x1, y0+110], 0, fill=AMBER)
    text(d, (x0+40, y0+55), "BERUANG", font(44, True), fill=WHITE, anchor="lm")
    if red_dot:
        d.ellipse([x1-90, y0+35, x1-50, y0+75], fill=RED)
    return y0+110

def stories(d, x0, y0):
    colors = [AMBER_DK, PURPLE, AMBER, MUT]
    cx = x0+50
    for i, c in enumerate(colors):
        d.ellipse([cx, y0, cx+90, y0+90], fill=c, outline=WHITE, width=4)
        cx += 110
    # add-story dashed
    d.ellipse([cx, y0, cx+90, y0+90], outline=MUT, width=3)
    return y0+120

def post_card(d, x0, y0, x1, accent=AMBER_LT, like=True, comment=True):
    rrect(d, [x0, y0, x1, y0+560], 24, fill=WHITE, outline=LINE, w=2)
    d.ellipse([x0+24, y0+24, x0+90, y0+90], fill=AMBER_DK)
    text(d, (x0+110, y0+40), "Altomedia", font(30, True))
    text(d, (x0+110, y0+74), "2 jam lalu", font(22), fill=MUT)
    rrect(d, [x0+24, y0+110, x1-24, y0+330], 12, fill=accent)
    if like:
        d.ellipse([x0+30, y0+350, x0+66, y0+386], fill=RED)
    text(d, (x0+84, y0+358), "128 suka", font(24, True))
    if comment:
        d.ellipse([x0+200, y0+350, x0+236, y0+386], fill=MUT)
    text(d, (x0+254, y0+358), "24 komentar", font(24))
    text(d, (x0+24, y0+430), "Selamat datang di BERUANG!", font(28, True))
    text(d, (x0+24, y0+470), "Bagikan momenmu dan dapatkan poin.", font(24), fill=MUT)
    text(d, (x0+24, y0+504), "+20 poin dari posting ini", font(22), fill=AMBER_DK)
    return y0+560+24

def dock(d, x0, y1):
    x0s = x0
    x1s = W-x0
    rrect(d, [x0s, y1-130, x1s, y1-20], 30, fill=AMBER)
    for i, lbl in enumerate(["Beranda", "Cari", "Posting", "Chat", "Profil"]):
        cxp = x0s + 90 + i*((x1s-x0s-180)//4)
        text(d, (cxp, y1-75), lbl, font(24, i==0), fill=WHITE, anchor="lm")

def save(img, name):
    p = os.path.join(OUT, name)
    img.save(p, "PNG")
    print("wrote", p, os.path.getsize(p), "bytes")

# ---- Screenshot 1: Feed ----
def screen_feed():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    x0 = phone_frame(img)
    x1 = W-x0
    y = x0
    y = header(d, x0, y, x1, "BERUANG", red_dot=True)
    y = stories(d, x0, y+16)
    y = post_card(d, x0+16, y, x1-16, accent=AMBER_LT)
    y = post_card(d, x0+16, y, x1-16, accent=(196, 181, 253))
    dock(d, x0, H-x0)
    save(img, "screenshot_01_feed.png")

# ---- Screenshot 2: Wallet & transfer ----
def screen_wallet():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    x0 = phone_frame(img)
    x1 = W-x0
    y = x0
    y = header(d, x0, y, x1, "Dompet")
    # balance card
    rrect(d, [x0+24, y+24, x1-24, y+300], 28, fill=AMBER_DK)
    text(d, (x0+56, y+70), "Saldo Poin", font(28), fill=AMBER_LT)
    text(d, (x0+56, y+150), "12.450", font(84, True), fill=WHITE, anchor="lm")
    text(d, (x0+56, y+250), "Tier: Silver", font(28, True), fill=AMBER_LT)
    # buttons
    by = y+340
    for i, lbl in enumerate(["Kirim", "Terima", "Riwayat"]):
        bx = x0+24 + i*((x1-x0-48)//3) + i*16
        bw = (x1-x0-48-32)//3
        rrect(d, [bx, by, bx+bw, by+90], 20, fill=AMBER)
        text(d, (bx+bw/2, by+45), lbl, font(26, True), fill=WHITE, anchor="mm")
    # qr card
    qy = by+130
    rrect(d, [x0+24, qy, x1-24, qy+620], 24, fill=WHITE, outline=LINE, w=2)
    text(d, (x0+56, qy+40), "Kode QR Akun Saya", font(30, True))
    qx, qy2, qs = x0+ (W-2*x0-360)//2, qy+110, 360
    d.rectangle([qx, qy2, qx+qs, qy2+qs], fill=WHITE, outline=INK, width=4)
    # fake qr modules
    import random
    random.seed(7)
    step = 20
    for r in range(qs//step):
        for c in range(qs//step):
            if random.random() > 0.5:
                d.rectangle([qx+c*step, qy2+r*step, qx+(c+1)*step, qy2+(r+1)*step], fill=INK)
    # corners
    for (cx, cy) in [(qx, qy2), (qx+qs-60, qy2), (qx, qy2+qs-60)]:
        d.rectangle([cx, cy, cx+60, cy+60], outline=AMBER_DK, width=8)
    text(d, (x0+(W-2*x0)//2, qy2+qs+40), "ID: 842913", font(32, True), fill=AMBER_DK, anchor="ma")
    dock(d, x0, H-x0)
    save(img, "screenshot_02_wallet.png")

# ---- Screenshot 3: Chat ----
def screen_chat():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    x0 = phone_frame(img)
    x1 = W-x0
    y = x0
    y = header(d, x0, y, x1, "Pesan")
    chats = [("Tim Beruang", "Oke, transfer poinnya sudah..", "5m", AMBER_DK, 3),
             ("Sari", "Lihat postingan baruku!", "12m", PURPLE, 1),
             ("Komunitas Game", "Event malam ini jam 8", "1j", AMBER, 0),
             ("Budi", "Mau tukar poin?", "2j", MUT, 0),
             ("Andi", "Terima kasih bro 🐻", "3j", AMBER_DK, 0)]
    cy = y+24
    for name, msg, t, col, badge in chats:
        rrect(d, [x0+16, cy, x1-16, cy+150], 20, fill=WHITE, outline=LINE, w=1)
        d.ellipse([x0+40, cy+30, x0+120, cy+110], fill=col)
        text(d, (x0+150, cy+45), name, font(30, True))
        text(d, (x0+150, cy+88), msg, font(24), fill=MUT)
        text(d, (x1-50, cy+45), t, font(22), fill=MUT, anchor="ra")
        if badge:
            d.ellipse([x1-95, cy+80, x1-55, cy+120], fill=RED)
            text(d, (x1-75, cy+100), str(badge), font(20, True), fill=WHITE, anchor="mm")
        cy += 170
    dock(d, x0, H-x0)
    save(img, "screenshot_03_chat.png")

# ---- Screenshot 4: Profile & tiers ----
def screen_profile():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    x0 = phone_frame(img)
    x1 = W-x0
    y = x0
    y = header(d, x0, y, x1, "Profil")
    # avatar + name
    d.ellipse([x0+ (W-2*x0-160)//2, y+30, x0+ (W-2*x0+160)//2, y+190], fill=AMBER_DK)
    text(d, (W/2, y+230), "ALTOMEDIA", font(40, True), anchor="ma")
    text(d, (W/2, y+285), "@altomedia · ID 842913", font(26), fill=MUT, anchor="ma")
    # stats
    sy = y+340
    stats = [("Posting", "84"), ("Pengikut", "1.2K"), ("Mengikuti", "320")]
    sw = (W-2*x0-48)//3
    for i, (l, v) in enumerate(stats):
        sx = x0+24 + i*(sw+24)
        rrect(d, [sx, sy, sx+sw, sy+130], 20, fill=WHITE, outline=LINE, w=1)
        text(d, (sx+sw/2, sy+45), v, font(36, True), anchor="ma")
        text(d, (sx+sw/2, sy+95), l, font(22), fill=MUT, anchor="ma")
    # tier progress
    ty = sy+170
    rrect(d, [x0+24, ty, x1-24, ty+300], 24, fill=WHITE, outline=LINE, w=1)
    text(d, (x0+56, ty+40), "Tier Silver", font(32, True), fill=MUT)
    text(d, (x0+56, ty+90), "12.450 / 20.000 poin", font(28, True))
    rrect(d, [x0+56, ty+150, x1-56, ty+200], 25, fill=LINE)
    rrect(d, [x0+56, ty+150, x0+56+ int((x1-x0-112)*0.62), ty+200], 25, fill=AMBER)
    text(d, (x0+56, ty+240), "Berikutnya: Gold pada 20.000 poin", font(24), fill=MUT)
    dock(d, x0, H-x0)
    save(img, "screenshot_04_profile.png")

# ---- Screenshot 5: Stories ----
def screen_stories():
    img = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(img)
    x0 = phone_frame(img)
    x1 = W-x0
    # full-bleed story
    d.rectangle([x0, x0, x1, H-x0], fill=AMBER_LT)
    # progress bars
    bars_y = x0+20
    for i in range(4):
        rrect(d, [x0+20+i*((x1-x0-80)//4)+i*16, bars_y, x0+20+(i+1)*((x1-x0-80)//4)+i*16, bars_y+8], 4,
              fill=WHITE if i<2 else (255,255,255,80) if False else (255,255,255))
    # big bear
    cx, cy = W/2, H/2-60
    d.ellipse([cx-160, cy-200, cx-80, cy-120], fill=AMBER_DK)
    d.ellipse([cx+80, cy-200, cx+160, cy-120], fill=AMBER_DK)
    d.ellipse([cx, cy-180, cx+80, cy-100], fill=AMBER_DK)
    d.ellipse([cx-130, cy-100, cx+130, cy+160], fill=AMBER_DK)
    d.ellipse([cx-70, cy+20, cx+70, cy+150], fill=(245,230,200))
    d.ellipse([cx-50, cy-30, cx-10, cy+10], fill=INK)
    d.ellipse([cx+10, cy-30, cx+50, cy+10], fill=INK)
    d.ellipse([cx-20, cy+50, cx+20, cy+90], fill=INK)
    text(d, (cx, cy+260), "Cerita Altomedia", font(36, True), fill=INK, anchor="ma")
    # reply bar
    ry = H-x0-160
    rrect(d, [x0+30, ry, x1-160, ry+80], 40, fill=WHITE)
    rrect(d, [x1-140, ry, x1-30, ry+80], 40, fill=AMBER)
    text(d, (x1-85, ry+40), "→", font(40, True), fill=WHITE, anchor="mm")
    save(img, "screenshot_05_stories.png")

screen_feed()
screen_wallet()
screen_chat()
screen_profile()
screen_stories()
print("All screenshots generated.")
