import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3
import os

# === 1. VERİTABANI BAĞLANTISI ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'kurs_platformu.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS kurslar (id TEXT PRIMARY KEY, ad TEXT, egitmen TEXT, kontenjan INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS egitmenler (id TEXT PRIMARY KEY, ad TEXT, uzmanlik TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS ogrenciler (id TEXT PRIMARY KEY, ad TEXT, email TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS kayitlar (ogrenci_id TEXT, kurs_id TEXT)''')
conn.commit()

# === 1.5 BAŞLANGIÇ VERİLERİ (SEEDING) ===
cursor.execute("SELECT COUNT(*) FROM egitmenler")
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO egitmenler VALUES ('E01', 'Erdem Yücesan', 'Nesne Tabanlı Programlama')")
    cursor.execute("INSERT INTO egitmenler VALUES ('E02', 'Muharrem Altunışık', 'Veritabanı (SQL)')")
    cursor.execute("INSERT INTO ogrenciler VALUES ('O1', 'Avni Özyurt', 'avniozyurt@gmail.com')")
    cursor.execute("INSERT INTO ogrenciler VALUES ('O2', 'Umut Kuruel', 'umutkuruel@gmail.com')")
    cursor.execute("INSERT INTO kurslar VALUES ('K1', 'Python ile Nesne Tabanlı Programlama', 'Erdem Hoca', 100)")
    conn.commit()

# === 2. OOP SINIFLARI ===
class Kurs:
    def __init__(self, kurs_id, kurs_adi, egitmen, kontenjan):
        self.kurs_id = kurs_id
        self.kurs_adi = kurs_adi
        self.egitmen = egitmen
        self.kontenjan = int(kontenjan)

    def ogrenci_kaydet(self):
        if self.kontenjan > 0:
            self.kontenjan -= 1
            cursor.execute("UPDATE kurslar SET kontenjan = ? WHERE id = ?", (self.kontenjan, self.kurs_id))
            conn.commit()
            return True
        return False

class Egitmen:
    def __init__(self, e_id, ad, uzmanlik):
        self.e_id = e_id # ID özelliği eklendi
        self.ad = ad
        self.uzmanlik = uzmanlik

class Ogrenci:
    def __init__(self, ogrenci_id, ad, email):
        self.ogrenci_id = ogrenci_id
        self.ad = ad
        self.email = email

    def kurs_listesi(self):
        cursor.execute("SELECT k.ad FROM kayitlar kay JOIN kurslar k ON kay.kurs_id = k.id WHERE kay.ogrenci_id = ?", (self.ogrenci_id,))
        return [row[0] for row in cursor.fetchall()]

# === 3. ARAYÜZ (GUI) FONKSİYONLARI ===
kurslar = []
ogrenciler = []
egitmenler = []

def verileri_tazele():
    kurslar.clear(); ogrenciler.clear(); egitmenler.clear()
    for s in cursor.execute("SELECT * FROM kurslar"): kurslar.append(Kurs(*s))
    for s in cursor.execute("SELECT * FROM ogrenciler"): ogrenciler.append(Ogrenci(*s))
    for s in cursor.execute("SELECT * FROM egitmenler"): egitmenler.append(Egitmen(*s))

def kurs_ekle_gui():
    k_id = simpledialog.askstring("Giriş", "Kurs ID:", parent=pencere)
    if not k_id: return
    ad = simpledialog.askstring("Giriş", "Kurs Adı:", parent=pencere)
    egitmen = simpledialog.askstring("Giriş", "Eğitmen Adı:", parent=pencere)
    kontenjan = simpledialog.askinteger("Giriş", "Kontenjan:", parent=pencere)
    if kontenjan is None: return
    try:
        cursor.execute("INSERT INTO kurslar VALUES (?, ?, ?, ?)", (k_id, ad, egitmen, kontenjan))
        conn.commit(); verileri_tazele()
        messagebox.showinfo("Başarılı", "Kurs sisteme eklendi.", parent=pencere)
    except:
        messagebox.showerror("Hata", "Bu Kurs ID zaten kullanılıyor!", parent=pencere)

