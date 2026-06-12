import json
import os
import random
import urllib.error
import urllib.request

# Game Title and Introduction
def display_title():
    print("=" * 50)
    print("    MURDER MYSTERY: THE STOLEN DIAMOND")
    print("=" * 50)
    print()


# Show the crime scene in simple words
def display_crime_scene(victim):
    print("\n--- CRIME SCENE ---")
    print(f"Tonight's victim: {victim}")
    print("The priceless diamond is missing from the museum display.")
    print("You are standing in the main gallery.")
    print("A broken glass case, a red scarf, and a strange note were found nearby.")
    print("Your job is to study the clues and find the hidden culprit.\n")


# Random victim names for each new round
def create_victims():
    victims = [
        "Curator Sarah Lane",
        "Guide Leo Stone",
        "Archivist Nina Reed",
        "Security Chief Paul Grant"
    ]
    return victims


# Store clues in a list so the player can review them later
def create_clues():
    clues = [
        "The glass case was broken from the inside, not from the outside.",
        "A red scarf was found near the diamond display.",
        "The museum alarm stopped exactly at 9:40 PM.",
        "Someone used a museum key to open the vault.",
        "Dr. Wilson was seen leaving the gallery just before the alarm stopped."
    ]
    return clues


# Hidden contradictions between clues and alibis
# These are simple, beginner-friendly hints that reward detective work.
def create_contradictions():
    contradictions = [
        {
            "suspect": "Dr. James Wilson",
            "message": "Clue: The alarm stopped at 9:40 PM, but Dr. Wilson said he was in his office. This timing does not match his alibi.",
            "points": 10
        },
        {
            "suspect": "Emma Rodriguez",
            "message": "Clue: A red scarf was found near the main gallery, but Emma said she was patrolling the east wing. This is a possible contradiction in her story.",
            "points": 10
        },
        {
            "suspect": "Marcus Chen",
            "message": "Clue: Someone used a museum key, but Marcus said he was only in the storage room. This makes his alibi less reliable.",
            "points": 10
        }
    ]
    return contradictions


# Show all clues in a friendly way
def display_clues(clues):
    print("\n--- CLUE BOARD ---")
    if not clues:
        print("No clues have been found yet.")
        return

    for index, clue in enumerate(clues, 1):
        print(f"{index}. {clue}")
    print()


# Build a safe built-in case when Gemini is not available
def create_default_case():
    return {
        "victim": random.choice([
            "Curator Sarah Lane",
            "Guide Leo Stone",
            "Archivist Nina Reed",
            "Security Chief Paul Grant"
        ]),
        "scene": "The priceless diamond is missing from the museum display.",
        "clues": [
            "The glass case was broken from the inside, not from the outside.",
            "A red scarf was found near the diamond display.",
            "The museum alarm stopped exactly at 9:40 PM.",
            "Someone used a museum key to open the vault.",
            "Dr. Wilson was seen leaving the gallery just before the alarm stopped."
        ],
        "suspects": [
            {
                "name": "Dr. James Wilson",
                "profession": "Museum Director",
                "motive": "He wanted to sell the diamond secretly",
                "alibi": "I was in my office reviewing documents",
                "interrogation": [
                    "Q: Where were you during the theft?",
                    "A: I was working late in my office, going over some paperwork.",
                    "Q: Do you know anyone who would steal the diamond?",
                    "A: Many people know about the diamond's value... *nervous laugh*"
                ]
            },
            {
                "name": "Emma Rodriguez",
                "profession": "Museum Security Guard",
                "motive": "She needed money for her sick daughter",
                "alibi": "I was patrolling the east wing",
                "interrogation": [
                    "Q: Were you watching the diamond vault?",
                    "A: Yes, I patrol that area every hour.",
                    "Q: Did you see anyone suspicious?",
                    "A: No... well, Dr. Wilson was acting strange earlier that evening."
                ]
            },
            {
                "name": "Marcus Chen",
                "profession": "Art Appraiser",
                "motive": "He has connections to diamond smugglers",
                "alibi": "I was cataloging artifacts in the storage room",
                "interrogation": [
                    "Q: What were you doing in the storage room?",
                    "A: Cataloging recently acquired artifacts, like always.",
                    "Q: Do you have any ties to the black market?",
                    "A: That's ridiculous! I'm a legitimate professional."
                ]
            }
        ],
        "contradictions": [
            {
                "suspect": "Dr. James Wilson",
                "message": "Clue: The alarm stopped at 9:40 PM, but Dr. Wilson said he was in his office. This timing does not match his alibi.",
                "points": 10
            },
            {
                "suspect": "Emma Rodriguez",
                "message": "Clue: A red scarf was found near the main gallery, but Emma said she was patrolling the east wing. This is a possible contradiction in her story.",
                "points": 10
            },
            {
                "suspect": "Marcus Chen",
                "message": "Clue: Someone used a museum key, but Marcus said he was only in the storage room. This makes his alibi less reliable.",
                "points": 10
            }
        ]
    }


