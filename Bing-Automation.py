import time
import random
import pyautogui
import threading
import tkinter as tk
from tkinter import messagebox
import json
import os
import requests

# =========================
# GROQ API CONFIG
# =========================
GROQ_API_KEYS = [

   " key 1 "
   " key 2 "
   " key 3 "
    

]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"
HISTORY_FILE = "history.json"

current_key_index = 0

# =========================
# Profile coordinates
# =========================

profiles = {

    "Kalex":   (326, 276),
    "Miles":   (499, 283),
    "Beckett": (666, 283),
    "Caleb":   (827, 284),
    "Asher":   (992, 284)
}

search_bar_coords = {
   "Kalex":   (792, 111),
    "Miles":   (772, 186),
    "Beckett": (786, 188),
    "Caleb":   (767, 186),
    "Asher":   (846, 109)
}

close_x, close_y = 1881, 17
folder_open      = (44, 42)
folder_close     = (1879, 15)



def shutdown():
    pyautogui.doubleClick(1846, 203)
    time.sleep(2)
    pyautogui.doubleClick(661, 285)
    time.sleep(2)

# =========================
# GENRE SETS
# =========================
GENRE_SETS = {
    "Set 1": [
        "Artificial Intelligence", "Machine Learning", "Cybersecurity",
        "Cloud Computing", "Blockchain Technology", "Data Science",
        "Internet of Things", "Augmented Reality", "Quantum Computing",
        "Web Development"
    ],
    "Set 2": [
        "Fitness & Nutrition", "Mental Health", "Yoga & Meditation",
        "Weight Loss", "Healthy Eating", "Running & Marathon",
        "Home Workouts", "Sleep Health", "Stress Management",
        "Plant Based Diet"
    ],
    "Set 3": [
        "Travel Photography", "Budget Travel", "Solo Travel",
        "Luxury Destinations", "Road Trips", "Backpacking",
        "Cultural Tourism", "Adventure Travel", "Beach Destinations",
        "City Breaks"
    ],
    "Set 4": [
        "Personal Finance", "Stock Market", "Cryptocurrency",
        "Real Estate Investing", "Retirement Planning", "Budgeting Tips",
        "Side Hustles", "Passive Income", "Tax Planning",
        "Debt Management"
    ],
    "Set 5": [
        "Home Cooking", "Baking & Pastry", "Vegan Recipes",
        "Quick Meals", "Mediterranean Diet", "Street Food",
        "Meal Prep", "Food Photography", "Restaurant Reviews",
        "International Cuisine"
    ],
    "Set 6": [
        "Interior Design", "Minimalist Living", "Home Organization",
        "DIY Home Projects", "Sustainable Living", "Smart Home",
        "Gardening", "Home Renovation", "Furniture Design",
        "Small Space Living"
    ],
    "Set 7": [
        "Online Learning", "Study Techniques", "Career Development",
        "Public Speaking", "Leadership Skills", "Time Management",
        "Productivity Hacks", "Remote Work", "Freelancing",
        "Job Interview Tips"
    ],
    "Set 8": [
        "Skincare Routine", "Hair Care", "Fashion Trends",
        "Sustainable Fashion", "Makeup Tutorials", "Mens Grooming",
        "Anti Aging Tips", "Natural Beauty", "Perfume & Fragrance",
        "Nail Art"
    ],
    "Set 9": [
        "Parenting Tips", "Child Development", "Homeschooling",
        "Family Activities", "Pregnancy & Birth", "Toddler Care",
        "Teen Parenting", "Special Needs Parenting", "Family Travel",
        "Educational Toys"
    ],
    "Set 10": [
        "Gaming & Esports", "Movie Reviews", "Music Production",
        "Podcast Creation", "Digital Art", "Photography Tips",
        "Book Reviews", "Anime & Manga", "Stand Up Comedy",
        "Film Making"
    ]
}

# =========================
# PERCENTAGE RANGES (NEW)
# =========================
PERCENT_RANGES = {
    "10%":  (1,  2),
    "20%":  (6,  9),
    "30%":  (9,  12),
    "40%":  (12, 16),
    "50%":  (15, 19),
    "60%":  (18, 21),
    "75%":  (23, 28),
    "90%":  (27, 31),
    "100%": (30, 37),
    "120%": (34, 39),
    "150%": (40, 45),
}

