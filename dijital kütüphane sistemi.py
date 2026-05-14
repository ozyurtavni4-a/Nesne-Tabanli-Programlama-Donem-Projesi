import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3
import os
import datetime 

# === 1. VERİTABANI BAĞLANTISI ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'kutuphane_sistemi_final.db') 
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Tabloları oluştur 
cursor.execute('''CREATE TABLE IF NOT EXISTS kitaplar (id TEXT PRIMARY KEY, ad TEXT, yazar TEXT, kategori TEXT, durum TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS uyeler (id TEXT PRIMARY KEY, ad TEXT, email TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS oduncler (odunc_id TEXT PRIMARY KEY, kitap_id TEXT, uye_id TEXT, odunc_tarihi TEXT, iade_tarihi TEXT)''')
conn.commit()

# === 1.5 BAŞLANGIÇ VERİLERİ (SEEDING) ===
cursor.execute("SELECT COUNT(*) FROM kitaplar")
if cursor.fetchone()[0] == 0:
    # Örnek Kitaplar 
    cursor.execute("INSERT INTO kitaplar VALUES ('K1', 'Ajan', 'Stuart Woods', 'Polisiye', 'Rafta')")
    cursor.execute("INSERT INTO kitaplar VALUES ('K2', 'Demir Orkide', 'Stuart Woods', 'Gerilim', 'Rafta')")
    cursor.execute("INSERT INTO kitaplar VALUES ('K3', 'Suç ve Ceza', 'Fyodor Dostoyevski', 'Klasik', 'Rafta')")
    
    # Örnek Üyeler 
    cursor.execute("INSERT INTO uyeler VALUES ('U1', 'Avni Özyurt', 'avniozyurt@gmail.com')")
    cursor.execute("INSERT INTO uyeler VALUES ('U2', 'Umut Kuruel', 'umutkuruel@gmail.com')")
    conn.commit()

# === 2. OOP SINIFLARI  ===
class Kitap:
    def __init__(self, kitap_id, ad, yazar, kategori, durum="Rafta"):
        self.kitap_id = kitap_id
        self.ad = ad
        self.yazar = yazar
        self.kategori = kategori
        self.durum = durum

    def kitap_durumu_degistir(self, yeni_durum):
        self.durum = yeni_durum
        cursor.execute("UPDATE kitaplar SET durum = ? WHERE id = ?", (self.durum, self.kitap_id))
        conn.commit()

class Uye:
    def __init__(self, uye_id, ad, email):
        self.uye_id = uye_id
        self.ad = ad
        self.email = email

    def kitap_odunc_al(self, kitap):
        if kitap.durum == "Rafta":
            kitap.kitap_durumu_degistir("Ödünç Verildi")
            return True
        return False

    def kitap_iade_et(self, kitap):
        if kitap.durum == "Ödünç Verildi":
            kitap.kitap_durumu_degistir("Rafta")
            return True
        return False

class Odunc:
    def __init__(self, odunc_id, kitap, uye, odunc_tarihi, iade_tarihi="Teslim Edilmedi"):
        self.odunc_id = odunc_id
        self.kitap = kitap
        self.uye = uye
        self.odunc_tarihi = odunc_tarihi
        self.iade_tarihi = iade_tarihi

# === 3. ARAYÜZ (GUI) FONKSİYONLARI ===
kitap_listesi = []
uye_listesi = []

def verileri_tazele():
    kitap_listesi.clear(); uye_listesi.clear()
    for s in cursor.execute("SELECT * FROM kitaplar"): kitap_listesi.append(Kitap(*s))
    for s in cursor.execute("SELECT * FROM uyeler"): uye_listesi.append(Uye(*s))

def kitap_ekle_gui():
    k_id = simpledialog.askstring("Giriş", "Kitap ID (Örn: K10):", parent=pencere)
    if not k_id: return
    ad = simpledialog.askstring("Giriş", "Kitap Adı:", parent=pencere)
    yazar = simpledialog.askstring("Giriş", "Yazar Adı:", parent=pencere)
    kategori = simpledialog.askstring("Giriş", "Kategori (Roman, Bilim vb.):", parent=pencere)
    try:
        cursor.execute("INSERT INTO kitaplar VALUES (?, ?, ?, ?, 'Rafta')", (k_id, ad, yazar, kategori))
        conn.commit(); verileri_tazele()
        messagebox.showinfo("Başarılı", "Kitap kütüphaneye eklendi.", parent=pencere)
    except:
        messagebox.showerror("Hata", "Bu Kitap ID zaten var!", parent=pencere)

