import pygame
import sys
import random
import math

# --- BAŞLATMA VE AYARLAR ---
pygame.init()
pygame.font.init()

GENISLIK, YUKSEKLIK = 550, 800
ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
pygame.display.set_caption("BLOCK BLAST")
saat = pygame.time.Clock()
FPS = 60  # Yüksek FPS, akıcı deneyim

# --- BLOCK BLAST TEMA SİSTEMİ ---
TEMALAR = [
    {
        "isim": "Mavis",
        "bg": (20, 24, 82),      
        "panel": (26, 35, 126),      
        "header": (30, 50, 150),   
        "yazi": (255, 255, 255),    
        "bos": (45, 60, 140),        
        "cizgi": (100, 130, 200),
        "accent": (100, 200, 255)
    },
    {
        "isim": " Cok Tatlis Pembis",
        "bg": (240, 169, 195),      
        "panel": (139, 68, 89),     
        "header": (240, 169, 195),  
        "yazi": (255, 255, 255),    
        "bos": (190, 100, 135),     
        "cizgi": (120, 50, 80),     
        "accent": (255, 105, 180)   
    },
    {
        "isim": "Tatlıs Yesil",
        "bg": (15, 80, 40),
        "panel": (20, 110, 50),
        "header": (30, 150, 70),
        "yazi": (255, 255, 255),
        "bos": (25, 100, 45),
        "cizgi": (80, 200, 120),
        "accent": (100, 255, 150)
    }
]

aktif_tema_idx = 1 # Başlangıçta Pembe (ecurin) tema aktif olsun
tema = TEMALAR[aktif_tema_idx]

# --- BLOK RENK PALETİ ---
BLOK_RENKLERI = [
    ((255, 107, 107), (220, 76, 76)),    
    ((255, 193, 7), (230, 170, 0)),      
    ((76, 175, 80), (56, 142, 60)),      
    ((33, 150, 243), (21, 101, 192)),    
    ((156, 39, 176), (123, 31, 162)),    
    ((255, 152, 0), (230, 124, 0)),      
    ((0, 188, 212), (0, 150, 180)),      
    ((233, 30, 99), (194, 24, 91))       
]

BLOK_RENKLERI_PEMBE = [
    ((255, 105, 180), (200, 70, 140)),    
    ((255, 130, 180), (210, 85, 150)),    
    ((255, 110, 170), (205, 75, 135)),    
    ((255, 150, 190), (215, 110, 160)),   
    ((255, 120, 175), (208, 80, 145)),    
    ((255, 140, 185), (212, 100, 155)),   
    ((255, 100, 165), (200, 65, 130)),    
    ((255, 160, 195), (220, 120, 170))    
]

# --- FONTLAR ---
FONT_SKOR_BASLIK = pygame.font.SysFont("Arial", 20, bold=True)
FONT_SKOR_RAKAM = pygame.font.SysFont("Arial", 48, bold=True)
FONT_ANIMASYON = pygame.font.SysFont("Arial", 40, bold=True)
FONT_GAMEOVER = pygame.font.SysFont("Arial", 55, bold=True)
FONT_KUCUK = pygame.font.SysFont("Arial", 16, bold=True)
FONT_ECURIN = pygame.font.SysFont("Verdana", 24, bold=True, italic=True) # Ecurin için özel font
FONT_COMBO = pygame.font.SysFont("Arial", 32, bold=True)

# --- OYUN DEĞİŞKENLERİ ---
IZGARA_BOYUTU = 6
HÜCRE_BOYUTU = 60
PANEL_GENISLIK = IZGARA_BOYUTU * HÜCRE_BOYUTU
BASLANGIC_X = (GENISLIK - PANEL_GENISLIK) // 2
BASLANGIC_Y = 140

tahta = [[0 for _ in range(IZGARA_BOYUTU)] for _ in range(IZGARA_BOYUTU)]
skor = 0
best_skor = 0
animasyonlar = [] 
oyun_bitti = False
ayarlar_acik = False
combo = 0
combo_timer = 0
sallanma_miktari = 0 # Ekran sallanma efekti için (YENİLİK)