PERCENT_OPTIONS = ["10%", "20%", "30%", "40%", "50%", "60%", "75%", "90%", "100%", "120%", "150%"]

# =========================
# HISTORY MANAGEMENT
# =========================
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def get_all_used_topics(history):
    all_topics = []
    for set_name, genres in history.items():
        for genre, topics in genres.items():
            all_topics.extend(topics)
    return all_topics

def add_topic_to_history(history, set_name, genre, topic):
    if set_name not in history:
        history[set_name] = {}
    if genre not in history[set_name]:
        history[set_name][genre] = []
    history[set_name][genre].append(topic)
    save_history(history)

# =========================
# GROQ API CALLS
# =========================
def groq_call(prompt):
    global current_key_index

    for attempt in range(len(GROQ_API_KEYS)):
        key = GROQ_API_KEYS[current_key_index]
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.9,
            "max_tokens": 3000
        }
        try:
            response = requests.post(GROQ_API_URL, headers=headers, json=body, timeout=30)

            if response.status_code == 429:
                print(f"[Key {current_key_index + 1}] Rate limit hit — switching to next key...")
                current_key_index = (current_key_index + 1) % len(GROQ_API_KEYS)
                time.sleep(1)
                continue

            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                current_key_index = (current_key_index + 1) % len(GROQ_API_KEYS)
                time.sleep(1)
                continue
            raise e

    raise Exception("All 3 Groq API keys have hit their rate limit. Please wait and try again.")

def generate_topic(genre, used_topics_same_set):
    used_str = ", ".join(used_topics_same_set) if used_topics_same_set else "None"
    prompt = f"""Generate ONE very specific, detailed topic related to the genre: "{genre}".

RULES:
1. Must be a specific niche topic, NOT just the genre name itself.
2. Example: Genre "Artificial Intelligence" → Topic "AI-powered diagnostic tools used in remote healthcare clinics"
3. Must be completely different from these already used topics: {used_str}
4. Return ONLY the topic name. No explanation, no quotes, no extra text."""

    result = groq_call(prompt)
    return result.strip().strip('"').strip("'")

def check_topic_similarity(new_topic, used_topics_same_set):
    if not used_topics_same_set:
        return False
    used_str = "\n".join(used_topics_same_set)
    prompt = f"""Is the topic "{new_topic}" similar in meaning or subject to any of these topics?

{used_str}

Answer with ONLY "YES" or "NO". Nothing else."""
    result = groq_call(prompt).strip().upper()
    return "YES" in result

def generate_keywords(topic, count):
    prompt = f"""Generate {count} unique, human-like search keywords strictly related to: "{topic}".

RULES:
1. Each keyword must be 5-8 words long.
2. Must sound like real human search queries people type in search engines.
3. High linguistic variety — different starting words each time.
4. No duplicates.

Return ONLY a JSON array of strings. No markdown, no explanation, just the array."""

    try:
        result   = groq_call(prompt)
        cleaned  = result.replace("```json", "").replace("```", "").strip()
        keywords = json.loads(cleaned)
        seen = []
        for k in keywords:
            if k not in seen:
                seen.append(k)
        return seen[:count]
    except Exception as e:
        print(f"[Keyword Gen Error] {e}")
        return []

# =========================
# SESSION GENRE TRACKING
# =========================
session_used_genres = set()

def get_random_genre(set_name):
    genres = GENRE_SETS[set_name]
    available = [g for g in genres if g not in session_used_genres]
    if not available:
        session_used_genres.clear()
        available = genres
    genre = random.choice(available)
    session_used_genres.add(genre)
    return genre

# =========================
# HOLD APPROACHES
# =========================
HOLD_APPROACHES = [
    (4, 6), (5, 8), (10, 14), (15, 20),
    (21, 25), (26, 31), (32, 36), (37, 40)
]

hold_cycle_state = {}

def post_search_hold(profile_name):
    if profile_name not in hold_cycle_state or not hold_cycle_state[profile_name]:
        cycle = HOLD_APPROACHES.copy()
        random.shuffle(cycle)
        hold_cycle_state[profile_name] = cycle
    low, high = hold_cycle_state[profile_name].pop(0)
    time.sleep(random.uniform(low, high))