def uye_ekle_gui():
    u_id = simpledialog.askstring("Giriş", "Üye ID (Örn: U50):", parent=pencere)
    if not u_id: return
    ad = simpledialog.askstring("Giriş", "Ad Soyad:", parent=pencere)
    mail = simpledialog.askstring("Giriş", "E-posta:", parent=pencere)
    try:
        cursor.execute("INSERT INTO uyeler VALUES (?, ?, ?)", (u_id, ad, mail))
        conn.commit(); verileri_tazele()
        messagebox.showinfo("Başarılı", "Üye kaydı yapıldı.", parent=pencere)
    except:
        messagebox.showerror("Hata", "Bu Üye ID zaten kullanılıyor!", parent=pencere)

def odunc_ver_gui():
    verileri_tazele()
    k_id = simpledialog.askstring("İşlem", "Ödünç Alınacak Kitap ID:", parent=pencere)
    u_id = simpledialog.askstring("İşlem", "Üye ID:", parent=pencere)
    sec_k = next((k for k in kitap_listesi if k.kitap_id == k_id), None)
    sec_u = next((u for u in uye_listesi if u.uye_id == u_id), None)
    
    if sec_k and sec_u:
        if sec_u.kitap_odunc_al(sec_k): # OOP Metodu kullanıldı
            tarih = datetime.datetime.now().strftime("%Y-%m-%d")
            o_id = f"OD_{k_id}_{u_id}"
            cursor.execute("INSERT INTO oduncler VALUES (?, ?, ?, ?, 'Teslim Edilmedi')", (o_id, k_id, u_id, tarih))
            conn.commit()
            messagebox.showinfo("Başarılı", f"Kitap verildi. Yeni Durum: {sec_k.durum}", parent=pencere)
        else:
            messagebox.showwarning("Uyarı", "Bu kitap şu an rafta değil!", parent=pencere)
    else:
        messagebox.showerror("Hata", "Kitap veya Üye bulunamadı.", parent=pencere)

def iade_al_gui():
    verileri_tazele()
    k_id = simpledialog.askstring("İşlem", "İade Edilecek Kitap ID:", parent=pencere)
    sec_k = next((k for k in kitap_listesi if k.kitap_id == k_id), None)
    
    if sec_k:
        
        ornek_uye = Uye("Sistem", "Sistem", "sistem") 
        if ornek_uye.kitap_iade_et(sec_k): # OOP Metodu kullanıldı
            tarih = datetime.datetime.now().strftime("%Y-%m-%d")
            cursor.execute("UPDATE oduncler SET iade_tarihi = ? WHERE kitap_id = ? AND iade_tarihi = 'Teslim Edilmedi'", (tarih, k_id))
            conn.commit()
            messagebox.showinfo("Başarılı", "Kitap kütüphaneye iade edildi.", parent=pencere)
        else:
            messagebox.showinfo("Bilgi", "Bu kitap zaten rafta görünüyor.", parent=pencere)
    else:
        messagebox.showerror("Hata", "Kitap bulunamadı.", parent=pencere)

# LİSTELEME
def kitaplari_listele_gui():
    verileri_tazele()
    if not kitap_listesi:
        messagebox.showinfo("Bilgi", "Kütüphane boş.", parent=pencere)
        return
    m = "\n".join([f"[{k.kitap_id}] {k.ad} - {k.kategori} ({k.durum})" for k in kitap_listesi])
    messagebox.showinfo("Kitap Listesi", m, parent=pencere)

def uyeleri_listele_gui():
    verileri_tazele()
    if not uye_listesi:
        messagebox.showinfo("Bilgi", "Kayıtlı üye yok.", parent=pencere)
        return
    m = "\n".join([f"[{u.uye_id}] {u.ad} - {u.email}" for u in uye_listesi])
    messagebox.showinfo("Üye Listesi", m, parent=pencere)