def ogrenci_ekle_gui():
    o_id = simpledialog.askstring("Giriş", "Öğrenci ID:", parent=pencere)
    if not o_id: return
    ad = simpledialog.askstring("Giriş", "Ad Soyad:", parent=pencere)
    mail = simpledialog.askstring("Giriş", "E-mail:", parent=pencere)
    try:
        cursor.execute("INSERT INTO ogrenciler VALUES (?, ?, ?)", (o_id, ad, mail))
        conn.commit(); verileri_tazele()
        messagebox.showinfo("Başarılı", "Öğrenci sisteme eklendi.", parent=pencere)
    except:
        messagebox.showerror("Hata", "Bu Öğrenci ID zaten kullanılıyor!", parent=pencere)

def egitmen_ekle_gui():
    e_id = simpledialog.askstring("Giriş", "Eğitmen ID:", parent=pencere)
    if not e_id: return
    ad = simpledialog.askstring("Giriş", "Eğitmen Adı:", parent=pencere)
    uzmanlik = simpledialog.askstring("Giriş", "Uzmanlık Alanı:", parent=pencere)
    try:
        cursor.execute("INSERT INTO egitmenler VALUES (?, ?, ?)", (e_id, ad, uzmanlik))
        conn.commit(); verileri_tazele()
        messagebox.showinfo("Başarılı", "Eğitmen sisteme eklendi.", parent=pencere)
    except:
        messagebox.showerror("Hata", "Bu Eğitmen ID zaten kullanılıyor!", parent=pencere)

def kayit_yap_gui():
    verileri_tazele()
    k_id = simpledialog.askstring("İşlem", "Kurs ID:", parent=pencere)
    o_id = simpledialog.askstring("İşlem", "Öğrenci ID:", parent=pencere)
    sec_k = next((k for k in kurslar if k.kurs_id == k_id), None)
    sec_o = next((o for o in ogrenciler if o.ogrenci_id == o_id), None)
    if sec_k and sec_o:
        if sec_k.ogrenci_kaydet():
            cursor.execute("INSERT INTO kayitlar VALUES (?, ?)", (o_id, k_id))
            conn.commit()
            messagebox.showinfo("Başarılı", "Kayıt yapıldı.", parent=pencere)
        else:
            messagebox.showwarning("Uyarı", "Kontenjan dolu!", parent=pencere)
    else:
        messagebox.showerror("Hata", "Bulunamadı.", parent=pencere)

#  ID GÖSTERİYOR
def egitmenleri_listele_gui():
    verileri_tazele()
    if not egitmenler:
        messagebox.showinfo("Bilgi", "Sistemde eğitmen yok.", parent=pencere)
        return
    m = "\n".join([f"[{e.e_id}] {e.ad} - Uzmanlık: {e.uzmanlik}" for e in egitmenler])
    messagebox.showinfo("Eğitmen Listesi", m, parent=pencere)

def kurslari_listele_gui():
    verileri_tazele()
    if not kurslar:
        messagebox.showinfo("Bilgi", "Sistemde kurs yok.", parent=pencere)
        return
    m = "\n".join([f"[{k.kurs_id}] {k.kurs_adi} (Kalan: {k.kontenjan})" for k in kurslar])
    messagebox.showinfo("Tüm Kurslar", m, parent=pencere)

def ogrencileri_listele_gui():
    verileri_tazele()
    if not ogrenciler:
        messagebox.showinfo("Bilgi", "Sistemde öğrenci yok.", parent=pencere)
        return
    m = "\n".join([f"[{o.ogrenci_id}] {o.ad} - {o.email}" for o in ogrenciler])
    messagebox.showinfo("Tüm Öğrenciler", m, parent=pencere)

def ogrenci_kurs_listele_gui():
    verileri_tazele()
    o_id = simpledialog.askstring("Sorgu", "Öğrenci ID:", parent=pencere)
    sec_o = next((o for o in ogrenciler if o.ogrenci_id == o_id), None)
    if sec_o:
        alinan = sec_o.kurs_listesi()
        m = "\n".join(alinan) if alinan else "Kayıtlı kurs yok."
        messagebox.showinfo(f"{sec_o.ad} Kursları", m, parent=pencere)