# =========================
# SCROLL APPROACHES
# =========================
SCROLL_PAUSE_SECONDS = 2

SCROLL_TIME_MAP = {
    "10_15": (2, 3), "25_35": (3, 4), "35_45": (3, 3),
    "40_45": (3, 3), "50": (3, 4), "100": (5, 6)
}

SCROLL_APPROACHES = [
    [("down", "10_15")],
    [("down", "25_35")],
    [("down", "40_45")],
    [("down", "10_15"), ("pause", None), ("down", "10_15"), ("pause", None)],
    [("down", "25_35"), ("pause", None), ("down", "25_35"), ("pause", None), ("down", "25_35")],
    [("down", "25_35"), ("up", "10_15"), ("down", "25_35"), ("up", "10_15")],
    [("down", "50"), ("up", "10_15"), ("down", "50"), ("up", "10_15")],
    [("down", "50"), ("pause", None)],
    [("down", "100"), ("up", "100")],
    [("down", "50"), ("down", "25_35")]
]

scroll_cycle_state = {}

def _scroll_amount(percent):
    screen_h = pyautogui.size().height
    return int(screen_h * (percent / 100.0))

def _scroll_step(direction, percent_key):
    if percent_key == "10_15":   pct = random.uniform(10, 15)
    elif percent_key == "25_35": pct = random.uniform(25, 35)
    elif percent_key == "35_45": pct = random.uniform(35, 45)
    elif percent_key == "40_45": pct = random.uniform(40, 45)
    elif percent_key == "50":    pct = 50
    elif percent_key == "100":   pct = 100
    else: return

    t_low, t_high = SCROLL_TIME_MAP[percent_key]
    duration = random.uniform(t_low, t_high)
    steps = max(1, int(duration * 10))
    amount = _scroll_amount(pct) // steps
    for _ in range(steps):
        pyautogui.scroll(amount if direction == "up" else -amount)
        time.sleep(duration / steps)

def _scroll_to_top_fast():
    steps = 20
    for _ in range(steps):
        pyautogui.scroll(5000)
        time.sleep(0.1)
    time.sleep(0.3)

def post_search_scroll(profile_name):
    if profile_name not in scroll_cycle_state or not scroll_cycle_state[profile_name]:
        cycle = SCROLL_APPROACHES.copy()
        random.shuffle(cycle)
        scroll_cycle_state[profile_name] = cycle
    approach = scroll_cycle_state[profile_name].pop(0)
    for action, key in approach:
        if action == "pause":
            time.sleep(SCROLL_PAUSE_SECONDS)
        else:
            _scroll_step(action, key)
    _scroll_to_top_fast()

# =========================
# Typing logic
# =========================
def type_query(query, is_first_search, profile_name):
    pause_event.wait()
    if not is_first_search:
        x, y = search_bar_coords[profile_name]
        pyautogui.click(x, y)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.15)
        pyautogui.press("delete")
        time.sleep(0.2)

    for letter in query:
        pause_event.wait()
        pyautogui.write(letter, interval=random.uniform(0.1, 0.3))

    pyautogui.press("enter")
    time.sleep(random.uniform(3, 6))
    post_search_hold(profile_name)
    post_search_scroll(profile_name)

# =========================
# COUNTDOWN TIMER
# =========================
def run_countdown(seconds):
    for remaining in range(seconds, 0, -1):
        root.after(0, lambda r=remaining: timer_label.config(
            text=f"Next account in: {r}s"
        ))
        time.sleep(1)
    root.after(0, lambda: timer_label.config(text=""))

# =========================
# Runtime flags
# =========================
running        = False
paused         = False
pause_event    = threading.Event()
pause_event.set()
selected_profiles = {}
selected_topic_set = list(GENRE_SETS.keys())[0]

