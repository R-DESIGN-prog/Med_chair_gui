import streamlit as st

st.set_page_config(page_title="Medical Chair", layout="centered", initial_sidebar_state="collapsed")

# --- Session state defaults ---
defaults = {
    "screen": "welcome",
    "height": 178,
    "disclaimers": {"no_piercings": False, "no_pacemaker": False, "no_implants": False, "no_phone": False},
    "treatment": None,
    "treatment_running": False,
    "treatment_paused": False,
    "time_remaining": 15,
    "power_all": 5,
    "power_zones": {"S": 5, "L_upper": 5, "B_upper": 5, "R_upper": 5, "L_lower": 5, "B_lower": 5, "R_lower": 5},
    "coil": {"L": 0, "B": 0, "R": 0},
    "sound_source": None,
    "volume": 5,
    "chair": {"backrest": 0, "seat": 0, "footrest": 0, "height": 0},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- Helpers ---
def go(screen):
    st.session_state.screen = screen

def treatment_header():
    if st.session_state.treatment_running or st.session_state.treatment_paused:
        trt = st.session_state.treatment or "—"
        mins = st.session_state.time_remaining
        status = "⏸ PAUSED" if st.session_state.treatment_paused else "▶ RUNNING"
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
        with col1:
            st.markdown(f"**{trt}** &nbsp; {status}")
        with col2:
            if not st.session_state.treatment_paused:
                if st.button("⏸", key="hdr_pause"):
                    st.session_state.treatment_paused = True
                    st.session_state.treatment_running = False
            else:
                if st.button("▶", key="hdr_resume"):
                    st.session_state.treatment_paused = False
                    st.session_state.treatment_running = True
        with col3:
            if st.button("⏹", key="hdr_stop"):
                st.session_state.treatment_running = False
                st.session_state.treatment_paused = False
                st.session_state.treatment = None
        with col4:
            st.markdown(f"**{mins} min remaining**")
        st.divider()

def bottom_nav():
    st.divider()
    cols = st.columns(6)
    buttons = [
        ("🪑", "chair_adjust"),
        ("TRT", "choose_treatment"),
        ("PWR", "adjust_power"),
        ("🧍", "coil_adjust"),
        ("🔊", "sound"),
        ("⚙️", "settings"),
    ]
    for i, (label, target) in enumerate(buttons):
        with cols[i]:
            current = st.session_state.screen == target
            style = "primary" if current else "secondary"
            if st.button(label, key=f"nav_{target}", type=style, use_container_width=True):
                go(target)

# ── SCREENS ────────────────────────────────────────────────────────────────

def screen_welcome():
    st.title("Welcome")
    st.markdown("Please confirm the following before your session:")
    st.divider()

    d = st.session_state.disclaimers
    d["no_piercings"] = st.checkbox("I have no piercings in the treatment area", value=d["no_piercings"])
    d["no_pacemaker"] = st.checkbox("I do not have a pacemaker", value=d["no_pacemaker"])
    d["no_implants"]  = st.checkbox("I do not have metal implants", value=d["no_implants"])
    d["no_phone"]     = st.checkbox("I have removed my phone and electronic devices", value=d["no_phone"])

    st.divider()
    st.markdown("**Enter your height (cm) for automatic chair adjustment:**")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("▼", key="h_down", use_container_width=True):
            st.session_state.height = max(140, st.session_state.height - 1)
    with col2:
        st.markdown(f"<h1 style='text-align:center'>{st.session_state.height}</h1>", unsafe_allow_html=True)
    with col3:
        if st.button("▲", key="h_up", use_container_width=True):
            st.session_state.height = min(220, st.session_state.height + 1)

    st.divider()
    all_confirmed = all(d.values())
    if all_confirmed:
        if st.button("Continue →", type="primary", use_container_width=True):
            go("chair_adjust")
    else:
        st.warning("Please confirm all items above to continue.")


def screen_chair_adjust():
    treatment_header()
    st.subheader("Chair Adjust")
    st.caption("Use buttons to adjust chair position")
    st.divider()

    chair = st.session_state.chair

    for part in ["Backrest", "Seat", "Footrest", "Height"]:
        key = part.lower()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("▼", key=f"chair_{key}_down", use_container_width=True):
                chair[key] = max(-5, chair[key] - 1)
        with col2:
            st.markdown(f"**{part}:** {chair[key]:+d}")
        with col3:
            if st.button("▲", key=f"chair_{key}_up", use_container_width=True):
                chair[key] = min(5, chair[key] + 1)

    st.divider()
    if st.button("Reset chair to default", use_container_width=True):
        st.session_state.chair = {"backrest": 0, "seat": 0, "footrest": 0, "height": 0}

    bottom_nav()


def screen_choose_treatment():
    treatment_header()
    st.subheader("Choose Treatment")
    st.divider()

    treatments = ["AUTO", "Protocol 1", "Protocol 2", "Protocol 3", "Protocol 4", "Protocol 5", "Protocol 6"]

    for t in treatments:
        selected = st.session_state.treatment == t
        label = f"✓  {t}" if selected else t
        btn_type = "primary" if selected else "secondary"
        if st.button(label, key=f"trt_{t}", type=btn_type, use_container_width=True):
            st.session_state.treatment = t

    st.divider()
    if st.session_state.treatment:
        col1, col2 = st.columns(2)
        with col1:
            duration = st.selectbox("Duration (min)", [5, 10, 15, 20, 30], index=2)
            st.session_state.time_remaining = duration
        with col2:
            if not st.session_state.treatment_running:
                if st.button("▶  Start", type="primary", use_container_width=True):
                    st.session_state.treatment_running = True
                    st.session_state.treatment_paused = False
    else:
        st.info("Select a treatment to start.")

    bottom_nav()


def screen_adjust_power():
    treatment_header()
    st.subheader("Adjust Power")
    st.divider()

    # ALL zones
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("▼", key="pwr_all_down", use_container_width=True):
            v = max(0, st.session_state.power_all - 1)
            st.session_state.power_all = v
            for z in st.session_state.power_zones:
                st.session_state.power_zones[z] = v
    with col2:
        st.markdown(f"**ALL zones:** {st.session_state.power_all}")
    with col3:
        if st.button("▲", key="pwr_all_up", use_container_width=True):
            v = min(10, st.session_state.power_all + 1)
            st.session_state.power_all = v
            for z in st.session_state.power_zones:
                st.session_state.power_zones[z] = v

    st.divider()
    st.caption("Individual zone control:")

    zone_labels = {
        "S": "Spine (S)",
        "L_upper": "Left upper (L)",
        "B_upper": "Back upper (B)",
        "R_upper": "Right upper (R)",
        "L_lower": "Left lower (L)",
        "B_lower": "Back lower (B)",
        "R_lower": "Right lower (R)",
    }

    for zone, label in zone_labels.items():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("▼", key=f"pwr_{zone}_down", use_container_width=True):
                st.session_state.power_zones[zone] = max(0, st.session_state.power_zones[zone] - 1)
        with col2:
            st.markdown(f"{label}: **{st.session_state.power_zones[zone]}**")
        with col3:
            if st.button("▲", key=f"pwr_{zone}_up", use_container_width=True):
                st.session_state.power_zones[zone] = min(10, st.session_state.power_zones[zone] + 1)

    bottom_nav()


def screen_coil_adjust():
    treatment_header()
    st.subheader("Coil Position")
    st.caption("Adjust coil positions (L = Left, B = Back/Body, R = Right)")
    st.divider()

    coil = st.session_state.coil
    directions = {"Left (L)": "L", "Body (B)": "B", "Right (R)": "R"}

    for label, key in directions.items():
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        with col1:
            if st.button("◀◀", key=f"coil_{key}_back2", use_container_width=True):
                coil[key] = max(-5, coil[key] - 2)
        with col2:
            if st.button("◀", key=f"coil_{key}_back", use_container_width=True):
                coil[key] = max(-5, coil[key] - 1)
        with col3:
            st.markdown(f"<p style='text-align:center'><b>{label}:</b> {coil[key]:+d}</p>", unsafe_allow_html=True)
        with col4:
            if st.button("▶", key=f"coil_{key}_fwd", use_container_width=True):
                coil[key] = min(5, coil[key] + 1)
        with col5:
            if st.button("▶▶", key=f"coil_{key}_fwd2", use_container_width=True):
                coil[key] = min(5, coil[key] + 2)

    st.divider()
    if st.button("Reset coils to default", use_container_width=True):
        st.session_state.coil = {"L": 0, "B": 0, "R": 0}

    bottom_nav()


def screen_sound():
    treatment_header()
    st.subheader("Sound")
    st.divider()

    sources = ["AUTO", "RADIO", "BLUETOOTH", "SPOTIFY"]
    cols = st.columns(2)
    for i, source in enumerate(sources):
        with cols[i % 2]:
            selected = st.session_state.sound_source == source
            label = f"✓  {source}" if selected else source
            btn_type = "primary" if selected else "secondary"
            if st.button(label, key=f"sound_{source}", type=btn_type, use_container_width=True):
                st.session_state.sound_source = source

    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀", key="vol_down", use_container_width=True):
            st.session_state.volume = max(0, st.session_state.volume - 1)
    with col2:
        st.markdown(f"<h2 style='text-align:center'>Volume: {st.session_state.volume}</h2>", unsafe_allow_html=True)
    with col3:
        if st.button("▶", key="vol_up", use_container_width=True):
            st.session_state.volume = min(10, st.session_state.volume + 1)

    bottom_nav()


def screen_settings():
    treatment_header()
    st.subheader("Settings")
    st.divider()

    st.markdown("**Language**")
    st.selectbox("Interface language", ["English", "Norwegian"], key="lang")

    st.divider()
    st.markdown("**Accessibility**")
    st.toggle("Large text mode", key="large_text")
    st.toggle("High contrast mode", key="high_contrast")

    st.divider()
    st.markdown("**Session**")
    if st.button("End session / Goodbye", type="primary", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    bottom_nav()


# --- Router ---
screen = st.session_state.screen
if screen == "welcome":         screen_welcome()
elif screen == "chair_adjust":  screen_chair_adjust()
elif screen == "choose_treatment": screen_choose_treatment()
elif screen == "adjust_power":  screen_adjust_power()
elif screen == "coil_adjust":   screen_coil_adjust()
elif screen == "sound":         screen_sound()
elif screen == "settings":      screen_settings()
else:
    st.error(f"Unknown screen: {screen}")
    go("welcome")