# Use the AI provider to generate a fresh mystery case every game.
# The provided key format is Groq/OpenAI-compatible, so this path uses that endpoint.
def generate_case_from_grok():
    api_key = os.getenv("GROK_API_KEY")
    
    if not api_key:
        print("\n[!] API Key Missing: Please create your own API key at https://console.groq.com/")
        print("[!] Set it as an environment variable named 'GROK_API_KEY'.")
        return None

    prompt = """
    Create a small murder mystery case in strict JSON only.
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

        # Try the direct JSON parse first; if the response is wrapped or noisy,
        # extract the first JSON object from the text.
        try:
            print("\n===== AI RAW RESPONSE =====")
            print(cleaned)
            print("===== END RESPONSE =====\n")
            case = json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = cleaned[start:end + 1]
                try:
                    case = json.loads(candidate)
                except json.JSONDecodeError:
                    # Last-resort fallback: trim incomplete trailing text and try again.
                    candidate = candidate.strip()
                    if candidate.count("{") > candidate.count("}"):
                        candidate += "}" * (candidate.count("{") - candidate.count("}"))
                    case = json.loads(candidate)
            else:
                raise ValueError("No JSON object found in Groq response")

        print("Groq mystery case loaded successfully.")
        return case

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Groq API HTTP Error {e.code}: {error_body}")
        print("Using built-in mystery case instead.")
        return None
    except Exception as error:
        print(f"An unexpected error occurred: {error}")
        print("Using built-in mystery case instead.")
        return None


# Create suspects using dictionaries
def create_suspects():
    suspects = [
        {
            "name": "Dr. James Wilson",
            "profession": "Museum Director",
            "motive": "He wanted to sell the diamond secretly",
            "alibi": "I was in my office reviewing documents",
            "interrogation": [
                "Q: Where were you during the theft?",
                "A: I was working late in my office, going over some paperwork.",
                "Q: Do you know anyone who would steal the diamond?",
                "A: Many people know about the diamond's value... *nervous laugh*"
            ]
        },
        {
            "name": "Emma Rodriguez",
            "profession": "Museum Security Guard",
            "motive": "She needed money for her sick daughter",
            "alibi": "I was patrolling the east wing",
            "interrogation": [
                "Q: Were you watching the diamond vault?",
                "A: Yes, I patrol that area every hour.",
                "Q: Did you see anyone suspicious?",
                "A: No... well, Dr. Wilson was acting strange earlier that evening."
            ]
        },
        {
            "name": "Marcus Chen",
            "profession": "Art Appraiser",
            "motive": "He has connections to diamond smugglers",
            "alibi": "I was cataloging artifacts in the storage room",
            "interrogation": [
                "Q: What were you doing in the storage room?",
                "A: Cataloging recently acquired artifacts, like always.",
                "Q: Do you have any ties to the black market?",
                "A: That's ridiculous! I'm a legitimate professional."
            ]
        }
    ]
    return suspects




# Display all suspects
def display_suspects(suspects):
    print("\n--- SUSPECTS ---")
    for index, suspect in enumerate(suspects, 1):
        print(f"{index}. {suspect['name']} - {suspect['profession']}")
    print()




# Interrogate a suspect
def interrogate_suspect(suspects, suspect_number, contradictions):
    if suspect_number < 1 or suspect_number > len(suspects):
        print("Invalid suspect number!")
        return 0

    suspect = suspects[suspect_number - 1]
    print(f"\n--- INTERROGATING {suspect['name'].upper()} ---")
    print(f"Profession: {suspect['profession']}")
    print(f"Alibi: {suspect['alibi']}\n")

    # Display interrogation responses
    for line in suspect['interrogation']:
        print(line)

    score_gain = 0
    found_contradiction = False

    # Check for hidden contradictions connected to this suspect
    for clue in contradictions:
        if clue['suspect'] == suspect['name']:
            found_contradiction = True
            print("\nHidden contradiction found!")
            print(clue['message'])
            score_gain += clue['points']
            print(f"Detective Score +{clue['points']}!")

    if not found_contradiction:
        print("\nNo clear contradiction was found in this interview.")

    print()
    return score_gain




# Make an accusation
def make_accusation(suspects, accused_number, murderer_index):
    if accused_number < 1 or accused_number > len(suspects):
        print("Invalid suspect number!")
        return False

    accused = suspects[accused_number - 1]

    if accused_number - 1 == murderer_index:
        print(f"\n*** CORRECT! ***")
        print(f"{accused['name']} was the murderer!")
        print(f"Motive: {accused['motive']}")
        return True
    else:
        print(f"\n*** WRONG! ***")
        print(f"{accused['name']} is not the murderer.")
        print("Keep investigating...")
        return False




# Main game function
def play_game():
    display_title()

    # Game setup
    print("A priceless diamond has been stolen from the museum!")
    print("Three suspects are under investigation.")
    print("Use the clues and interviews to solve the mystery.\n")

    case = generate_case_from_grok()
    if case is None:
        case = create_default_case()

    victim = case.get("victim", random.choice(create_victims()))
    display_crime_scene(victim)

    # Create suspects, clues, contradictions, and randomly choose murderer
    suspects = case.get("suspects", create_suspects())
    clues = case.get("clues", create_clues())
    contradictions = case.get("contradictions", create_contradictions())

    # Ensure the murderer matches what the AI intended
    murderer_name = case.get("murderer")
    murderer_index = -1
    for i, s in enumerate(suspects):
        if s.get("name") == murderer_name:
            murderer_index = i
            break
    if murderer_index == -1:
        murderer_index = random.randint(0, len(suspects) - 1)

    detective_score = 0

    display_suspects(suspects)
    print("Tip: Each contradiction you spot gives detective points.\n")
   
    # Game loop
    game_won = False
    interrogations_done = 0
    max_interrogations = 5
   
    while not game_won and interrogations_done < max_interrogations:
        print("\n--- WHAT DO YOU WANT TO DO? ---")
        print("1. Interrogate a suspect")
        print("2. View clues")
        print("3. Make an accusation")
        print("4. Quit game")
        print(f"Current Detective Score: {detective_score}")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            display_suspects(suspects)
            try:
                suspect_num = int(input("Enter suspect number to interrogate: "))
                detective_score += interrogate_suspect(suspects, suspect_num, contradictions)
                interrogations_done += 1
                print(f"\nCurrent Detective Score: {detective_score}")
            except ValueError:
                print("Please enter a valid number!")

        elif choice == "2":
            display_clues(clues)

        elif choice == "3":
            display_suspects(suspects)
            try:
                accused_num = int(input("Enter suspect number to accuse: "))
                game_won = make_accusation(suspects, accused_num, murderer_index)
                if game_won:
                    detective_score += 25
                    print(f"\nGreat work! You earned 25 bonus points for solving the case.")
                    print(f"Final Detective Score: {detective_score}")
            except ValueError:
                print("Please enter a valid number!")

        elif choice == "4":
            print("\nThanks for playing!")
            return

        else:
            print("Invalid choice! Please enter 1, 2, 3, or 4.")

    if not game_won:
        print(f"\n*** GAME OVER ***")
        print(f"The murderer was: {suspects[murderer_index]['name']}")
        print(f"Motive: {suspects[murderer_index]['motive']}")
        print(f"Final Detective Score: {detective_score}")




# Run the game
if __name__ == "__main__":
    play_game()
   
    # Ask if player wants to play again
    play_again = input("\nDo you want to play again? (yes/no): ").strip().lower()
    if play_again == "yes" or play_again == "y":
        play_game()
    else:
        print("Goodbye!")


























        