# =========================
# MAIN GRIND FUNCTION
# =========================
def grind_points(sel_profiles, auto_mode=False, auto_count=10, percent_mode=False, percent_key="100%"):
    global running
    history = load_history()

    profile_list = list(profiles.keys()) if (auto_mode or percent_mode) else list(sel_profiles.keys())
    random.shuffle(profile_list)

    session_topics = {}

    for i, profile in enumerate(profile_list):
        pause_event.wait()
        if not running:
            break

        # --- Determine search count for this profile ---
        if percent_mode:
            low, high = PERCENT_RANGES[percent_key]
            search_count = random.randint(low, high)
        elif auto_mode:
            search_count = auto_count
        else:
            search_count = sel_profiles.get(profile, 12)

        set_name = selected_topic_set
        genre    = get_random_genre(set_name)

        history_genre_topics = []
        if set_name in history and genre in history[set_name]:
            history_genre_topics = history[set_name][genre]
        session_genre_topics = session_topics.get(genre, [])
        same_genre_topics = history_genre_topics + session_genre_topics

        root.after(0, lambda g=genre, p=profile: status_label.config(
            text=f"[{p}] Generating topic for: {g}..."
        ))

        topic = None
        for attempt in range(5):
            candidate = generate_topic(genre, same_genre_topics)
            is_similar = check_topic_similarity(candidate, same_genre_topics)
            if not is_similar:
                topic = candidate
                break
            time.sleep(2)

        if not topic:
            topic = generate_topic(genre, same_genre_topics)

        if genre not in session_topics:
            session_topics[genre] = []
        session_topics[genre].append(topic)

        root.after(0, lambda t=topic, p=profile, c=search_count: status_label.config(
            text=f"[{p}] Generating {c} keywords for: {t[:40]}..."
        ))

        keywords = generate_keywords(topic, search_count)

        if len(keywords) < search_count:
            extra    = generate_keywords(topic, search_count - len(keywords))
            keywords = list(dict.fromkeys(keywords + extra))[:search_count]

        add_topic_to_history(history, set_name, genre, topic)
        root.after(0, update_dashboard)

        kw_pool = keywords.copy()
        random.shuffle(kw_pool)
        used_kw = set()

        root.after(0, lambda p=profile, t=topic: status_label.config(
            text=f"Searching [{p}] — {t[:40]}..."
        ))

        pyautogui.doubleClick(folder_open[0], folder_open[1])
        time.sleep(4)

        pyautogui.doubleClick(profiles[profile][0], profiles[profile][1])
        time.sleep(5)

        search_counter = 0

        for j in range(search_count):
            pause_event.wait()
            if not running:
                break

            available = [k for k in kw_pool if k not in used_kw]
            if not available:
                used_kw.clear()
                available = kw_pool

            query = available[0]
            used_kw.add(query)

            is_first_search = (search_counter == 0)
            type_query(query, is_first_search, profile)
            search_counter += 1

        pyautogui.click(close_x, close_y)
        time.sleep(2)

        pyautogui.click(folder_close[0], folder_close[1])
        time.sleep(2)

        is_last = (i == len(profile_list) - 1)

        if is_last:
            shutdown()
        else:
            wait_sec = random.randint(10, 25)
            run_countdown(wait_sec)

    root.after(0, lambda: status_label.config(text="Done!"))
    running = False

