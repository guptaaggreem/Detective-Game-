import json
import os
import random
import urllib.error
import urllib.request

import streamlit as st

st.set_page_config(page_title="Murder Mystery Detective Desk", page_icon="🕵️", layout="wide")

st.markdown(
    """
    <style>
        :root {
            --bg: #02070f;
            --panel: #07111d;
            --panel-2: #0d1726;
            --accent: #00e5ff;
            --accent-2: #ffd54a;
            --accent-3: #ff4fd8;
            --text: #eff7ff;
            --muted: #d9e8ff;
            --good: #8bffb4;
            --bad: #ff8e9e;
        }
        html, body, [class*="stApp"] {
            background:
              radial-gradient(circle at top, rgba(0,229,255,0.07), transparent 22%),
              radial-gradient(circle at 80% 15%, rgba(255,79,216,0.08), transparent 18%),
              linear-gradient(180deg, #02070f 0%, #040b13 45%, #010409 100%);
            color: var(--text);
            font-family: "Segoe UI", Arial, sans-serif;
        }
        .stApp { background: transparent; }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3, h4 {
            color: #eff7ff !important;
            letter-spacing: 0.5px;
        }
        @keyframes neonPulse {
            0% { box-shadow: 0 0 0 rgba(0,229,255,0.15), 0 0 10px rgba(0,229,255,0.18); }
            50% { box-shadow: 0 0 8px rgba(0,229,255,0.35), 0 0 18px rgba(255,79,216,0.25); }
            100% { box-shadow: 0 0 0 rgba(0,229,255,0.15), 0 0 10px rgba(0,229,255,0.18); }
        }
        @keyframes scanGlow {
            0% { transform: translateX(-4px); opacity: 0.7; }
            50% { transform: translateX(4px); opacity: 1; }
            100% { transform: translateX(-4px); opacity: 0.7; }
        }
        .stButton > button {
            background: linear-gradient(135deg, var(--accent), var(--accent-3));
            color: #05101c;
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 12px;
            font-weight: 800;
            box-shadow: 0 0 0 1px rgba(0,229,255,0.25), 0 10px 24px rgba(0,229,255,0.18);
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 22px rgba(255, 209, 102, 0.35);
        }
        .stSelectbox > div > div, .stTextInput > div > div {
            background-color: rgba(21, 29, 51, 0.95);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #111827 0%, #18233a 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        .css-1d391kg, .css-1v0mbdj, .css-18e3th9 { background: transparent; }
        .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.08);
        }
        .suspect-card {
    border: 2px solid rgba(0,229,255,0.85) !important;
    border-radius: 18px !important;
    width: 100% !important;
    padding: 16px !important;
    min-height: 320px !important;
    box-sizing: border-box !important;

    background: linear-gradient(
        135deg,
        rgba(7,17,29,0.98),
        rgba(13,23,38,0.98)
    ) !important;

    box-shadow:
        0 0 0 1px rgba(255,255,255,0.03),
        0 12px 30px rgba(0,229,255,0.12),
        inset 0 0 18px rgba(0,229,255,0.05);

    animation: neonPulse 2.4s infinite;
}
        .detective-strip {
            background: linear-gradient(135deg, rgba(0,229,255,0.08), rgba(255,79,216,0.05));
            border: 1px solid rgba(0,229,255,0.25);
            border-radius: 14px;
            padding: 10px 12px;
            margin-bottom: 10px;
            box-shadow: 0 0 18px rgba(0,229,255,0.08);
            animation: scanGlow 2.6s infinite;
        }
        .scene-card {
            background: linear-gradient(135deg, rgba(7,17,29,0.98), rgba(13,23,38,0.98));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 10px;
            box-shadow: 0 0 18px rgba(0,229,255,0.08), inset 0 0 18px rgba(255,255,255,0.02);
            margin-bottom: 12px;
        }
        [data-testid="column"] {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
}
        [data-testid="stHorizontalBlock"] { gap: 1.05rem; align-items: stretch; }
        div[data-testid="column"] > div { display: flex; justify-content: center; align-items: stretch; width: 100%; }
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(255,209,102,0.12), rgba(255,127,80,0.12));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 8px 10px;
        }
        div[data-testid="stMetricValue"] { color: #fff7d6 !important; }
        div[data-testid="stMetricLabel"] { color: #dbe4ff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False, ttl=1800)
def get_ai_api_key():
    key = os.getenv("GROK_API_KEY")
    if not key:
        try:
            key = st.secrets.get("GROK_API_KEY")
        except Exception:
            pass
    return key


@st.cache_data(show_spinner="Generating a new mystery...", ttl=1800)
def generate_case_from_grok(nonce: int):
    api_key = get_ai_api_key()
    if not api_key:
        st.error("⚠️ API Key is missing! Please set 'GROK_API_KEY' in your environment or Streamlit secrets.")
        st.info("Check README.md for instructions on how to get an API key.")
        return None

    prompt = """
    Create a short, beginner-friendly murder mystery case in strict JSON only.
    Return exactly this structure:
    {
      "victim": "Name",
      "scene": "One sentence",
      "murderer": "Name of one of the suspects",
      "clues": ["clue 1", "clue 2", "clue 3", "clue 4"],
      "suspects": [
        {"name": "Suspect", "profession": "Job", "motive": "Reason", "alibi": "Simple alibi", "interrogation": ["Q: ...", "A: ..."]},
        {"name": "Suspect", "profession": "Job", "motive": "Reason", "alibi": "Simple alibi", "interrogation": ["Q: ...", "A: ..."]},
        {"name": "Suspect", "profession": "Job", "motive": "Reason", "alibi": "Simple alibi", "interrogation": ["Q: ...", "A: ..."]}
      ],
      "contradictions": [
        {"suspect": "Suspect", "message": "Explain conflict.", "points": 10},
        {"suspect": "Suspect", "message": "Explain conflict.", "points": 10},
        {"suspect": "Suspect", "message": "Explain conflict.", "points": 10}
      ]
    }
    Keep it beginner-friendly and do not add any text outside the JSON object.
    """

    data = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a murder mystery story generator. Return ONLY valid JSON."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 4000,
    }).encode("utf-8")

    url = "https://api.groq.com/openai/v1/chat/completions"
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MurderMysteryGame/1.0"
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.load(response)

        text = result["choices"][0]["message"]["content"]
        cleaned = text.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "", 1).strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

        try:
            case = json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = cleaned[start:end + 1]
                case = json.loads(candidate)
            else:
                raise ValueError("No JSON object found in AI response")

        return case
    except urllib.error.HTTPError as e:
        # Log the detailed error to the console for debugging
        print(f"Groq API HTTP Error {e.code}: {e.read().decode()}")
        return None
    except Exception:
        return None


def get_default_case():
    suspects = [
        {
            "name": "Dr. James Wilson",
            "profession": "Museum Director",
            "motive": "He wanted to sell the diamond secretly.",
            "alibi": "I was in my office reviewing documents.",
            "interrogation": [
                "Q: Where were you during the theft?",
                "A: I was working late in my office, going over some paperwork.",
                "Q: Do you know anyone who would steal the diamond?",
                "A: Many people know about the diamond's value... *nervous laugh*"
            ],
        },
        {
            "name": "Emma Rodriguez",
            "profession": "Museum Security Guard",
            "motive": "She needed money for her sick daughter.",
            "alibi": "I was patrolling the east wing.",
            "interrogation": [
                "Q: Were you watching the diamond vault?",
                "A: Yes, I patrol that area every hour.",
                "Q: Did you see anyone suspicious?",
                "A: No... well, Dr. Wilson was acting strange earlier that evening."
            ],
        },
        {
            "name": "Marcus Chen",
            "profession": "Art Appraiser",
            "motive": "He has connections to diamond smugglers.",
            "alibi": "I was cataloging artifacts in the storage room.",
            "interrogation": [
                "Q: What were you doing in the storage room?",
                "A: Cataloging recently acquired artifacts, like always.",
                "Q: Do you have any ties to the black market?",
                "A: That's ridiculous! I'm a legitimate professional."
            ],
        },
    ]

    clues = [
        "The glass case was broken from the inside, not from the outside.",
        "A red scarf was found near the diamond display.",
        "The museum alarm stopped exactly at 9:40 PM.",
        "Someone used a museum key to open the vault.",
        "Dr. Wilson was seen leaving the gallery just before the alarm stopped."
    ]

    contradictions = [
        {
            "suspect": "Dr. James Wilson",
            "message": "The alarm stopped at 9:40 PM, but Dr. Wilson said he was in his office. This timing does not match his alibi.",
            "points": 10,
        },
        {
            "suspect": "Emma Rodriguez",
            "message": "A red scarf was found in the main gallery, but Emma said she was patrolling the east wing. That is a contradiction in her story.",
            "points": 10,
        },
        {
            "suspect": "Marcus Chen",
            "message": "Someone used a museum key, but Marcus said he was only in the storage room. This makes his alibi less reliable.",
            "points": 10,
        },
    ]

    return {
    "suspects": suspects,
    "clues": clues,
    "contradictions": contradictions,
    "murderer": "Dr. James Wilson",
    "victim": random.choice([
        "Curator Sarah Lane",
        "Guide Leo Stone",
        "Archivist Nina Reed",
        "Security Chief Paul Grant"
    ]),
    "scene": "The priceless diamond is missing from the museum display."
    }


def get_case_data(case_nonce: int): # Added case_nonce parameter
    ai_case = generate_case_from_grok(case_nonce)
    fallback_case = get_default_case()

    if ai_case and isinstance(ai_case, dict):

        suspects = ai_case.get("suspects") or fallback_case["suspects"]
        clues = ai_case.get("clues") or fallback_case["clues"]
        contradictions = ai_case.get("contradictions") or fallback_case["contradictions"]
        victim = ai_case.get("victim") or fallback_case["victim"]
        scene = ai_case.get("scene") or fallback_case["scene"]

        murderer_name = ai_case.get("murderer")

        murderer_index = 0

        for i, suspect in enumerate(suspects):
            if suspect["name"] == murderer_name:
                murderer_index = i
                break

        return suspects, clues, contradictions, victim, scene, murderer_index, True

    return(
        fallback_case["suspects"],
        fallback_case["clues"],
        fallback_case["contradictions"],
        fallback_case["victim"],
        fallback_case.get("scene", "Unknown crime scene"),
        0, # In the default case, Dr. James Wilson (index 0) is always the murderer
        False, # Groq not used
    )


if "score" not in st.session_state:
    st.session_state.score = 0
if "selected_suspect" not in st.session_state:
    st.session_state.selected_suspect = 0
if "case_nonce" not in st.session_state:
    st.session_state.case_nonce = random.randint(1, 10_000_000)

if "game_data" not in st.session_state:
    res = get_case_data(st.session_state.case_nonce)
    st.session_state.game_data = {
        "suspects": res[0],
        "clues": res[1],
        "contradictions": res[2],
        "victim": res[3],
        "scene": res[4],
        "murderer_index": res[5],
        "groq_used": res[6]
    }

gd = st.session_state.game_data
suspects, clues, contradictions = gd["suspects"], gd["clues"], gd["contradictions"]
victim, scene, murderer_index, groq_used = gd["victim"], gd["scene"], gd["murderer_index"], gd["groq_used"]


st.markdown(
    """
    <div style="background: linear-gradient(135deg, rgba(255,209,102,0.12), rgba(255,127,80,0.08));
                border: 1px solid rgba(255,255,255,0.08); border-radius: 18px;
                padding: 18px 18px 10px 18px; margin-bottom: 12px;">
      <h1 style="margin:0; color:#fff7d6; font-size:2.2rem;">🕵️ Detective Murder Mystery</h1>
      <p style="margin-top:8px; color:#dbe4ff; font-size:1rem;">A polished detective desk for solving the museum diamond theft.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col_top, col_top_btn = st.columns([3, 1], vertical_alignment="bottom")
with col_top_btn:
    if st.button("Generate fresh case", use_container_width=True):
        st.cache_data.clear()
        if "game_data" in st.session_state:
            del st.session_state.game_data
        # Invalidate cache by changing the nonce
        st.session_state.case_nonce = random.randint(1, 10_000_000)
        st.session_state.selected_suspect = 0 # Reset selected suspect
        st.rerun()

with col_top:
    status_text = "Groq AI-generated case is active." if groq_used else "Groq is unavailable or rate-limited; the built-in case is active."
    st.info(status_text)


st.markdown("---")

left_col = st.container()

with left_col:
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(7,17,29,0.98), rgba(13,23,38,0.98));
                    border: 2px solid rgba(255,78,98,0.85); border-radius: 22px;
                    padding: 16px; margin: 0 auto 12px auto; max-width: 920px;
                    text-align: center; box-shadow: 0 0 18px rgba(255,78,98,0.14), inset 0 0 18px rgba(255,255,255,0.02);">
          <h3 style="margin-top:0; color:#ffe1e6; text-shadow: 0 0 8px rgba(255,78,98,0.25);">🧾 Crime Scene</h3>
          <p style="color:#dbe4ff; margin-bottom: 6px;"><b>Victim:</b> """ + victim + """</p>
          <p style="color:#dbe4ff; line-height: 1.45;">""" + scene + """</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="detective-strip">
          <b style="color:#eaffff;">🕵️ Detective status:</b> Interrogation mode is live. {'Groq API is powering this case.' if groq_used else 'The built-in case is active because the Groq provider is unavailable.'}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Suspect Cards")
    cards = st.columns(3, gap="large")
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    for i, suspect in enumerate(suspects):
        with cards[i]:
            st.markdown(
                f"""
                <div class="suspect-card">
                  <h4 style="margin-top:0; color:#eaffff; text-shadow: 0 0 6px rgba(0,229,255,0.28);">{suspect['name']}</h4>
                  <p style="color:#ffd54a; margin-bottom: 6px; font-weight: 800;">{suspect['profession']}</p>
                  <p style="color:#dbe4ff; line-height: 1.4;">{suspect['motive']}</p>
                  <div style="margin-top: 14px; color:#8bffb4; font-size: 0.92rem;">⚡ Ready for interrogation</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Inspect {suspect['name']}", key=f"btn_{i}"):
                st.session_state.selected_suspect = i
            st.caption("Click to open this suspect’s interview notes.")
    st.markdown(
        """
        <div class="detective-strip" style="margin-bottom: 12px;">
          <b style="color:#eaffff;">🕵️ Detective mode:</b> interrogations are active. Use the right panel to track clues while the suspect cards stay open on the left.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    st.sidebar.markdown("<h2 style='color:#fff7d6;'>🕵️ Detective Desk</h2>", unsafe_allow_html=True)
    st.sidebar.metric("Detective Score", st.session_state.score)
    st.sidebar.markdown("<p style='color:#dbe4ff;'>Solve the case by finding contradictions and accusing the right suspect.</p>", unsafe_allow_html=True)

    st.sidebar.markdown("<h4 style='color:#fff7d6;'>🧩 Clue Board</h4>", unsafe_allow_html=True)
    for index, clue in enumerate(clues, 1):
        st.sidebar.markdown(f"<div style='background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:8px 10px; margin-bottom:6px; color:#dbe4ff;'> {index}. {clue}</div>", unsafe_allow_html=True)

    st.sidebar.markdown("<h4 style='color:#fff7d6;'>💡 Quick Tips</h4>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='color:#dbe4ff;'>1. Read every suspect card.<br>2. Spot contradictions in each alibi.<br>3. Accuse the real culprit for bonus points.</div>", unsafe_allow_html=True)


selected = suspects[st.session_state.selected_suspect]

st.markdown("---")

st.markdown(
    f"""
    <div style="background: linear-gradient(135deg, rgba(255,209,102,0.12), rgba(255,127,80,0.08));
                border: 1px solid rgba(255,255,255,0.08); border-radius: 16px;
                padding: 12px 14px; margin-bottom: 10px;">
      <h3 style="margin:0; color:#fff7d6;">Current Investigation: {selected['name']}</h3>
    </div>
    """,
    unsafe_allow_html=True,
)
col_a, col_b = st.columns([1, 1])

with col_a:
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(7,17,29,0.98), rgba(13,23,38,0.98));
                    border: 1px solid rgba(0,229,255,0.25); border-radius: 18px;
                    padding: 14px; min-height: 220px;
                    box-shadow: 0 0 18px rgba(0,229,255,0.07), inset 0 0 18px rgba(255,255,255,0.02);">
          <p style="color:#ffd54a; margin-bottom: 6px;"><b>Profession</b></p>
          <p style="color:#dbe4ff;">""" + selected['profession'] + """</p>
          <p style="color:#ffd54a; margin-bottom: 6px;"><b>Alibi</b></p>
          <p style="color:#dbe4ff;">""" + selected['alibi'] + """</p>
          <p style="color:#ffd54a; margin-bottom: 6px;"><b>Motive</b></p>
          <p style="color:#dbe4ff;">""" + selected['motive'] + """</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_b:
    notes_html = """
    <div style="background: linear-gradient(135deg, rgba(7,17,29,0.98), rgba(13,23,38,0.98));
                border: 2px solid rgba(0,229,255,0.75); border-radius: 18px;
                padding: 14px; min-height: 220px; box-shadow: 0 0 18px rgba(0,229,255,0.10), inset 0 0 18px rgba(255,255,255,0.02);">
      <h4 style="margin-top:0; color:#fff7d6;">Interview Notes</h4>
    """
    for line in selected['interrogation']:
        notes_html += f"<p style='margin: 6px 0; color:#dbe4ff; line-height: 1.35;'>• {line}</p>"
    notes_html += "</div>"
    st.markdown(notes_html, unsafe_allow_html=True)

    st.markdown(
        """
        <div style="margin-top: 10px; padding: 10px 12px; border-radius: 14px;
                    background: linear-gradient(135deg, rgba(255,79,216,0.05), rgba(0,229,255,0.06));
                    border: 1px solid rgba(255,255,255,0.08); color:#dbe4ff;">
          <b style="color:#ffd54a;">Interrogation cue:</b> the detective is comparing alibis with the clues in real time.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Check for contradiction", key="check_contradiction"):
        found = False
        for item in contradictions:
            if item['suspect'] == selected['name']:
                found = True
                st.success(f"Contradiction found! +{item['points']} points")
                st.info(item['message'])
                st.session_state.score += item['points']
                break
        if not found:
            st.warning("No clear contradiction was found in this interview.")

st.markdown("---")

st.markdown(
    """
    <div style="background: linear-gradient(135deg, rgba(0,229,255,0.08), rgba(255,79,216,0.05));
                border: 1px solid rgba(0,229,255,0.25); border-radius: 18px;
                padding: 12px 14px; margin-top: 10px;
                box-shadow: 0 0 18px rgba(0,229,255,0.07);">
      <h3 style="margin-top:0; color:#eaffff; text-shadow: 0 0 8px rgba(0,229,255,0.18);">Make an Accusation</h3>
    </div>
    """,
    unsafe_allow_html=True,
)
accuse_choice = st.selectbox("Choose the suspect you think did it:", [suspect['name'] for suspect in suspects])
if st.button("Accuse selected suspect"):
    accused_index = [suspect['name'] for suspect in suspects].index(accuse_choice)
    if accused_index == murderer_index:
        st.balloons()
        st.success("Correct! You solved the case.")
        st.session_state.score += 25
        st.write(f"**Motive:** {suspects[murderer_index]['motive']}")
    else:
        st.error("That was not the culprit. Keep investigating.")

st.markdown(
    f"""
    <div style="background: linear-gradient(135deg, rgba(255,209,102,0.14), rgba(255,127,80,0.10));
                border: 1px solid rgba(255,255,255,0.08); border-radius: 14px;
                padding: 10px 12px; margin-top: 12px; color:#fff7d6;">
      <b>Detective Score:</b> {st.session_state.score}
    </div>
    """,
    unsafe_allow_html=True,
)
