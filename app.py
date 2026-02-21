import customtkinter as ctk
from tkinter import messagebox
from supabase import create_client, Client

# --- KONFIGURATION ---
LAPD_BLUE = "#001D3D"
LAPD_ACCENT = "#FFD700"
LAPD_TEXT = "#E0E0E0"

# Setze hier deine Daten ein
SUPABASE_URL = "https://djygnispywljflrhxwyv.supabase.co"
SUPABASE_KEY = "sb_publishable_sRR_KUa2ujLYxCaktLhRWQ_trkT8vXY"

class LAPD_MDC(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LAPD MDC - Unit Dispatch v3.0")
        self.after(0, lambda: self.state('zoomed'))
        self.configure(fg_color=LAPD_BLUE)
        
        try:
            self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except:
            messagebox.showerror("Error", "Zentrale nicht erreichbar!")

        self.setup_ui()
        self.load_units()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=300, fg_color="#001220", border_color=LAPD_ACCENT, border_width=1)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="POLICE DEPT.", font=("Impact", 30), text_color="white").pack(pady=20)

        self.entry_callsign = ctk.CTkEntry(self.sidebar, placeholder_text="Callsign (z.B. 7-XRAY-1)")
        self.entry_callsign.pack(pady=10, padx=20, fill="x")
        
        self.entry_officers = ctk.CTkEntry(self.sidebar, placeholder_text="Officers")
        self.entry_officers.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(self.sidebar, text="UNIT DEPLOY", fg_color="#1A5276", command=self.deploy_unit).pack(pady=20, padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="REFRESH SYSTEM", command=self.load_units).pack(pady=10, padx=20, fill="x")

        # --- MAIN VIEW ---
        self.main_view = ctk.CTkScrollableFrame(self, label_text="FIELD OPERATIONS", fg_color=LAPD_BLUE)
        self.main_view.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def deploy_unit(self):
        call = self.entry_callsign.get()
        offi = self.entry_officers.get()
        if call and offi:
            self.supabase.table("units").insert({"callsign": call, "officers": offi, "status": "AVAILABLE"}).execute()
            self.load_units()
        else:
            messagebox.showwarning("Warning", "Bitte alle Felder ausfüllen!")

    def load_units(self):
        for widget in self.main_view.winfo_children(): widget.destroy()
        
        response = self.supabase.table("units").select("*").execute()
        for unit in response.data:
            self.create_unit_card(unit)

    def create_unit_card(self, unit):
        # Farbe basierend auf Status
        status_colors = {"AVAILABLE": "#2ECC71", "EN ROUTE": "#F1C40F", "BUSY": "#E74C3C", "OFF DUTY": "#95A5A6"}
        current_color = status_colors.get(unit['status'], "white")

        card = ctk.CTkFrame(self.main_view, fg_color="#00284D", border_width=1, border_color="#1A5276")
        card.pack(fill="x", pady=5, padx=5)

        # Info Text
        info = f"UNIT: {unit['callsign']} | CREW: {unit['officers']}"
        ctk.CTkLabel(card, text=info, font=("Consolas", 14), text_color=LAPD_TEXT).pack(side="left", padx=20, pady=15)

        # Status Label
        status_lbl = ctk.CTkLabel(card, text=unit['status'], text_color=current_color, font=("Consolas", 14, "bold"))
        status_lbl.pack(side="left", padx=20)

        # --- STATUS ÄNDERN MENÜ ---
        status_menu = ctk.CTkOptionMenu(card, values=["AVAILABLE", "EN ROUTE", "BUSY", "OFF DUTY"], 
                                       width=120, height=25, fg_color="#34495E",
                                       command=lambda val, uid=unit['id']: self.update_status(uid, val))
        status_menu.set(unit['status'])
        status_menu.pack(side="right", padx=10)

        # Lösch-Button
        ctk.CTkButton(card, text="DEL", width=40, height=25, fg_color="#922B21", 
                      command=lambda i=unit['id']: self.delete_unit(i)).pack(side="right", padx=5)

    def update_status(self, unit_id, new_status):
        """Aktualisiert den Status direkt in Supabase."""
        try:
            self.supabase.table("units").update({"status": new_status}).eq("id", unit_id).execute()
            self.load_units() # Neu laden für Farb-Update
        except Exception as e:
            messagebox.showerror("Update Error", str(e))

    def delete_unit(self, unit_id):
        self.supabase.table("units").delete().eq("id", unit_id).execute()
        self.load_units()

if __name__ == "__main__":
    app = LAPD_MDC()
    app.mainloop()