# =========================
# GUI FUNCTIONS
# =========================
def start_grind():
    global running, selected_profiles, selected_topic_set, paused
    running = True
    paused  = False
    pause_event.set()
    selected_profiles.clear()
    selected_topic_set = topic_var.get()

    # Percent mode takes priority check
    if percent_auto_var.get():
        chosen_percent = percent_var.get()
        threading.Thread(target=grind_points, args=({}, False, 10, True, chosen_percent), daemon=True).start()
        return

    if auto_search_var.get():
        try:
            count = int(auto_count_var.get())
            threading.Thread(target=grind_points, args=({}, True, count), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number for Auto Search!")
        return

    for profile, var in checkboxes.items():
        if var[0].get():
            try:
                search_count = int(var[1].get())
                selected_profiles[profile] = search_count if search_count > 0 else 12
            except ValueError:
                selected_profiles[profile] = 12

    if not selected_profiles:
        messagebox.showerror("Error", "Please select at least one profile!")
        return

    threading.Thread(target=grind_points, args=(selected_profiles,), daemon=True).start()

def stop_grind():
    global running, paused
    running = False
    paused  = False
    pause_event.set()

def toggle_pause():
    global paused
    if not running:
        return
    if not paused:
        paused = True
        pause_event.clear()
        pause_button.config(text="Resume", bg="red")
    else:
        paused = False
        pause_event.set()
        pause_button.config(text="Pause", bg="yellow")

def update_dashboard():
    history = load_history()
    total   = sum(len(t) for genres in history.values() for t in genres.values())
    total_label.config(text=f"Total Topics Generated: {total}")

def show_history():
    history = load_history()
    win = tk.Toplevel(root)
    win.title("Topic History")
    win.geometry("520x600")

    text = tk.Text(win, font=("Courier", 10), wrap="word")
    sb   = tk.Scrollbar(win, command=text.yview)
    text.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    text.pack(fill="both", expand=True, padx=10, pady=10)

    grand_total = 0
    for set_name, genres in history.items():
        set_total = sum(len(t) for t in genres.values())
        grand_total += set_total
        text.insert("end", f"\n{'='*45}\n{set_name}  [{set_total} topics]\n{'='*45}\n")
        for genre, topics in genres.items():
            text.insert("end", f"\n  [{genre}] — {len(topics)} topic(s)\n")
            for t in topics:
                text.insert("end", f"    • {t}\n")

    text.insert("1.0", f"GRAND TOTAL TOPICS: {grand_total}\n\n")
    text.config(state="disabled")

# =========================
# GUI SETUP
# =========================
root = tk.Tk()
root.title("Bing Auto Search")
root.geometry("500x900")

dash_frame = tk.Frame(root, bg="#1e1e1e", pady=8)
dash_frame.pack(fill="x")
total_label = tk.Label(
    dash_frame, text="Total Topics Generated: 0",
    font=("Arial", 11, "bold"), bg="#1e1e1e", fg="white"
)
total_label.pack()

history_btn = tk.Button(
    root, text="View History", command=show_history,
    font=("Arial", 10), bg="#333333", fg="white"
)
history_btn.pack(pady=4)

status_label = tk.Label(
    root, text="Idle — Press Start",
    font=("Arial", 9), fg="#555555", wraplength=460
)
status_label.pack(pady=2)

timer_label = tk.Label(
    root, text="",
    font=("Arial", 10, "bold"), fg="#FF8C00"
)
timer_label.pack(pady=2)

pause_button = tk.Button(root, text="Pause",  command=toggle_pause, font=("Arial", 12), bg="yellow")
pause_button.pack(pady=5)

start_button = tk.Button(root, text="Start",  command=start_grind,  font=("Arial", 12), bg="green", fg="white")
start_button.pack(pady=10)

stop_button  = tk.Button(root, text="Stop",   command=stop_grind,   font=("Arial", 12), bg="red",   fg="white")
stop_button.pack(pady=10)

# --- Auto Search All Profiles (existing) ---
auto_frame       = tk.Frame(root)
auto_frame.pack(pady=5)
auto_search_var  = tk.BooleanVar()
auto_count_var   = tk.StringVar()
tk.Checkbutton(auto_frame, text="Auto Search (All Profiles)", variable=auto_search_var).pack(side="left")
tk.Entry(auto_frame, textvariable=auto_count_var, width=5).pack(side="left", padx=5)

# --- Percentage Auto Search (NEW) ---
percent_frame    = tk.Frame(root)
percent_frame.pack(pady=5)
percent_auto_var = tk.BooleanVar()
percent_var      = tk.StringVar(value="100%")
tk.Checkbutton(percent_frame, text="Percentage Auto Search", variable=percent_auto_var).pack(side="left")
percent_dropdown = tk.OptionMenu(percent_frame, percent_var, *PERCENT_OPTIONS)
percent_dropdown.pack(side="left", padx=5)

topic_var = tk.StringVar()
topic_var.set(list(GENRE_SETS.keys())[0])
topic_frame = tk.Frame(root)
topic_frame.pack(pady=10)
tk.Label(topic_frame, text="Select Set:").pack(side="left", padx=5)
tk.OptionMenu(topic_frame, topic_var, *GENRE_SETS.keys()).pack(side="left")

canvas           = tk.Canvas(root)
scrollbar        = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

checkboxes = {}
for profile in profiles.keys():
    var              = tk.BooleanVar()
    search_count_var = tk.StringVar()
    checkboxes[profile] = (var, search_count_var)
    row = tk.Frame(scrollable_frame)
    row.pack(anchor="w", padx=5, pady=2)
    tk.Checkbutton(row, text=profile, variable=var).pack(side="left")
    tk.Entry(row, textvariable=search_count_var, width=5).pack(side="left", padx=5)

update_dashboard()
root.mainloop()