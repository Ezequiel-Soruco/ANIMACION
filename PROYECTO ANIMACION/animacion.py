import tkinter as tk
import math
import random

class AnimationMath:
    @staticmethod
    def ease_in_out(t):
        
        return t * t * (3 - 2 * t)

    @staticmethod
    def ease_in(t):
       
        return t * t * t

    @staticmethod
    def ease_out(t):
      
        return 1 - (1 - t) ** 3

    @staticmethod
    def elastic_out(t):
       
        if t == 0 or t == 1:
            return t
        return (2 ** (-10 * t)) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1

    @staticmethod
    def arc_trajectory(sx, sy, ex, ey, peak_offset, t):
       
        x = sx + (ex - sx) * t
        mid_y = (sy + ey) / 2 - peak_offset
        y = (1 - t) * (1 - t) * sy + 2 * (1 - t) * t * mid_y + t * t * ey
        return x, y

    @staticmethod
    def lerp(a, b, t):
        return a + (b - a) * t

    @staticmethod
    def blend_color(hex_col, bg="#1E2040", alpha=0.22):
        def parse(h):
            h = h.lstrip("#")
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        r1, g1, b1 = parse(hex_col)
        r2, g2, b2 = parse(bg)
        r = int(r1 * alpha + r2 * (1 - alpha))
        g = int(g1 * alpha + g2 * (1 - alpha))
        b = int(b1 * alpha + b2 * (1 - alpha))
        return f"#{r:02x}{g:02x}{b:02x}"


# =========================================================================
# MODEL — Propiedades físicas y de expresión del personaje
# =========================================================================
class SlimeCharacter:
    def __init__(self, x, y):
        self.base_x = x
        self.base_y = y
        self.x = x
        self.y = y

        # Dimensiones base
        self.radius_x = 46
        self.radius_y = 42
        self.scale_x = 1.0
        self.scale_y = 1.0

        # Acción secundaria — antena pendular
        self.antenna_angle = 0.0
        self.antenna_length = 34

        # Expresión facial
        self.eye_offset_x = 0.0
        self.eye_offset_y = 0.0
        self.pupil_scale = 1.0
        self.mouth_state = "smile"   # smile | open | flat | wide | sad

        # Brazo (para animación de saludo)
        self.arm_angle = 0.0         # ángulo del brazo derecho
        self.show_arm = False

        # Partículas vivas
        self.particles = []

    def squash_stretch(self, sx, sy):
        """Conserva masa (volumen constante). Principio 1."""
        self.scale_x = sx
        self.scale_y = sy

    def reset(self):
        self.x = self.base_x
        self.y = self.base_y
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.antenna_angle = 0.0
        self.eye_offset_x = 0.0
        self.eye_offset_y = 0.0
        self.pupil_scale = 1.0
        self.mouth_state = "smile"
        self.arm_angle = 0.0
        self.show_arm = False
        self.particles.clear()

    # --- Fábrica de partículas ---
    def emit_dust(self, n=8):
        for _ in range(n):
            angle = random.uniform(0, math.pi)
            speed = random.uniform(2, 6)
            self.particles.append({
                "type": "dust",
                "x": self.x, "y": self.y + self.radius_y,
                "vx": math.cos(angle) * speed * random.choice([-1, 1]),
                "vy": -math.sin(angle) * speed * 0.5,
                "life": 1.0, "r": random.randint(3, 7),
                "color": random.choice(["#C8A96E", "#E8C87A", "#A07850"])
            })

    def emit_sparkle(self, n=6):
        for _ in range(n):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 9)
            self.particles.append({
                "type": "sparkle",
                "x": self.x + random.uniform(-20, 20),
                "y": self.y - self.radius_y + random.uniform(-10, 10),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 3,
                "life": 1.0, "r": random.randint(2, 5),
                "color": random.choice(["#FFD700", "#FFF176", "#FFB300", "#FFFFFF"])
            })

    def emit_speed_lines(self, n=5):
        for _ in range(n):
            self.particles.append({
                "type": "speed_line",
                "x": self.x - random.uniform(30, 90),
                "y": self.y + random.uniform(-self.radius_y, self.radius_y),
                "vx": -12, "vy": 0,
                "life": 1.0, "r": 2,
                "color": random.choice(["#00F2FE", "#4FACFE", "#FFFFFF"])
            })

    def emit_trail(self):
        self.particles.append({
            "type": "trail",
            "x": self.x, "y": self.y,
            "vx": 0, "vy": 0,
            "life": 1.0,
            "r": int(self.radius_x * self.scale_x * 0.85),
            "ry": int(self.radius_y * self.scale_y * 0.85),
            "color": "#10ac84"
        })

    def step_particles(self):
        alive = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 0.06
            if p["type"] == "dust":
                p["vy"] += 0.3   # gravedad
            if p["life"] > 0:
                alive.append(p)
        self.particles = alive


