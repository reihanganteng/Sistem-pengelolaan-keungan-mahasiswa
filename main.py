import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
from collections import deque

FILE_NAME = 'transaksi.csv'
undo_stack = []             # Stack untuk Undo Hapus
antrian_hari_ini = deque()  # Queue untuk transaksi hari ini
selected_index = None       # Untuk fitur update

def load_transaksi():
    transaksi = []
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                transaksi.append(row)
    return transaksi

def simpan_transaksi(transaksi):
    with open(FILE_NAME, mode='w', newline='') as file:
        fieldnames = ['tanggal', 'jenis', 'kategori', 'jumlah', 'deskripsi']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for t in transaksi:
            writer.writerow(t)

def tambah_transaksi():
    global selected_index
    if selected_index is not None:
        messagebox.showwarning("Peringatan", "Gunakan 'Simpan Perubahan' untuk update.")
        return

    tanggal = datetime.now().strftime('%Y-%m-%d')
    jenis = jenis_var.get()
    kategori = kategori_entry.get()
    jumlah = jumlah_entry.get()
    deskripsi = deskripsi_entry.get()

    if jenis not in ['Pemasukan', 'Pengeluaran'] or not jumlah.isdigit():
        messagebox.showerror("Error", "Data tidak valid. Cek kembali input Anda.")
        return

    transaksi = load_transaksi()
    data = {
        'tanggal': tanggal,
        'jenis': jenis,
        'kategori': kategori,
        'jumlah': jumlah,
        'deskripsi': deskripsi
    }
    transaksi.append(data)
    simpan_transaksi(transaksi)

    # Tambah ke queue
    antrian_hari_ini.append(f"{jenis} - {kategori} - Rp{jumlah}")
    tampilkan_antrian()

    messagebox.showinfo("Sukses", "Transaksi berhasil ditambahkan.")
    tampilkan_transaksi()
    clear_form()

def tampilkan_transaksi():
    for item in tree.get_children():
        tree.delete(item)
    transaksi = load_transaksi()
    for t in transaksi:
        tree.insert('', 'end', values=(t['tanggal'], t['jenis'], t['kategori'], t['jumlah'], t['deskripsi']))

def hapus_transaksi():
    global selected_index
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Peringatan", "Pilih transaksi yang ingin dihapus.")
        return
    index = tree.index(selected[0])
    transaksi = load_transaksi()
    undo_stack.append(transaksi[index])
    del transaksi[index]
    simpan_transaksi(transaksi)
    tampilkan_transaksi()
    clear_form()
    messagebox.showinfo("Sukses", "Transaksi dihapus. Gunakan Undo jika perlu.")
    selected_index = None

def undo_hapus():
    if not undo_stack:
        messagebox.showinfo("Info", "Tidak ada transaksi yang bisa di-undo.")
        return
    transaksi = load_transaksi()
    transaksi.append(undo_stack.pop())
    simpan_transaksi(transaksi)
    tampilkan_transaksi()
    messagebox.showinfo("Sukses", "Transaksi terakhir dikembalikan.")

def lihat_laporan():
    transaksi = load_transaksi()
    pemasukan = sum(int(t['jumlah']) for t in transaksi if t['jenis'] == 'Pemasukan')
    pengeluaran = sum(int(t['jumlah']) for t in transaksi if t['jenis'] == 'Pengeluaran')
    saldo = pemasukan - pengeluaran

    laporan = (
        f"📊 Laporan Keuangan\n\n"
        f"Total Pemasukan: Rp{pemasukan:,}\n"
        f"Total Pengeluaran: Rp{pengeluaran:,}\n"
        f"Saldo Akhir: Rp{saldo:,}"
    )
    messagebox.showinfo("Laporan Keuangan", laporan)

def tampilkan_antrian():
    queue_list.delete(0, tk.END)
    for item in antrian_hari_ini:
        queue_list.insert(tk.END, item)