# Cache sistem
yazı_cache = {}
last_skor = -1
last_best_skor = -1
skor_yazi_cache = None
best_skor_yazi_cache = None

def get_cached_font_render(text, font, color, cache_key):
    if cache_key not in yazı_cache:
        yazı_cache[cache_key] = font.render(text, True, color).convert_alpha()
    return yazı_cache[cache_key]

# --- PARÇACIK SİSTEMİ ---
class Parcacik:
    def __init__(self, x, y, vx, vy, renk, size=5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.renk = renk
        self.size = size
        self.alpha = 255
        self.gravity = 0.3

    def guncelle(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.alpha -= 10  # Daha uzun süre ekranda kalsın
        if self.alpha < 0:
            self.alpha = 0

    def ciz(self, pencere, ofset_x=0, ofset_y=0):
        if self.alpha > 0:
            surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA).convert_alpha()
            pygame.draw.circle(surface, (*self.renk, self.alpha), (self.size, self.size), self.size)
            pencere.blit(surface, (int(self.x - self.size + ofset_x), int(self.y - self.size + ofset_y)))

# --- GELIŞMIŞ ANIMASYON SİSTEMİ ---
class YuzenYazi:
    def __init__(self, metin, x, y, renk, hiz=2):
        self.metin = metin
        self.x = x
        self.y = y
        self.renk = renk
        self.alpha = 255  
        self.hiz_y = hiz
        self.yazi_surface = FONT_ANIMASYON.render(self.metin, True, self.renk).convert_alpha()
        self.halo_surface = FONT_ANIMASYON.render(self.metin, True, (255, 255, 255)).convert_alpha()
        self.w = self.yazi_surface.get_width()

    def guncelle(self):
        self.y -= self.hiz_y  
        self.alpha -= 8  
        if self.alpha < 0:
            self.alpha = 0

    def ciz(self, pencere, ofset_x=0, ofset_y=0):
        if self.alpha > 0:
            self.yazi_surface.set_alpha(self.alpha)
            self.halo_surface.set_alpha(int(self.alpha * 0.3))
            pencere.blit(self.halo_surface, (self.x - self.w//2 + 1 + ofset_x, self.y + 1 + ofset_y))
            pencere.blit(self.yazi_surface, (self.x - self.w//2 + ofset_x, self.y + ofset_y))

class ComboAnimasyon:
    def __init__(self, combo_count, x, y):
        self.metin = f"{combo_count}x COMBO!"
        self.x = x
        self.y = y
        self.alpha = 255
        self.hiz_y = 1.5
        self.renk = (255, 180, 0)
        self.yazi_surface = FONT_COMBO.render(self.metin, True, self.renk).convert_alpha()
        self.w = self.yazi_surface.get_width()

    def guncelle(self):
        self.y -= self.hiz_y  
        self.alpha -= 6  
        if self.alpha < 0:
            self.alpha = 0

    def ciz(self, pencere, ofset_x=0, ofset_y=0):
        if self.alpha > 0:
            self.yazi_surface.set_alpha(self.alpha)
            pencere.blit(self.yazi_surface, (self.x - self.w//2 + ofset_x, self.y + ofset_y))

def oluştur_parcaciklar(x, y, renk, sayi=3):
    for _ in range(sayi):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6) # Hız artırıldı
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        animasyonlar.append(Parcacik(x, y, vx, vy, renk, size=random.randint(4, 7)))

def draw_block_rect(pencere, color_tuple, rect, border_radius=4, tema_idx=0, alpha=255, ofset_x=0, ofset_y=0):
    main_color, shadow_color = color_tuple
    
    # Hayalet (Ghost) blok çizimi için alpha desteği
    if alpha < 255:
        surface = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA).convert_alpha()
        main_c = (*main_color, alpha)
        shadow_c = (*shadow_color, alpha)
        
        pygame.draw.rect(surface, main_c, (0, 0, rect.w, rect.h), border_radius=border_radius)
        wedge_depth = 5 if tema_idx == 1 else 4
        
        shadow_rect = pygame.Rect(border_radius, rect.h - wedge_depth, rect.w - 2*border_radius, wedge_depth)
        if shadow_rect.w > 0:
            pygame.draw.rect(surface, shadow_c, shadow_rect, border_radius=max(1, border_radius//2))
            
        shadow_rect_v = pygame.Rect(rect.w - wedge_depth, border_radius, wedge_depth, rect.h - 2*border_radius)
        if shadow_rect_v.h > 0:
            pygame.draw.rect(surface, shadow_c, shadow_rect_v, border_radius=max(1, border_radius//2))
            
        if tema_idx == 1:
            pygame.draw.rect(surface, (255, 255, 255, alpha), (0, 0, rect.w, rect.h), 2, border_radius=border_radius)
            
        pencere.blit(surface, (rect.x + ofset_x, rect.y + ofset_y))
    else:
        rect = pygame.Rect(rect.x + ofset_x, rect.y + ofset_y, rect.w, rect.h)
        pygame.draw.rect(pencere, main_color, rect, border_radius=border_radius)
        
        wedge_depth = 5 if tema_idx == 1 else 4
        shadow_rect = pygame.Rect(rect.x + border_radius, rect.y + rect.h - wedge_depth, rect.w - 2*border_radius, wedge_depth)
        if shadow_rect.w > 0:
            pygame.draw.rect(pencere, shadow_color, shadow_rect, border_radius=max(1, border_radius//2))
        
        shadow_rect_v = pygame.Rect(rect.x + rect.w - wedge_depth, rect.y + border_radius, wedge_depth, rect.h - 2*border_radius)
        if shadow_rect_v.h > 0:
            pygame.draw.rect(pencere, shadow_color, shadow_rect_v, border_radius=max(1, border_radius//2))
        
        if tema_idx == 1:
            pygame.draw.rect(pencere, (255, 255, 255), rect, 2, border_radius=border_radius)

# --- BLOK ŞEKİLLERİ ---
BLOK_SHAPES = [
    [[1, 1]], [[1], [1]], [[1, 1, 1]], [[1], [1], [1]], [[1, 1, 1, 1]], [[1], [1], [1], [1]], [[1, 1], [1, 1]], 
    [[1, 0], [1, 0], [1, 1]], [[0, 1], [0, 1], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1, 1], [0, 0, 1]],
    [[1, 0], [1, 1]], [[0, 1], [1, 1]], [[1, 1], [1, 0]], [[1, 1], [0, 1]],
    [[1, 1, 1], [0, 1, 0]], [[0, 1, 0], [1, 1, 1]], [[1, 1, 0], [0, 1, 1]], [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
]

class SecilebilirBlok:
    def __init__(self, slot_index):
        self.slot_index = slot_index
        self.yenile()

    def yenile(self):
        self.sekil = random.choice(BLOK_SHAPES)
        if aktif_tema_idx == 1:
            self.renk_cifti = random.choice(BLOK_RENKLERI_PEMBE)
        else:
            self.renk_cifti = random.choice(BLOK_RENKLERI)
        self.aktif = True
        
        self.slot_merkez_x = 95 + self.slot_index * 160  
        self.slot_merkez_y = 690  
        
        hucre_b = HÜCRE_BOYUTU - 18
        blok_w = len(self.sekil[0]) * hucre_b
        blok_h = len(self.sekil) * hucre_b
        
        self.orijinal_x = self.slot_merkez_x - blok_w // 2
        self.orijinal_y = self.slot_merkez_y - blok_h // 2
        self.x = self.orijinal_x
        self.y = self.orijinal_y
        self.hover = False

    def ciz(self, pencere, surukleniyor=False, hover=False, ofset_x=0, ofset_y=0):
        if not self.aktif: return
        
        cizim_hucre_boyutu = HÜCRE_BOYUTU if surukleniyor else HÜCRE_BOYUTU - 18
        gap = 2
        scale_offset = 0.05 if (hover and not surukleniyor) else 0
        
        for r in range(len(self.sekil)):
            for c in range(len(self.sekil[0])):
                if self.sekil[r][c] == 1:
                    bx = self.x + c * cizim_hucre_boyutu + (cizim_hucre_boyutu * scale_offset / 2)
                    by = self.y + r * cizim_hucre_boyutu + (cizim_hucre_boyutu * scale_offset / 2)
                    size = cizim_hucre_boyutu - gap
                    rect = pygame.Rect(bx, by, int(size * (1 + scale_offset)), int(size * (1 + scale_offset)))
                    draw_block_rect(pencere, self.renk_cifti, rect, border_radius=6, tema_idx=aktif_tema_idx, ofset_x=ofset_x, ofset_y=ofset_y)

    def get_rect(self):
        if not self.aktif: return pygame.Rect(0,0,0,0)
        hucre_b = HÜCRE_BOYUTU - 18
        w = len(self.sekil[0]) * hucre_b
        h = len(self.sekil) * hucre_b
        return pygame.Rect(self.x, self.y, w, h)

def hamle_var_mi():
    for b in alttaki_bloklar:
        if not b.aktif: continue
        b_satir, b_sutun = len(b.sekil), len(b.sekil[0])
        for r in range(IZGARA_BOYUTU - b_satir + 1):
            for c in range(IZGARA_BOYUTU - b_sutun + 1):
                sarsa_bilir = True
                for br in range(b_satir):
                    for bc in range(b_sutun):
                        if b.sekil[br][bc] == 1 and tahta[r + br][c + bc] == 1:
                            sarsa_bilir = False
                            break
                    if not sarsa_bilir: break
                if sarsa_bilir: return True
    return False

def satirlari_sutunlari_temizle():
    global skor, combo, combo_timer, sallanma_miktari
    silinecek_satirlar = [r for r in range(IZGARA_BOYUTU) if all(tahta[r][c] == 1 for c in range(IZGARA_BOYUTU))]
    silinecek_sutunlar = [c for c in range(IZGARA_BOYUTU) if all(tahta[r][c] == 1 for r in range(IZGARA_BOYUTU))]
    patlayan_adet = len(silinecek_satirlar) + len(silinecek_sutunlar)
    
    if patlayan_adet > 0:
        parcacik_renk = (255, 105, 180) if aktif_tema_idx == 1 else (255, 180, 0)
        
        # Ekran sallanma efekti (Juice!)
        sallanma_miktari = patlayan_adet * 4
        
        for r in silinecek_satirlar:
            for c in range(IZGARA_BOYUTU):
                x = BASLANGIC_X + c * HÜCRE_BOYUTU + HÜCRE_BOYUTU // 2
                y = BASLANGIC_Y + r * HÜCRE_BOYUTU + HÜCRE_BOYUTU // 2
                oluştur_parcaciklar(x, y, parcacik_renk, sayi=4)
                tahta[r][c] = 0
        
        for c in silinecek_sutunlar:
            for r in range(IZGARA_BOYUTU):
                if tahta[r][c] == 1: 
                    x = BASLANGIC_X + c * HÜCRE_BOYUTU + HÜCRE_BOYUTU // 2
                    y = BASLANGIC_Y + r * HÜCRE_BOYUTU + HÜCRE_BOYUTU // 2
                    oluştur_parcaciklar(x, y, parcacik_renk, sayi=4)
                tahta[r][c] = 0
        
        combo += 1
        combo_timer = 120
        
        base_puan = patlayan_adet * patlayan_adet * 100
        puan = int(base_puan * (1 + (combo - 1) * 0.5))
        skor += puan
        
        anim_x, anim_y = GENISLIK // 2, YUKSEKLIK // 2 - 50
        metin = "GÜZEL!" if patlayan_adet == 1 else ("HARİKA!" if patlayan_adet == 2 else "MÜKEMMEL!")
        renk = (255, 255, 255) if aktif_tema_idx == 1 else (100, 255, 150)
        
        animasyonlar.append(YuzenYazi(metin, anim_x, anim_y, renk))
        if combo > 1:
            animasyonlar.append(ComboAnimasyon(combo, anim_x, anim_y + 60))

def oyunu_sifirla():
    global tahta, skor, oyun_bitti, animasyonlar, combo, combo_timer, best_skor, sallanma_miktari
    if skor > best_skor: best_skor = skor
    tahta = [[0 for _ in range(IZGARA_BOYUTU)] for _ in range(IZGARA_BOYUTU)]
    skor = 0
    combo = 0
    combo_timer = 0
    sallanma_miktari = 0
    animasyonlar.clear()
    oyun_bitti = False
    for b in alttaki_bloklar: b.yenile()

alttaki_bloklar = [SecilebilirBlok(0), SecilebilirBlok(1), SecilebilirBlok(2)]
secili_blok = None
surukleniyor = False
ofset_x, ofset_y = 0, 0

ayar_butonu_rect = pygame.Rect(GENISLIK - 60, 25, 40, 40)
menu_w, menu_h = 300, 350
menu_x = (GENISLIK - menu_w) // 2
menu_y = (YUKSEKLIK - menu_h) // 2
kapat_btn_rect = pygame.Rect(menu_x + 80, menu_y + 280, menu_w - 160, 40)

tema_butonlari = []
for i, t in enumerate(TEMALAR):
    btn_rect = pygame.Rect(menu_x + 30, menu_y + 80 + (i * 60), menu_w - 60, 45)
    tema_butonlari.append({"rect": btn_rect, "idx": i})

karartma_surface = pygame.Surface((GENISLIK, YUKSEKLIK)).convert_alpha()
karartma_surface.fill((0, 0, 0))

# --- ANA OYUN DÖNGÜSÜ ---
while True:
    tema = TEMALAR[aktif_tema_idx] 
    ekran.fill(tema["bg"])
    fare_x, fare_y = pygame.mouse.get_pos()
    
    # Ekran Sallanma Titremesi (Screen Shake)
    shake_x, shake_y = 0, 0
    if sallanma_miktari > 0:
        shake_x = random.randint(-sallanma_miktari, sallanma_miktari)
        shake_y = random.randint(-sallanma_miktari, sallanma_miktari)
        sallanma_miktari -= 1
    
    if combo_timer > 0:
        combo_timer -= 1
    else:
        combo = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and oyun_bitti:
                oyunu_sifirla()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if ayarlar_acik:
                for btn in tema_butonlari:
                    if btn["rect"].collidepoint(fare_x, fare_y):
                        aktif_tema_idx = btn["idx"]
                        # Tema değişince blokların renklerini de güncelle
                        for b in alttaki_bloklar:
                            b.yenile()
                if kapat_btn_rect.collidepoint(fare_x, fare_y):
                    ayarlar_acik = False
            elif not oyun_bitti:
                if ayar_butonu_rect.collidepoint(fare_x, fare_y):
                    ayarlar_acik = True
                else:
                    for b in alttaki_bloklar:
                        if b.get_rect().collidepoint(fare_x, fare_y):
                            secili_blok = b
                            surukleniyor = True
                            ofset_x = b.get_rect().width // 2
                            ofset_y = b.get_rect().height // 2
                            b.x = fare_x - ofset_x
                            b.y = fare_y - ofset_y
                            break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not oyun_bitti and not ayarlar_acik:
            if surukleniyor and secili_blok:
                surukleniyor = False
                izgara_sutun = round((secili_blok.x - BASLANGIC_X) / HÜCRE_BOYUTU)
                izgara_satir = round((secili_blok.y - BASLANGIC_Y) / HÜCRE_BOYUTU)

                yerlesebilir = True
                if 0 <= izgara_satir <= IZGARA_BOYUTU - len(secili_blok.sekil) and 0 <= izgara_sutun <= IZGARA_BOYUTU - len(secili_blok.sekil[0]):
                    for r in range(len(secili_blok.sekil)):
                        for c in range(len(secili_blok.sekil[0])):
                            if secili_blok.sekil[r][c] == 1 and tahta[izgara_satir + r][izgara_sutun + c] == 1:
                                yerlesebilir = False
                else: yerlesebilir = False

                if yerlesebilir:
                    for r in range(len(secili_blok.sekil)):
                        for c in range(len(secili_blok.sekil[0])):
                            if secili_blok.sekil[r][c] == 1:
                                x = BASLANGIC_X + (izgara_sutun + c) * HÜCRE_BOYUTU + HÜCRE_BOYUTU // 2
                                y = BASLANGIC_Y + (izgara_satir + r) * HÜCRE_BOYUTU + HÜCRE_BOYUTU // 2
                                oluştur_parcaciklar(x, y, secili_blok.renk_cifti[0], sayi=2)
                                tahta[izgara_satir + r][izgara_sutun + c] = 1
                    
                    # Yerleştirme esnasında da hafif sarsıntı
                    sallanma_miktari = max(sallanma_miktari, 3)
                    skor += sum(row.count(1) for row in secili_blok.sekil) * 10
                    secili_blok.aktif = False
                    satirlari_sutunlari_temizle()
                    
                    if all(not b.aktif for b in alttaki_bloklar):
                        for b in alttaki_bloklar: b.yenile()
                        
                    if not hamle_var_mi(): oyun_bitti = True
                else:
                    secili_blok.x = secili_blok.orijinal_x
                    secili_blok.y = secili_blok.orijinal_y
                secili_blok = None

    if surukleniyor and secili_blok:
        secili_blok.x = fare_x - ofset_x
        secili_blok.y = fare_y - ofset_y

    hovering_block = None
    for b in alttaki_bloklar:
        if b.aktif and b.get_rect().collidepoint(fare_x, fare_y) and not surukleniyor:
            hovering_block = b
            break

    for anim in animasyonlar[:]:
        anim.guncelle()
        if anim.alpha <= 0:
            animasyonlar.remove(anim)

    # --- ÇİZİM İŞLEMLERİ ---
    header_rect = pygame.Rect(0 + shake_x, 0 + shake_y, GENISLIK, 110)
    pygame.draw.rect(ekran, tema["header"], header_rect)
    
    # "ecurin için" yazısını ekleme
    if aktif_tema_idx == 1:
        ecurin_yazi = get_cached_font_render("~ ecurin için ~", FONT_ECURIN, (255, 220, 240), "ecurin_yazi")
        ekran.blit(ecurin_yazi, (GENISLIK // 2 - ecurin_yazi.get_width() // 2 + shake_x, 70 + shake_y))
    
    skor_baslik_yazi = get_cached_font_render("PUAN", FONT_SKOR_BASLIK, tema["yazi"], f"pb_{aktif_tema_idx}")
    ekran.blit(skor_baslik_yazi, (GENISLIK // 2 - skor_baslik_yazi.get_width() // 2 + shake_x, 10 + shake_y))
    
    if skor != last_skor:
        skor_yazi_cache = FONT_SKOR_RAKAM.render(str(skor), True, tema["accent"]).convert_alpha()
        last_skor = skor
    ekran.blit(skor_yazi_cache, (GENISLIK // 2 - skor_yazi_cache.get_width() // 2 + shake_x, 30 + shake_y))
    
    if best_skor != last_best_skor:
        best_skor_yazi_cache = FONT_KUCUK.render(f"EN İYİ: {best_skor}", True, tema["yazi"]).convert_alpha()
        last_best_skor = best_skor
    ekran.blit(best_skor_yazi_cache, (20 + shake_x, 45 + shake_y))
    
    if combo > 1:
        combo_renk = (255, 255, 255) if aktif_tema_idx == 1 else (255, 200, 0)
        combo_text = FONT_COMBO.render(f"{combo}x COMBO!" if aktif_tema_idx == 1 else f"{combo}x", True, combo_renk).convert_alpha()
        ekran.blit(combo_text, (GENISLIK - 150 + shake_x, 55 + shake_y))
    
    pygame.draw.rect(ekran, tema["header"], (ayar_butonu_rect.x + shake_x, ayar_butonu_rect.y + shake_y, ayar_butonu_rect.width, ayar_butonu_rect.height), border_radius=8)
    for i in range(3):
        pygame.draw.line(ekran, tema["yazi"], (GENISLIK - 50 + shake_x, 35 + i*8 + shake_y), (GENISLIK - 30 + shake_x, 35 + i*8 + shake_y), 3)

    panel_rect = pygame.Rect(BASLANGIC_X - 10 + shake_x, BASLANGIC_Y - 10 + shake_y, PANEL_GENISLIK + 20, PANEL_GENISLIK + 20)
    pygame.draw.rect(ekran, tema["panel"], panel_rect, border_radius=8)

    gap = 2
    aktif_blok_renkleri = BLOK_RENKLERI_PEMBE if aktif_tema_idx == 1 else BLOK_RENKLERI
    
    for satir in range(IZGARA_BOYUTU):
        for sutun in range(IZGARA_BOYUTU):
            x = BASLANGIC_X + sutun * HÜCRE_BOYUTU
            y = BASLANGIC_Y + satir * HÜCRE_BOYUTU
            rect = pygame.Rect(x, y, HÜCRE_BOYUTU - gap, HÜCRE_BOYUTU - gap)
            
            if tahta[satir][sutun] == 0:
                pygame.draw.rect(ekran, tema["bos"], (rect.x + shake_x, rect.y + shake_y, rect.w, rect.h))
                pygame.draw.rect(ekran, tema["cizgi"], (rect.x + shake_x, rect.y + shake_y, rect.w, rect.h), 1)
            else:
                color_idx = (satir * IZGARA_BOYUTU + sutun) % len(aktif_blok_renkleri)
                draw_block_rect(ekran, aktif_blok_renkleri[color_idx], rect, border_radius=2, tema_idx=aktif_tema_idx, ofset_x=shake_x, ofset_y=shake_y)

    # GHOST PIECE (Hayalet Blok) SİSTEMİ YENİLİĞİ
    if surukleniyor and secili_blok:
        izgara_sutun = round((secili_blok.x - BASLANGIC_X) / HÜCRE_BOYUTU)
        izgara_satir = round((secili_blok.y - BASLANGIC_Y) / HÜCRE_BOYUTU)
        yerlesebilir = True
        
        if 0 <= izgara_satir <= IZGARA_BOYUTU - len(secili_blok.sekil) and 0 <= izgara_sutun <= IZGARA_BOYUTU - len(secili_blok.sekil[0]):
            for r in range(len(secili_blok.sekil)):
                for c in range(len(secili_blok.sekil[0])):
                    if secili_blok.sekil[r][c] == 1 and tahta[izgara_satir + r][izgara_sutun + c] == 1:
                        yerlesebilir = False
        else: yerlesebilir = False
        
        if yerlesebilir:
            for r in range(len(secili_blok.sekil)):
                for c in range(len(secili_blok.sekil[0])):
                    if secili_blok.sekil[r][c] == 1:
                        gx = BASLANGIC_X + (izgara_sutun + c) * HÜCRE_BOYUTU
                        gy = BASLANGIC_Y + (izgara_satir + r) * HÜCRE_BOYUTU
                        g_rect = pygame.Rect(gx, gy, HÜCRE_BOYUTU - gap, HÜCRE_BOYUTU - gap)
                        draw_block_rect(ekran, secili_blok.renk_cifti, g_rect, border_radius=6, tema_idx=aktif_tema_idx, alpha=100, ofset_x=shake_x, ofset_y=shake_y)


    for i in range(3):
        slot_x = 95 + i * 160
        slot_y = 690
        pygame.draw.circle(ekran, tema["accent"], (slot_x + shake_x, slot_y + shake_y), 65)
        pygame.draw.circle(ekran, (255, 255, 255) if aktif_tema_idx == 1 else tema["accent"], (slot_x + shake_x, slot_y + shake_y), 65, 2)

    for b in alttaki_bloklar:
        if b != secili_blok:
            b.ciz(ekran, surukleniyor=False, hover=(b == hovering_block), ofset_x=shake_x, ofset_y=shake_y)

    if secili_blok and surukleniyor:
        secili_blok.ciz(ekran, surukleniyor=True)

    for anim in animasyonlar:
        anim.ciz(ekran, ofset_x=shake_x, ofset_y=shake_y)

    # --- AYARLAR MENÜSÜ ---
    if ayarlar_acik:
        karartma_surface.set_alpha(200)
        ekran.blit(karartma_surface, (0, 0))
        
        menu_bg = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
        menu_renk = (139, 68, 89) if aktif_tema_idx == 1 else tema["panel"]
        baslik_renk = (255, 255, 255) if aktif_tema_idx == 1 else tema["yazi"]
        
        pygame.draw.rect(ekran, menu_renk, menu_bg, border_radius=8)
        pygame.draw.rect(ekran, tema["accent"], menu_bg, 2, border_radius=8)
        
        baslik = FONT_ANIMASYON.render("TEMALAR", True, baslik_renk)
        ekran.blit(baslik, (menu_x + menu_w//2 - baslik.get_width()//2, menu_y + 20))

        for btn in tema_butonlari:
            btn_renk = tema["accent"] if btn["idx"] == aktif_tema_idx else tema["bos"]
            pygame.draw.rect(ekran, btn_renk, btn["rect"], border_radius=4)
            pygame.draw.rect(ekran, tema["cizgi"], btn["rect"], 1, border_radius=4)
            t_isim = FONT_KUCUK.render(TEMALAR[btn["idx"]]["isim"], True, tema["yazi"])
            ekran.blit(t_isim, (btn["rect"].x + btn["rect"].width//2 - t_isim.get_width()//2, btn["rect"].y + 12))

        pygame.draw.rect(ekran, (220, 20, 60), kapat_btn_rect, border_radius=4)
        kapat_yazi = FONT_KUCUK.render("KAPAT", True, (255, 255, 255))
        ekran.blit(kapat_yazi, (kapat_btn_rect.x + kapat_btn_rect.width//2 - kapat_yazi.get_width()//2, kapat_btn_rect.y + 12))

    # --- OYUN BİTTİ EKRANI ---
    if oyun_bitti and not ayarlar_acik:
        if aktif_tema_idx == 1:
            karartma_surface.fill((139, 68, 89))
            karartma_surface.set_alpha(180)
        else:
            karartma_surface.fill((0, 0, 0))
            karartma_surface.set_alpha(190)
        ekran.blit(karartma_surface, (0, 0))
        
        go_yazi = FONT_GAMEOVER.render("OYUN BİTTİ", True, tema["accent"]) 
        ekran.blit(go_yazi, (GENISLIK // 2 - go_yazi.get_width() // 2, YUKSEKLIK // 2 - 80))
        
        skor_bilgi = FONT_ANIMASYON.render(f"Skorun: {skor}", True, (255, 255, 255))
        ekran.blit(skor_bilgi, (GENISLIK // 2 - skor_bilgi.get_width() // 2, YUKSEKLIK // 2 - 10))
        
        if skor == best_skor and skor > 0:
            best_bilgi = FONT_KUCUK.render("YENİ REKOR! 🎉", True, (255, 215, 0))
            ekran.blit(best_bilgi, (GENISLIK // 2 - best_bilgi.get_width() // 2, YUKSEKLIK // 2 + 35))
        
        tekrar_yazi = FONT_KUCUK.render("Yeniden Başlamak için 'R' Tuşuna Bas", True, tema["yazi"])
        ekran.blit(tekrar_yazi, (GENISLIK // 2 - tekrar_yazi.get_width() // 2, YUKSEKLIK // 2 + 80))

    pygame.display.flip()
    saat.tick(FPS)