# SİLME İŞLEMLERİ
def kurs_sil_gui():
    k_id = simpledialog.askstring("Sil", "Kurs ID:", parent=pencere)
    if k_id and messagebox.askyesno("Onay", "Silinsin mi?", parent=pencere):
        cursor.execute("DELETE FROM kurslar WHERE id = ?", (k_id,))
        conn.commit(); verileri_tazele()

def ogrenci_sil_gui():
    o_id = simpledialog.askstring("Sil", "Öğrenci ID:", parent=pencere)
    if o_id and messagebox.askyesno("Onay", "Silinsin mi?", parent=pencere):
        cursor.execute("DELETE FROM ogrenciler WHERE id = ?", (o_id,))
        conn.commit(); verileri_tazele()

def egitmen_sil_gui():
    e_id = simpledialog.askstring("Sil", "Eğitmen ID:", parent=pencere)
    if e_id and messagebox.askyesno("Onay", "Silinsin mi?", parent=pencere):
        cursor.execute("DELETE FROM egitmenler WHERE id = ?", (e_id,))
        conn.commit(); verileri_tazele()

# === 4. DASHBOARD TASARIMI (RENKLER VE BOYUTLAR AYNI) ===
pencere = tk.Tk()
pencere.title("Online Kurs Platformu Kontrol Paneli")
pencere.geometry("850x500")
pencere.configure(bg="#192a56")

tk.Label(pencere, text="KURS PLATFORMU YÖNETİM PANELİ", fg="#00a8ff", bg="#192a56", font=("Arial", 20, "bold")).pack(pady=15)

ana_frame = tk.Frame(pencere, bg="#192a56")
ana_frame.pack(pady=10)

# Sütunlar
f_ekle = tk.Frame(ana_frame, bg="#192a56"); f_ekle.grid(row=0, column=0, padx=15, sticky="n")
f_list = tk.Frame(ana_frame, bg="#192a56"); f_list.grid(row=0, column=1, padx=15, sticky="n")
f_sil = tk.Frame(ana_frame, bg="#192a56"); f_sil.grid(row=0, column=2, padx=15, sticky="n")

# Sütun Başlıkları
tk.Label(f_ekle, text="➕ EKLEME", fg="#f1c40f", bg="#192a56", font=("Arial", 12, "bold")).pack(pady=5)
tk.Label(f_list, text="🔍 LİSTELEME", fg="#2ecc71", bg="#192a56", font=("Arial", 12, "bold")).pack(pady=5)
tk.Label(f_sil, text="🗑️ SİLME", fg="#e74c3c", bg="#192a56", font=("Arial", 12, "bold")).pack(pady=5)

def buton_olustur(h, y, k, r="#2f3640", yr="white"):
    tk.Button(h, text=y, command=k, font=("Arial", 11, "bold"), width=24, height=2, bg=r, fg=yr, cursor="hand2").pack(pady=5)

# 1. SÜTUN
buton_olustur(f_ekle, "Yeni Kurs Ekle", kurs_ekle_gui)
buton_olustur(f_ekle, "Yeni Öğrenci Ekle", ogrenci_ekle_gui)
buton_olustur(f_ekle, "Yeni Eğitmen Ekle", egitmen_ekle_gui)
buton_olustur(f_ekle, "Kursa Kaydet", kayit_yap_gui, "#3498db")

# 2. SÜTUN
buton_olustur(f_list, "Tüm Kursları Gör", kurslari_listele_gui)
buton_olustur(f_list, "Tüm Öğrencileri Gör", ogrencileri_listele_gui)
buton_olustur(f_list, "Tüm Eğitmenleri Gör", egitmenleri_listele_gui)
buton_olustur(f_list, "Öğrenci Kursları", ogrenci_kurs_listele_gui, "#e1b12c", "black")

# 3. SÜTUN
buton_olustur(f_sil, "Kurs Sil", kurs_sil_gui, "#c0392b")
buton_olustur(f_sil, "Öğrenci Sil", ogrenci_sil_gui, "#c0392b")
buton_olustur(f_sil, "Eğitmen Sil", egitmen_sil_gui, "#c0392b")

tk.Button(pencere, text="SİSTEMDEN ÇIKIŞ YAP", command=pencere.quit, font=("Arial", 12, "bold"), width=30, bg="#576574", fg="white").pack(pady=25)

verileri_tazele()
pencere.mainloop()