def uye_kitaplari_listele_gui():
    verileri_tazele()
    u_id = simpledialog.askstring("Sorgu", "Üye ID Girin:", parent=pencere)
    sec_u = next((u for u in uye_listesi if u.uye_id == u_id), None)
    if sec_u:
        cursor.execute("SELECT k.ad FROM oduncler o JOIN kitaplar k ON o.kitap_id = k.id WHERE o.uye_id = ? AND o.iade_tarihi = 'Teslim Edilmedi'", (u_id,))
        alinanlar = [row[0] for row in cursor.fetchall()]
        m = "\n".join(alinanlar) if alinanlar else "Bu üye henüz kitap almamış veya hepsini iade etmiş."
        messagebox.showinfo(f"{sec_u.ad} Üzerindeki Kitaplar", m, parent=pencere)
    else:
        messagebox.showerror("Hata", "Üye bulunamadı.", parent=pencere)

# SİLME
def kitap_sil_gui():
    k_id = simpledialog.askstring("Sil", "Silinecek Kitap ID:", parent=pencere)
    if k_id and messagebox.askyesno("Onay", "Kitap silinsin mi?", parent=pencere):
        cursor.execute("DELETE FROM kitaplar WHERE id = ?", (k_id,))
        conn.commit(); verileri_tazele()

def uye_sil_gui():
    u_id = simpledialog.askstring("Sil", "Silinecek Üye ID:", parent=pencere)
    if u_id and messagebox.askyesno("Onay", "Üye kaydı silinsin mi?", parent=pencere):
        cursor.execute("DELETE FROM uyeler WHERE id = ?", (u_id,))
        conn.commit(); verileri_tazele()

# === 4. DASHBOARD TASARIMI ===
pencere = tk.Tk()
pencere.title("Kütüphane Yönetim Sistemi")
pencere.geometry("850x550") 
pencere.configure(bg="#192a56")

tk.Label(pencere, text="KÜTÜPHANE YÖNETİM PANELİ", fg="#00a8ff", bg="#192a56", font=("Arial", 20, "bold")).pack(pady=15)

ana_frame = tk.Frame(pencere, bg="#192a56")
ana_frame.pack(pady=10)

# Sütunlar 
f_ekle = tk.Frame(ana_frame, bg="#192a56"); f_ekle.grid(row=0, column=0, padx=15, sticky="n")
f_list = tk.Frame(ana_frame, bg="#192a56"); f_list.grid(row=0, column=1, padx=15, sticky="n")
f_sil = tk.Frame(ana_frame, bg="#192a56"); f_sil.grid(row=0, column=2, padx=15, sticky="n")

# Başlıklar
tk.Label(f_ekle, text="➕ KAYIT İŞLEMLERİ", fg="#f1c40f", bg="#192a56", font=("Arial", 12, "bold")).pack(pady=5)
tk.Label(f_list, text="🔍 LİSTELEME", fg="#2ecc71", bg="#192a56", font=("Arial", 12, "bold")).pack(pady=5)
tk.Label(f_sil, text="🗑️ SİLME İŞLEMLERİ", fg="#e74c3c", bg="#192a56", font=("Arial", 12, "bold")).pack(pady=5)

def buton_olustur(h, y, k, r="#2f3640", yr="white"):
    tk.Button(h, text=y, command=k, font=("Arial", 11, "bold"), width=24, height=2, bg=r, fg=yr, cursor="hand2").pack(pady=5)

# 1. SÜTUN
buton_olustur(f_ekle, "Yeni Kitap Ekle", kitap_ekle_gui)
buton_olustur(f_ekle, "Yeni Üye Kaydı", uye_ekle_gui)
buton_olustur(f_ekle, "Kitap Ödünç Ver", odunc_ver_gui, "#3498db")
buton_olustur(f_ekle, "Kitap İade Al", iade_al_gui, "#e67e22") 

# 2. SÜTUN
buton_olustur(f_list, "Tüm Kitapları Gör", kitaplari_listele_gui)
buton_olustur(f_list, "Tüm Üyeleri Gör", uyeleri_listele_gui)
buton_olustur(f_list, "Üyenin Kitaplarını Gör", uye_kitaplari_listele_gui, "#e1b12c", "black")

# 3. SÜTUN
buton_olustur(f_sil, "Kitap Sil", kitap_sil_gui, "#c0392b")
buton_olustur(f_sil, "Üye Sil", uye_sil_gui, "#c0392b")

tk.Button(pencere, text="SİSTEMİ KAPAT", command=pencere.quit, font=("Arial", 12, "bold"), width=30, bg="#576574", fg="white").pack(pady=25)

verileri_tazele()
pencere.mainloop()
