import json
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

# Fungsi untuk menggabungkan dua nilai CF
def combine_cf(cf1, cf2):
    return cf1 + cf2 * (1 - cf1)

# --- Load rules dari JSON ---
with open("../rules.json", "r", encoding="utf-8") as f:
    rules = json.load(f)

# --- Ambil semua gejala unik ---
possible_facts = sorted({g for r in rules for g in r["if"]})

# --- Deskripsi penyakit ---
penyakit_info = {
    "busuk_akar": "Terjadi karena jamur *Phytophthora capsici*. Menyerang akar dan batang bawah sehingga tanaman layu dan mati mendadak.",
    "busuk_pangkal": "Disebabkan oleh jamur *Fusarium sp.*. Ditandai dengan kulit batang hitam dan pembuluh berwarna cokelat.",
    "kuning_daun": "Disebabkan kekurangan unsur hara atau infeksi virus. Daun menguning dan gugur perlahan, pertumbuhan terhambat.",
    "kerdil_keriting": "Akibat serangan virus. Tanaman tumbuh kerdil, daun berkerut, dan ukuran buah mengecil.",
    "busuk_tunggul": "Terjadi karena jamur tanah yang menyerang pangkal batang atau tunggul bekas pemangkasan.",
    "ganggang_pirang": "Disebabkan oleh ganggang *Cephaleuros virescens* yang menyerang permukaan daun muda dan batang."
}

class ExpertUI:
    def __init__(self, root):
        self.root = root
        root.title("🌿 Sistem Pakar Penyakit Tanaman Lada (Metode Certainty Factor)")
        frame = ttk.Frame(root, padding=12)
        frame.grid()

        ttk.Label(frame, text="Centang gejala yang terjadi:", font=("Segoe UI", 10, "bold")).grid(column=0, row=0, sticky="w")

        # daftar gejala
        self.vars = {}
        row = 1
        for g in possible_facts:
            v = tk.DoubleVar(value=0.0)
            cb = ttk.Checkbutton(frame, text=g.replace("_", " ").title(), variable=v, onvalue=1.0, offvalue=0.0)
            cb.grid(column=0, row=row, sticky="w")
            self.vars[g] = v
            row += 1

        # tombol diagnosa
        ttk.Button(frame, text="🔍 Diagnosa", command=self.infer).grid(column=0, row=row, pady=10, sticky="w")

        # area hasil
        self.result_txt = tk.Text(frame, width=70, height=16, bg="#f7f7f7", fg="#222", font=("Consolas", 10))
        self.result_txt.grid(column=0, row=row + 1, pady=8)

    def infer(self):
        selected = [g for g, var in self.vars.items() if var.get() == 1.0]
        known = {s: 1.0 for s in selected}
        fired = True
        fired_rules = set()

        while fired:
            fired = False
            for r in rules:
                if r["id"] in fired_rules:
                    continue

                prem = r["if"]
                matched = [p for p in prem if p in known]
                if not matched:
                    continue

                ratio = len(matched) / len(prem)
                premise_cf = min(known[p] for p in matched)
                weighted_cf = premise_cf * ratio
                inferred_cf = weighted_cf * r.get("cf", 1.0)
                conclusion = r["then"]

                if conclusion in known:
                    known[conclusion] = combine_cf(known[conclusion], inferred_cf)
                else:
                    known[conclusion] = inferred_cf

                fired_rules.add(r["id"])
                fired = True

        sorted_results = sorted(known.items(), key=lambda x: x[1], reverse=True)
        self.result_txt.delete(1.0, tk.END)
        self.result_txt.insert(tk.END, "=== HASIL DIAGNOSA ===\n\n")

        has_result = False
        penyakit_labels = []
        cf_values = []

        for fact, cf in sorted_results:
            if fact not in possible_facts:
                has_result = True
                nama = fact.replace("_", " ").title()
                cf_percent = cf * 100
                penyakit_labels.append(nama)
                cf_values.append(cf_percent)

                self.result_txt.insert(tk.END, f"🌱 {nama} : {cf_percent:.1f}%\n")
                if fact in penyakit_info:
                    self.result_txt.insert(tk.END, f"   🩺 {penyakit_info[fact]}\n\n")

        if not has_result:
            self.result_txt.insert(tk.END, "Tidak ada penyakit yang dapat didiagnosa berdasarkan gejala tersebut.\n")
        else:
            # --- Tampilkan grafik batang ---
            plt.figure(figsize=(6, 4))
            plt.barh(penyakit_labels, cf_values, color='seagreen')
            plt.xlabel('Tingkat Keyakinan (%)')
            plt.title('Hasil Diagnosa Penyakit Tanaman Lada')
            plt.xlim(0, 100)
            plt.grid(axis='x', linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.show()

# --- Jalankan GUI ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpertUI(root)
    root.mainloop()