# =========================================================================
# VIEW — Laboratorio gráfico interactivo (Principio 3: Staging)
# =========================================================================
PRINCIPLES = {
    "jump":          {"num": "1,2,6,7",  "name": "Squash & Stretch · Anticipación · Slow In/Out · Arcos",
                      "color": "#00F2FE", "desc": "El Slime comprime su masa, lanza una parábola perfecta y absorbe el impacto al aterrizar."},
    "exaggerate":    {"num": "10,12",    "name": "Exageración · Atractivo",
                      "color": "#FF5555", "desc": "Deformación extrema del eje vertical al 230%. Speed-lines refuerzan el drama visual."},
    "inertia":       {"num": "5,8",      "name": "Follow Through · Acción Secundaria",
                      "color": "#50FA7B", "desc": "Caminata con desfase armónico: antena y pupilas reaccionan con retardo a cada paso."},
    "wave":          {"num": "3,9,11",   "name": "Staging · Timing · Dibujo Sólido",
                      "color": "#BD93F9", "desc": "Saludo con arco completo del brazo. La cámara se organiza para destacar el gesto."},
    "anticipate_run":{"num": "2,4",      "name": "Anticipación · Pose a Pose",
                      "color": "#FFB86C", "desc": "Poses clave: agacharse → arrancar → frenar. Animación pose-a-pose clásica."},
    "dance":         {"num": "5,8,12",   "name": "Overlapping · Sec. Action · Carisma",
                      "color": "#FF79C6", "desc": "Baile con rebote corporal y antena con Follow Through desfasado. Puro carisma."},
}

GROUND_Y   = 430
CANVAS_W   = 600
CANVAS_H   = 620
PANEL_W    = 420
WIN_H      = 680


class DisneyEngineStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Disney 12 Principles — Stop Motion Engine")
        self.root.geometry(f"{CANVAS_W + PANEL_W + 60}x{WIN_H}")
        self.root.configure(bg="#0D0E17")
        self.root.resizable(False, False)

        self.slime = SlimeCharacter(150, GROUND_Y)

        self.time_step    = 0.0
        self.current_action = None
        self.stars        = self._gen_stars(80)
        self.star_tick    = 0

        # Círculos de impacto (efecto visual al aterrizar)
        self.impact_rings = []

        self._build_ui()
        self._animate_background()
        self._sync_view()

    # ------------------------------------------------------------------
    # BACKGROUND — Estrellas flotantes (Staging / Appeal)
    # ------------------------------------------------------------------
    def _gen_stars(self, n):
        return [{"x": random.randint(0, CANVAS_W),
                 "y": random.randint(0, GROUND_Y - 50),
                 "r": random.uniform(0.8, 2.5),
                 "phase": random.uniform(0, 2 * math.pi),
                 "speed": random.uniform(0.02, 0.06)} for _ in range(n)]

    def _animate_background(self):
        self.star_tick += 1
        self.viewport.delete("bg_layer")
        for s in self.stars:
            brightness = int(128 + 100 * math.sin(s["phase"] + self.star_tick * s["speed"]))
            brightness = max(60, min(220, brightness))
            col = f"#{brightness:02x}{brightness:02x}{brightness + 20:02x}"
            self.viewport.create_oval(
                s["x"] - s["r"], s["y"] - s["r"],
                s["x"] + s["r"], s["y"] + s["r"],
                fill=col, outline="", tags="bg_layer")
        self.root.after(50, self._animate_background)

    # ------------------------------------------------------------------
    # UI SETUP
    # ------------------------------------------------------------------
    def _build_ui(self):
        # ── Canvas de render ──────────────────────────────────────────
        self.viewport = tk.Canvas(
            self.root, width=CANVAS_W, height=CANVAS_H,
            bg="#090A12", highlightthickness=2,
            highlightbackground="#1A1C35")
        self.viewport.pack(side=tk.LEFT, padx=(20, 10), pady=20)

        # Suelo con gradiente simulado (líneas superpuestas)
        for i, alpha in enumerate(["#1A1C35", "#141627", "#0F1020", "#090A12"]):
            self.viewport.create_rectangle(
                0, GROUND_Y + 38 + i * 10,
                CANVAS_W, GROUND_Y + 48 + i * 10,
                fill=alpha, outline="", tags="ground")
        self.viewport.create_line(
            0, GROUND_Y + 38, CANVAS_W, GROUND_Y + 38,
            fill="#252847", width=2, tags="ground")

        # ── Panel derecho ─────────────────────────────────────────────
        self.panel = tk.Frame(self.root, bg="#13152A", padx=18, pady=18)
        self.panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True,
                        padx=(0, 20), pady=20)

        # Título
        tk.Label(self.panel,
                 text="🎬 DISNEY ENGINE",
                 fg="#FFFFFF", bg="#13152A",
                 font=("Courier New", 16, "bold")).pack(pady=(0, 2))
        tk.Label(self.panel,
                 text="12 Principios de Animación",
                 fg="#6272A4", bg="#13152A",
                 font=("Courier New", 9)).pack(pady=(0, 14))

        # ── Separador ──
        tk.Frame(self.panel, bg="#252847", height=1).pack(fill=tk.X, pady=(0, 12))

        # ── Slider timing ──
        tk.Label(self.panel,
                 text="⏱  Timing — Delay por cuadro (ms)",
                 fg="#FFB86C", bg="#13152A",
                 font=("Arial", 9, "bold")).pack(anchor="w")
        self.slider_speed = tk.Scale(
            self.panel, from_=8, to=60, orient=tk.HORIZONTAL,
            bg="#13152A", fg="#FFB86C", troughcolor="#252847",
            activebackground="#FFB86C", highlightthickness=0,
            sliderlength=18, bd=0)
        self.slider_speed.set(20)
        self.slider_speed.pack(fill=tk.X, pady=(2, 12))

        # ── Separador ──
        tk.Frame(self.panel, bg="#252847", height=1).pack(fill=tk.X, pady=(0, 12))

        # ── Botones de animación ──
        tk.Label(self.panel,
                 text="▶  Módulos de Animación",
                 fg="#8BE9FD", bg="#13152A",
                 font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 8))

        self._make_btn("🦘  Salto Parabólico",        "jump",           "#00F2FE", "#000")
        self._make_btn("💥  Exageración por Impacto",  "exaggerate",     "#FF5555", "#FFF")
        self._make_btn("🚶  Caminata con Inercia",     "inertia",        "#50FA7B", "#000")
        self._make_btn("👋  Saludo (Staging)",          "wave",           "#BD93F9", "#FFF")
        self._make_btn("🏃  Anticipación → Correr",    "anticipate_run", "#FFB86C", "#000")
        self._make_btn("💃  Baile (Overlapping)",       "dance",          "#FF79C6", "#000")

        # ── Separador ──
        tk.Frame(self.panel, bg="#252847", height=1).pack(fill=tk.X, pady=(12, 10))

        # ── Principio activo ──
        tk.Label(self.panel,
                 text="📖  Principio Activo",
                 fg="#8BE9FD", bg="#13152A",
                 font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 6))

        self.badge_frame = tk.Frame(self.panel, bg="#1E2040",
                                    padx=12, pady=10, bd=0)
        self.badge_frame.pack(fill=tk.X, pady=(0, 8))

        self.lbl_principle_num = tk.Label(
            self.badge_frame, text="—",
            fg="#6272A4", bg="#1E2040",
            font=("Courier New", 11, "bold"))
        self.lbl_principle_num.pack(anchor="w")

        self.lbl_principle_name = tk.Label(
            self.badge_frame, text="Selecciona un módulo",
            fg="#FFFFFF", bg="#1E2040",
            font=("Arial", 9, "bold"), wraplength=340, justify=tk.LEFT)
        self.lbl_principle_name.pack(anchor="w", pady=(2, 4))

        self.lbl_principle_desc = tk.Label(
            self.badge_frame, text="",
            fg="#8892B0", bg="#1E2040",
            font=("Arial", 8), wraplength=340, justify=tk.LEFT)
        self.lbl_principle_desc.pack(anchor="w")

        # ── Barra de progreso ──
        tk.Label(self.panel,
                 text="⚙  Progreso de Animación (Timing)",
                 fg="#8BE9FD", bg="#13152A",
                 font=("Arial", 8)).pack(anchor="w", pady=(4, 4))

        prog_bg = tk.Frame(self.panel, bg="#252847", height=14)
        prog_bg.pack(fill=tk.X, pady=(0, 8))
        prog_bg.pack_propagate(False)
        self.progress_bar = tk.Frame(prog_bg, bg="#00F2FE", height=14, width=0)
        self.progress_bar.place(x=0, y=0, height=14)

        # ── Consola ──
        tk.Label(self.panel,
                 text="📟  Consola de Telemetría",
                 fg="#8BE9FD", bg="#13152A",
                 font=("Arial", 9, "bold")).pack(anchor="w", pady=(4, 4))

        self.console = tk.Text(
            self.panel, height=6, bg="#090A12", fg="#00F2FE",
            font=("Consolas", 9), wrap=tk.WORD, bd=0,
            padx=10, pady=10, state=tk.DISABLED)
        self.console.pack(fill=tk.BOTH, expand=True)
        self._log("🟢 Engine listo. Selecciona un módulo de animación.")

    def _make_btn(self, text, action, bg, fg):
        p = PRINCIPLES.get(action, {})
        btn = tk.Button(
            self.panel, text=text,
            bg=bg, fg=fg,
            font=("Arial", 9, "bold"),
            relief=tk.FLAT, bd=0,
            padx=8, pady=6,
            cursor="hand2",
            activebackground=bg,
            command=lambda a=action: self._start(a))
        btn.pack(fill=tk.X, pady=3)
        # hover glow
        btn.bind("<Enter>", lambda e, b=btn, c=bg: b.config(relief=tk.RIDGE))
        btn.bind("<Leave>", lambda e, b=btn: b.config(relief=tk.FLAT))

    # ------------------------------------------------------------------
    # LOGGING & PROGRESS
    # ------------------------------------------------------------------
    def _log(self, msg):
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.insert(tk.END, f">>> {msg}")
        self.console.config(state=tk.DISABLED)

    def _update_badge(self, action):
        p = PRINCIPLES.get(action)
        if not p:
            return
        col  = p["color"]
        bg_tint = AnimationMath.blend_color(col)   # mezcla válida para tkinter
        self.badge_frame.config(bg=bg_tint)
        self.lbl_principle_num.config(
            text=f"Principio(s) #{p['num']}", fg=col, bg=bg_tint)
        self.lbl_principle_name.config(
            text=p["name"], fg="#FFFFFF", bg=bg_tint)
        self.lbl_principle_desc.config(
            text=p["desc"], fg="#CCCCCC", bg=bg_tint)

    def _clear_badge(self):
        self.badge_frame.config(bg="#1E2040")
        self.lbl_principle_num.config(text="—", fg="#6272A4", bg="#1E2040")
        self.lbl_principle_name.config(text="Selecciona un módulo",
                                       fg="#FFFFFF", bg="#1E2040")
        self.lbl_principle_desc.config(text="", bg="#1E2040")

    def _set_progress(self, t, color="#00F2FE"):
        total_w = self.panel.winfo_width() - 36
        if total_w < 10:
            total_w = PANEL_W - 36
        w = max(0, int(total_w * min(t, 1.0)))
        self.progress_bar.config(width=w, bg=color)
        self.progress_bar.place(x=0, y=0, height=14, width=w)

    # ------------------------------------------------------------------
    # RENDER — Dibuja el personaje y sus partículas cada frame
    # ------------------------------------------------------------------
    def _sync_view(self):
        self.viewport.delete("character_layer")

        rx = self.slime.radius_x * self.slime.scale_x
        ry = self.slime.radius_y * self.slime.scale_y
        vc = self.slime.radius_y - ry          # compensación vertical
        cx = self.slime.x
        cy = self.slime.y + vc

        # ── Impacto: anillos concéntricos ────────────────────────────
        for ring in self.impact_rings[:]:
            ring["r"]    += 5
            ring["alpha"] -= 0.12
            if ring["alpha"] <= 0:
                self.impact_rings.remove(ring)
                continue
            a = int(ring["alpha"] * 255)
            col = f"#{a:02x}{min(242, a+30):02x}{min(254, a+50):02x}"
            self.viewport.create_oval(
                ring["x"] - ring["r"], GROUND_Y + 36,
                ring["x"] + ring["r"], GROUND_Y + 42,
                outline=col, width=2, tags="character_layer")

        # ── Partículas ───────────────────────────────────────────────
        self.slime.step_particles()
        for p in self.slime.particles:
            a = int(p["life"] * 220)
            col = p["color"]
            if p["type"] == "trail":
                # estela translúcida
                op = int(p["life"] * 80)
                outline_col = f"#{op:02x}{min(255,op+30):02x}{op:02x}"
                self.viewport.create_oval(
                    p["x"] - p["r"], p["y"] - p.get("ry", p["r"]),
                    p["x"] + p["r"], p["y"] + p.get("ry", p["r"]),
                    fill="", outline=outline_col, width=2,
                    tags="character_layer")
            elif p["type"] == "speed_line":
                llen = int(p["life"] * 60)
                self.viewport.create_line(
                    p["x"], p["y"], p["x"] + llen, p["y"],
                    fill=col, width=2, tags="character_layer")
            else:
                self.viewport.create_oval(
                    p["x"] - p["r"], p["y"] - p["r"],
                    p["x"] + p["r"], p["y"] + p["r"],
                    fill=col, outline="", tags="character_layer")

        # ── Sombra (Peso / Volumen) ───────────────────────────────────
        dist = max(0, GROUND_Y - self.slime.y)
        shadow_scale = max(0.2, 1 - dist / 300)
        sr = rx * shadow_scale
        self.viewport.create_oval(
            cx - sr, GROUND_Y + 36,
            cx + sr, GROUND_Y + 44,
            fill="#050508", outline="", tags="character_layer")

        # ── Brazo (animación de saludo / wave) ────────────────────────
        if self.slime.show_arm:
            shoulder_x = cx + rx * 0.7
            shoulder_y = cy
            arm_len = 38
            elbow_x  = shoulder_x + math.cos(self.slime.arm_angle) * arm_len
            elbow_y  = shoulder_y - math.sin(self.slime.arm_angle) * arm_len
            hand_x   = elbow_x + math.cos(self.slime.arm_angle + 0.4) * 20
            hand_y   = elbow_y - math.sin(self.slime.arm_angle + 0.4) * 20
            self.viewport.create_line(
                shoulder_x, shoulder_y, elbow_x, elbow_y,
                fill="#0e8f6e", width=8, capstyle=tk.ROUND, tags="character_layer")
            self.viewport.create_line(
                elbow_x, elbow_y, hand_x, hand_y,
                fill="#0e8f6e", width=6, capstyle=tk.ROUND, tags="character_layer")
            self.viewport.create_oval(
                hand_x - 7, hand_y - 7, hand_x + 7, hand_y + 7,
                fill="#1dd1a1", outline="#0e8f6e", width=2,
                tags="character_layer")

        # ── Cuerpo principal (Dibujo Sólido) ─────────────────────────
        self.viewport.create_oval(
            cx - rx, cy - ry, cx + rx, cy + ry,
            fill="#10ac84", outline="#1dd1a1", width=3,
            tags="character_layer")

        # Highlight superior (volumen 3D)
        self.viewport.create_oval(
            cx - rx * 0.65, cy - ry * 0.72,
            cx + rx * 0.15, cy - ry * 0.15,
            fill="#2ee8b5", outline="", tags="character_layer")

        # ── Antena pendular (Acción Secundaria) ───────────────────────
        base_x = cx
        base_y = cy - ry
        end_x  = base_x + math.sin(self.slime.antenna_angle) * self.slime.antenna_length
        end_y  = base_y - math.cos(abs(self.slime.antenna_angle)) * 26
        self.viewport.create_line(
            base_x, base_y, end_x, end_y,
            fill="#ff9f43", width=4, tags="character_layer")
        self.viewport.create_oval(
            end_x - 7, end_y - 7, end_x + 7, end_y + 7,
            fill="#ffee73", outline="#ff9f43", width=2,
            tags="character_layer")

        # ── Expresión facial (Atractivo / Appeal) ─────────────────────
        eye_y   = cy - ry * 0.08 + self.slime.eye_offset_y
        eox     = self.slime.eye_offset_x
        ps      = self.slime.pupil_scale

        # Escleras
        self.viewport.create_oval(
            cx - 23 + eox, eye_y - 10,
            cx -  5 + eox, eye_y + 10,
            fill="#FFFFFF", outline="#0a3d30", width=2, tags="character_layer")
        self.viewport.create_oval(
            cx +  5 + eox, eye_y - 10,
            cx + 23 + eox, eye_y + 10,
            fill="#FFFFFF", outline="#0a3d30", width=2, tags="character_layer")

        # Pupilas reactivas
        pox = eox * 1.15
        pr  = 6 * ps
        self.viewport.create_oval(
            cx - 14 + pox - pr, eye_y - pr,
            cx - 14 + pox + pr, eye_y + pr,
            fill="#050508", tags="character_layer")
        self.viewport.create_oval(
            cx + 14 + pox - pr, eye_y - pr,
            cx + 14 + pox + pr, eye_y + pr,
            fill="#050508", tags="character_layer")

        # Brillos (anime)
        self.viewport.create_oval(
            cx - 17 + pox, eye_y - 6,
            cx - 13 + pox, eye_y - 1,
            fill="#FFFFFF", tags="character_layer")
        self.viewport.create_oval(
            cx + 11 + pox, eye_y - 6,
            cx + 15 + pox, eye_y - 1,
            fill="#FFFFFF", tags="character_layer")

        # Boca dinámica
        my = eye_y + 14
        ms = self.slime.mouth_state
        if ms == "open":
            self.viewport.create_oval(
                cx - 8 + eox, my, cx + 8 + eox, my + 12,
                fill="#ff4757", outline="#0a3d30", width=2,
                tags="character_layer")
        elif ms == "wide":
            self.viewport.create_oval(
                cx - 13 + eox, my - 2, cx + 13 + eox, my + 14,
                fill="#ff2d3a", outline="#0a3d30", width=2,
                tags="character_layer")
        elif ms == "flat":
            self.viewport.create_line(
                cx - 9 + eox, my + 5, cx + 9 + eox, my + 5,
                fill="#0a3d30", width=3, tags="character_layer")
        elif ms == "sad":
            self.viewport.create_arc(
                cx - 9 + eox, my + 2, cx + 9 + eox, my + 12,
                start=0, extent=180, style=tk.ARC,
                outline="#0a3d30", width=3, tags="character_layer")
        else:  # smile
            self.viewport.create_arc(
                cx - 9 + eox, my, cx + 9 + eox, my + 10,
                start=0, extent=-180, style=tk.ARC,
                outline="#0a3d30", width=3, tags="character_layer")

    # ------------------------------------------------------------------
    # ENGINE CORE — Controlador de física y estados
    # ------------------------------------------------------------------
    def _start(self, action):
        if self.current_action is not None:
            return
        self.current_action = action
        self.time_step = 0.0
        self.slime.reset()
        self.impact_rings.clear()
        self._update_badge(action)
        self._set_progress(0, PRINCIPLES[action]["color"])
        self._run()

    def _run(self):
        if self.current_action is None:
            return

        self.time_step += 0.022
        t = self.time_step

        color = PRINCIPLES.get(self.current_action, {}).get("color", "#00F2FE")

        if t > 1.0:
            self._finish()
            return

        self._set_progress(t, color)

        # ── MÓDULO 1: SALTO PARABÓLICO ────────────────────────────────
        if self.current_action == "jump":
            if t < 0.18:                        # Anticipación (P2)
                lt = AnimationMath.ease_in_out(t / 0.18)
                self.slime.squash_stretch(1 + 0.38 * lt, 1 - 0.38 * lt)
                self.slime.antenna_angle = -0.35 * lt
                self.slime.eye_offset_y  =  8 * lt
                self.slime.mouth_state   = "flat"
                self._log("[P2 – Anticipación] El Slime comprime su masa para acumular impulso vertical.")

            elif t < 0.75:                      # Vuelo parabólico (P1,7)
                lt = (t - 0.18) / 0.57
                eased = AnimationMath.ease_in_out(lt)
                self.slime.x, self.slime.y = AnimationMath.arc_trajectory(
                    150, GROUND_Y, 460, GROUND_Y, 280, eased)
                if lt < 0.5:                    # Subida — Stretch
                    s  = AnimationMath.ease_out(lt * 2)
                    self.slime.squash_stretch(0.72 - 0.05 * s, 1.40 + 0.05 * s)
                    self.slime.antenna_angle = 0.55
                    self.slime.eye_offset_y  = -7
                    self.slime.mouth_state   = "open"
                    self.slime.emit_trail()
                    self._log("[P1,7 – Stretch & Arcs] Estiramiento vertical. La trayectoria sigue una parábola perfecta.")
                else:                           # Bajada — vuelve a squash
                    s  = AnimationMath.ease_in((lt - 0.5) * 2)
                    self.slime.squash_stretch(0.78 + 0.10 * s, 1.32 - 0.10 * s)
                    self.slime.antenna_angle = -0.50
                    self.slime.eye_offset_y  =  8
                    self.slime.mouth_state   = "flat"
                    self._log("[P6 – Slow In/Out] Gravedad acelera la caída desde el ápice.")

            else:                               # Impacto + Follow Through (P5)
                lt = (t - 0.75) / 0.25
                self.slime.x, self.slime.y = 460, GROUND_Y
                bounce = math.sin(lt * math.pi)
                sx = 1.45 - 0.45 * lt
                sy = 0.58 + 0.42 * lt
                self.slime.squash_stretch(sx, sy)
                self.slime.antenna_angle = 0.9 * (1 - lt)
                self.slime.mouth_state   = "smile"
                if lt < 0.15:
                    self.slime.emit_dust(10)
                    self.impact_rings.append({"x": 460, "r": 5, "alpha": 1.0})
                self._log("[P5 – Follow Through] La antena oscila después del impacto: inercia residual.")

        # ── MÓDULO 2: EXAGERACIÓN ─────────────────────────────────────
        elif self.current_action == "exaggerate":
            if t < 0.25:                        # Pre-impacto sutil
                lt = AnimationMath.ease_in(t / 0.25)
                self.slime.squash_stretch(0.9 - 0.1 * lt, 1.1 + 0.1 * lt)
                self.slime.eye_offset_x = -8 * lt
                self.slime.mouth_state  = "flat"
                self._log("[Pre-impacto] Ligera inclinación antes del choque...")

            elif t < 0.68:                      # EXAGERACIÓN máxima (P10)
                lt = (t - 0.25) / 0.43
                self.slime.squash_stretch(0.22 + 0.08 * math.sin(lt * 12),
                                          2.45 - 0.15 * math.sin(lt * 12))
                self.slime.y = GROUND_Y - 160
                self.slime.antenna_angle = math.sin(t * 55) * 1.1
                self.slime.eye_offset_y  = -16
                self.slime.mouth_state   = "wide"
                self.slime.emit_speed_lines(4)
                self.slime.emit_sparkle(3)
                self.impact_rings.append({"x": self.slime.x, "r": 3, "alpha": 0.8})
                self._log("[P10 – Exageración] Estiramiento al 245% del eje Y. Speed-lines refuerzan el impacto.")

            else:                               # Vuelta al reposo (P12)
                lt = AnimationMath.elastic_out((t - 0.68) / 0.32)
                sx = AnimationMath.lerp(0.22, 1.0, lt)
                sy = AnimationMath.lerp(2.45, 1.0, lt)
                self.slime.squash_stretch(sx, sy)
                self.slime.y = AnimationMath.lerp(GROUND_Y - 160, GROUND_Y, lt)
                self.slime.mouth_state = "smile"
                self._log("[P12 – Atractivo] Regreso elástico al Idle carismático.")

        # ── MÓDULO 3: CAMINATA CON INERCIA ───────────────────────────
        elif self.current_action == "inertia":
            self.slime.x = 150 + t * 300
            wave = math.sin(t * math.pi * 5)
            self.slime.y = GROUND_Y - abs(wave) * 28
            bob  = abs(wave)

            # Squash en contacto, stretch en el aire
            if bob < 0.15:
                self.slime.squash_stretch(1.25, 0.78)
                self.slime.emit_dust(3)
            else:
                self.slime.squash_stretch(0.85, 1.18)

            # Overlapping: antena y ojos con retraso (P5)
            self.slime.antenna_angle = -math.cos(t * math.pi * 5) * 0.7
            self.slime.eye_offset_x  =  6 if wave > 0 else -4
            self.slime.mouth_state   = "open" if 0.45 < t < 0.55 else "smile"
            self.slime.emit_trail()
            self._log("[P5,8 – Overlapping & Secondary Action] Antena y pupilas calculan retardo harmónico respecto al core.")

        # ── MÓDULO 4: SALUDO — WAVE ───────────────────────────────────
        elif self.current_action == "wave":
            self.slime.show_arm = True
            self.slime.x = 300
            self.slime.y = GROUND_Y

            if t < 0.15:                        # Anticipación del brazo (P2)
                lt = AnimationMath.ease_in_out(t / 0.15)
                self.slime.arm_angle   = AnimationMath.lerp(0.3, -0.2, lt)
                self.slime.mouth_state = "smile"
                self._log("[P2,3 – Staging & Anticipación] El brazo baja primero para dar impulso al saludo.")

            elif t < 0.70:                      # Arco del saludo (P7,9)
                lt  = (t - 0.15) / 0.55
                arc = math.sin(lt * math.pi * 3) * 1.1
                self.slime.arm_angle   = arc + 0.5
                self.slime.antenna_angle = math.sin(lt * math.pi * 3) * 0.4
                self.slime.eye_offset_x  = 5 if math.sin(lt * math.pi * 2) > 0 else -5
                bob = math.sin(lt * math.pi * 3) * 0.12
                self.slime.squash_stretch(1 - bob, 1 + bob)
                self.slime.mouth_state = "open"
                self._log("[P7,9 – Arcos & Timing] El brazo describe un arco natural. El timing define la energía del saludo.")

            else:                               # Regreso suave (P11)
                lt = AnimationMath.ease_out((t - 0.70) / 0.30)
                self.slime.arm_angle   = AnimationMath.lerp(0.5, 0.0, lt)
                self.slime.antenna_angle = AnimationMath.lerp(0.4, 0.0, lt)
                self.slime.squash_stretch(1.0, 1.0)
                self.slime.mouth_state = "smile"
                self._log("[P11 – Dibujo Sólido] El brazo regresa con suavidad manteniendo el volumen tridimensional.")

        # ── MÓDULO 5: ANTICIPACIÓN → CORRER ──────────────────────────
        elif self.current_action == "anticipate_run":
            # Poses clave (Pose-to-Pose, P4):
            #   Pose 0 (t=0.00): reposo
            #   Pose 1 (t=0.20): agacharse (anticipación)
            #   Pose 2 (t=0.30): arranque explosivo (stretch extremo)
            #   Pose 3 (t=0.75): carrera (cuerpo inclinado)
            #   Pose 4 (t=1.00): freno (squash de parada)

            if t < 0.20:                        # POSE 1 — Anticipación (P2)
                lt = AnimationMath.ease_in_out(t / 0.20)
                self.slime.squash_stretch(1.30 + 0.10 * lt, 0.62 - 0.08 * lt)
                self.slime.eye_offset_y  = 10 * lt
                self.slime.mouth_state   = "flat"
                self.slime.antenna_angle = -0.5 * lt
                self._log("[P2,4 – Anticipación Pose 1] Agacharse: acumulación de energía antes del arranque.")

            elif t < 0.30:                      # POSE 2 — Arranque explosivo
                lt = AnimationMath.ease_out((t - 0.20) / 0.10)
                self.slime.squash_stretch(0.55, 1.60)
                self.slime.x = AnimationMath.lerp(150, 200, lt)
                self.slime.y = AnimationMath.lerp(GROUND_Y, GROUND_Y - 40, lt)
                self.slime.eye_offset_y  = -12
                self.slime.mouth_state   = "open"
                self.slime.antenna_angle =  0.8
                self.slime.emit_dust(12)
                self.impact_rings.append({"x": 150, "r": 5, "alpha": 1.0})
                self._log("[P4 – Pose a Pose] Arranque: de la pose de agacharse a stretch máximo en 1 cuadro.")

            elif t < 0.78:                      # POSE 3 — Carrera (P5)
                lt = (t - 0.30) / 0.48
                eased = AnimationMath.ease_in_out(lt)
                self.slime.x = AnimationMath.lerp(200, 480, eased)
                self.slime.y = GROUND_Y - abs(math.sin(lt * math.pi * 4)) * 30
                cycle = math.sin(lt * math.pi * 4)
                self.slime.squash_stretch(0.80 + 0.10 * abs(cycle), 1.20 - 0.10 * abs(cycle))
                self.slime.antenna_angle = -cycle * 0.65
                self.slime.eye_offset_x  =  8
                self.slime.mouth_state   = "open"
                self.slime.emit_trail()
                self._log("[P5,8 – Carrera] Zancadas con desfase de antena: secondary action clásica.")

            else:                               # POSE 4 — Freno (P6, Follow Through)
                lt = AnimationMath.ease_out((t - 0.78) / 0.22)
                self.slime.x = 480
                self.slime.y = GROUND_Y
                sx = AnimationMath.lerp(0.80, 1.45, lt)
                sy = AnimationMath.lerp(1.20, 0.62, lt)
                self.slime.squash_stretch(sx, sy)
                self.slime.antenna_angle = AnimationMath.lerp(-0.65, 0.0,
                                              AnimationMath.elastic_out(lt))
                self.slime.eye_offset_x  = 0
                self.slime.mouth_state   = "flat"
                if lt < 0.12:
                    self.slime.emit_dust(15)
                    self.impact_rings.append({"x": 480, "r": 5, "alpha": 1.0})
                self._log("[P6 – Slow-Out Freno] Squash de parada: el Slime absorbe la inercia al detenerse.")

        # ── MÓDULO 6: BAILE OVERLAPPING ───────────────────────────────
        elif self.current_action == "dance":
            # El cuerpo rebota en 4/4; antena en 3/4 (desfase)
            # Ojos siguen un compás distinto → Overlapping Action (P5)
            body_phase   = t * math.pi * 6
            ant_phase    = t * math.pi * 4.5   # desfasado
            eye_phase    = t * math.pi * 7.5   # más rápido

            # Rebote corporal
            bounce = abs(math.sin(body_phase))
            self.slime.y = GROUND_Y - bounce * 38
            sx = 0.95 + 0.12 * (1 - bounce)
            sy = 0.98 + 0.14 * bounce
            self.slime.squash_stretch(sx, sy)

            # Desplazamiento lateral suave (Principio 12 — Carisma)
            self.slime.x = 300 + math.sin(t * math.pi * 3) * 55

            # Antena con Follow Through desfasado (P5)
            self.slime.antenna_angle = math.sin(ant_phase) * 0.85

            # Ojos con Overlapping más rápido (P8)
            self.slime.eye_offset_x = math.sin(eye_phase) * 6
            self.slime.eye_offset_y = math.cos(eye_phase) * 4

            # Boca alterna con el ritmo
            self.slime.mouth_state = "open" if math.sin(body_phase) > 0.7 else "smile"

            # Partículas de brillo en el peak del salto
            if bounce > 0.9 and random.random() < 0.4:
                self.slime.emit_sparkle(3)

            # Squash al tocar suelo
            if self.slime.y >= GROUND_Y - 5 and bounce < 0.1:
                self.slime.emit_dust(5)

            self._log(f"[P5,8,12 – Dance] Cuerpo:{body_phase:.1f}rad | Antena:{ant_phase:.1f}rad | Ojos:{eye_phase:.1f}rad — Overlapping puro.")

        self._sync_view()
        self.root.after(self.slider_speed.get(), self._run)

    def _finish(self):
        self.slime.reset()
        self.current_action = None
        self._sync_view()
        self._set_progress(0, "#00F2FE")
        self._clear_badge()
        self._log("✅ Ciclo completado. Personaje en estado Idle. Selecciona otro módulo.")


if __name__ == "__main__":
    root = tk.Tk()
    root.tk.call("tk", "scaling", 1.3)
    engine = DisneyEngineStudio(root)
    root.mainloop()