def on_tree_select(event):
    global selected_index
    selected = tree.selection()
    if selected:
        index = tree.index(selected[0])
        transaksi = load_transaksi()
        t = transaksi[index]
        jenis_var.set(t['jenis'])
        kategori_entry.delete(0, tk.END)
        kategori_entry.insert(0, t['kategori'])
        jumlah_entry.delete(0, tk.END)
        jumlah_entry.insert(0, t['jumlah'])
        deskripsi_entry.delete(0, tk.END)
        deskripsi_entry.insert(0, t['deskripsi'])
        selected_index = index

def simpan_perubahan():
    global selected_index
    if selected_index is None:
        messagebox.showwarning("Peringatan", "Pilih transaksi yang ingin diubah.")
        return

    jenis = jenis_var.get()
    kategori = kategori_entry.get()
    jumlah = jumlah_entry.get()
    deskripsi = deskripsi_entry.get()

    if not jumlah.isdigit():
        messagebox.showerror("Error", "Jumlah harus berupa angka.")
        return

    transaksi = load_transaksi()
    transaksi[selected_index] = {
        'tanggal': transaksi[selected_index]['tanggal'],
        'jenis': jenis,
        'kategori': kategori,
        'jumlah': jumlah,
        'deskripsi': deskripsi
    }
    simpan_transaksi(transaksi)
    tampilkan_transaksi()
    messagebox.showinfo("Sukses", "Perubahan berhasil disimpan.")
    clear_form()
    selected_index = None

def clear_form():
    kategori_entry.delete(0, tk.END)
    jumlah_entry.delete(0, tk.END)
    deskripsi_entry.delete(0, tk.END)
    jenis_var.set('Pemasukan')

# ========== GUI ==========
root = tk.Tk()
root.title("SiDompet - CRUD & Struktur Data")

frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky='nsew')

jenis_var = tk.StringVar(value='Pemasukan')
ttk.Label(frame, text="Jenis:").grid(row=0, column=0, sticky='w')
jenis_menu = ttk.Combobox(frame, textvariable=jenis_var, values=['Pemasukan', 'Pengeluaran'], state='readonly')
jenis_menu.grid(row=0, column=1, sticky='ew')

ttk.Label(frame, text="Kategori:").grid(row=1, column=0, sticky='w')
kategori_entry = ttk.Entry(frame)
kategori_entry.grid(row=1, column=1, sticky='ew')

ttk.Label(frame, text="Jumlah (Rp):").grid(row=2, column=0, sticky='w')
jumlah_entry = ttk.Entry(frame)
jumlah_entry.grid(row=2, column=1, sticky='ew')

ttk.Label(frame, text="Deskripsi:").grid(row=3, column=0, sticky='w')
deskripsi_entry = ttk.Entry(frame)
deskripsi_entry.grid(row=3, column=1, sticky='ew')

ttk.Button(frame, text="Tambah Transaksi", command=tambah_transaksi).grid(row=4, column=0, columnspan=2, pady=5)
ttk.Button(frame, text="Simpan Perubahan", command=simpan_perubahan).grid(row=5, column=0, columnspan=2, pady=5)

tree = ttk.Treeview(frame, columns=('Tanggal', 'Jenis', 'Kategori', 'Jumlah', 'Deskripsi'), show='headings')
for col in tree['columns']:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.grid(row=6, column=0, columnspan=2, pady=10)
tree.bind("<<TreeviewSelect>>", on_tree_select)

ttk.Label(frame, text="Antrian Hari Ini (Queue):").grid(row=7, column=0, columnspan=2)
queue_list = tk.Listbox(frame, height=4)
queue_list.grid(row=8, column=0, columnspan=2, sticky='ew')

ttk.Button(frame, text="Hapus Transaksi", command=hapus_transaksi).grid(row=9, column=0, pady=5)
ttk.Button(frame, text="Undo Hapus (Stack)", command=undo_hapus).grid(row=9, column=1, pady=5)
ttk.Button(frame, text="Lihat Laporan", command=lihat_laporan).grid(row=10, column=0, columnspan=2, pady=5)

frame.columnconfigure(1, weight=1)
root.geometry("750x650")
tampilkan_transaksi()
root.mainloop()