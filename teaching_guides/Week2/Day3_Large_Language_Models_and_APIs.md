# Day 3: Large Language Models and APIs

## Objective
Understand Large Language Models (LLMs) and call one from Python via an API.

## Core Concepts
- **What an LLM is** and how it generates text
- **Calling an API** with an OpenAI-compatible client
- **API keys & secrets** — keeping them out of source control
- **Prompts**: system vs. user messages, `temperature`, `max_tokens`
- **Handling responses** and failures (fallbacks)

> **This project's LLM:** the game talks to UF's **NaviGator** endpoint using the
> `openai` client library pointed at a custom `base_url`, running the
> **`mistral-7b-instruct`** model. The notebook
> [ai_materials/03_navigator_api_testing.ipynb](../../ai_materials/03_navigator_api_testing.ipynb)
> walks through testing this from scratch.

## Hands-On Exercise
The student-facing steps live in
[student_tutorials/Week2_Day3_Day4_LLM.md](../../student_tutorials/Week2_Day3_Day4_LLM.md).
1. Create `ai_materials/navigator_api_key.json` (it is **gitignored** — never commit it):
   ```json
   {
     "OPENAI_API_KEY": "your-key-here",
     "base_url": "https://the-navigator-endpoint/v1"
   }
   ```
2. Run `python test_emotions.py` to see generated dialogue per emotion.

## Code References

> Snippets are copied from the real project files.

### Connecting to the API
**File**: [ai_dialogue_manager.py](../../ai_dialogue_manager.py) — `__init__`

```python
        # @STUDENT-EDIT-Week2_Day3-1: Add your API key in ai_materials/navigator_api_key.json
        self.credentials = self._load_api_credentials(key_file_path)

        if self.credentials:
            try:
                self.client = openai.OpenAI(
                    api_key=self.credentials["api_key"],
                    base_url=self.credentials["base_url"],
                )
                self.fallback_mode = False
                print("🤖 AI Dialogue Manager initialized with API access.")
            except Exception as e:
                print(f"⚠️ AI Manager could not connect, falling back to offline mode: {e}")
                self.fallback_mode = True
```

**DETAILED WALKTHROUGH:**
- **`openai.OpenAI(api_key=..., base_url=...)`** — the same client library that talks to
  OpenAI can talk to *any* OpenAI-compatible endpoint by changing `base_url`. That's how
  we reach UF NaviGator instead of OpenAI's servers.
- **`fallback_mode`** flips to `False` only once a client is built — if anything fails,
  we stay in safe offline mode.

### Loading the API Key Safely
**File**: [ai_dialogue_manager.py](../../ai_dialogue_manager.py) — `_load_api_credentials`

```python
    def _load_api_credentials(self, key_file_path):
        try:
            with open(key_file_path, "r") as file:
                data = json.load(file)
            api_key = data.get("OPENAI_API_KEY")
            base_url = data.get("base_url")
            if not api_key or not base_url:
                print("❌ Missing 'OPENAI_API_KEY' or 'base_url' in credentials file.")
                return None
            return {"api_key": api_key, "base_url": base_url}
        except FileNotFoundError:
            print(f"❌ Credentials file not found at: {key_file_path}")
            return None
        except json.JSONDecodeError:
            print("❌ Invalid JSON format in credentials file.")
            return None
```

**DETAILED WALKTHROUGH:**
- The key lives in a **separate JSON file** that is listed in `.gitignore`, so it never
  gets committed to GitHub. This is the single most important security habit in the
  whole camp — **secrets do not go in source code.**
- Note the expected JSON keys: **`OPENAI_API_KEY`** and **`base_url`**. (If the file is
  missing or malformed, the method returns `None` and the game uses fallback dialogue.)

### Generating Dialogue (Prompt Engineering)
**File**: [ai_dialogue_manager.py](../../ai_dialogue_manager.py) — `generate_npc_dialogue`

```python
    def generate_npc_dialogue(self, character_name, character_role,
                              player_context, emotion="neutral"):
        if self.fallback_mode or not self.client:
            return self._get_fallback_dialogue(character_name, player_context, emotion)

        emotion_guidance = {
            "happy": "The player seems cheerful... match their positive energy.",
            "sad": "The player appears down... be comforting and encouraging.",
            # ... angry, surprised, fearful, neutral ...
        }
        emotion_hint = emotion_guidance.get(emotion, emotion_guidance["neutral"])

        # @STUDENT-EDIT-Week2_Day4-1: Change the prompt to give the AI a new personality!
        prompt = f"""
        You are {character_name}, a {character_role} in a cozy farming game called PyDew Valley.
        Player context: {player_context}
        Player's current emotion: {emotion}
        Emotional guidance: {emotion_hint}
        Generate a short, friendly dialogue response (1-2 sentences) ...
        """

        response = self.client.chat.completions.create(
            model="mistral-7b-instruct",
            messages=[
                # @STUDENT-EDIT-Week2_Day5-1: Fine-tune the system prompt before the final demo
                {"role": "system", "content": "You are a helpful NPC in a farming game. "
                                              "Keep responses brief, friendly, all-ages."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
```

**DETAILED WALKTHROUGH:**
- **System vs. user message:** the *system* message sets the AI's overall behavior; the
  *user* message is the specific request. Marker `@STUDENT-EDIT-Week2_Day4-1` (in the
  user prompt) and `@STUDENT-EDIT-Week2_Day5-1` (system prompt) are where students give
  the NPC a personality — pirate, robot, grumpy farmer, etc.
- **`emotion_guidance`** is a dictionary that turns a detected emotion into instructions
  for the AI — this is where Week 2's two AI systems start to meet.
- **`temperature=0.8`** controls randomness/creativity; **`max_tokens=100`** caps length.
- **`response.choices[0].message.content`** is how we pull the text out of the API
  response object — a key "parsing the response" lesson.

### The Fallback Path (No Key, No Internet)
**File**: [ai_dialogue_manager.py](../../ai_dialogue_manager.py) — `_get_fallback_dialogue`

```python
    def _get_fallback_dialogue(self, character_name, player_context, emotion):
        # @STUDENT-EDIT-Week2_Day4-2: Create custom fallback responses for when the API is down
        if "Merchant Pete" in character_name:
            if emotion == "happy":
                return "I can see you're in great spirits today! ..."
            elif emotion == "sad":
                return "I notice you seem a bit down, friend. ..."
            # ... angry, surprised, fearful ...
        return "Hello there! Nice to see you around the farm today."
```

**DETAILED WALKTHROUGH:**
- Even with no API access, the NPC gives an **emotion-aware** reply. This is why the
  game is demoable offline. Marker `@STUDENT-EDIT-Week2_Day4-2` is where students write
  their own fallback lines.

## Key Learning Points
1. **LLMs generate text** from a prompt; we reach one over an HTTP API.
2. **OpenAI-compatible clients** work with any endpoint via `base_url`.
3. **Keep secrets in a gitignored file**, never in code.
4. **Prompt engineering** — system vs. user messages, `temperature`, `max_tokens`.
5. **Parse responses** and always have a **fallback**.

## Extension Activities
1. **Give the NPC a personality** at `@STUDENT-EDIT-Week2_Day4-1` /
   `@STUDENT-EDIT-Week2_Day5-1`.
2. **Write custom fallbacks** at `@STUDENT-EDIT-Week2_Day4-2`.
3. **Experiment with `temperature`** (e.g. 0.2 vs 1.0) and observe how replies change.
4. **Add a debug print** of the prompt at `@STUDENT-EDIT-Week2_Day5-2` to see exactly
   what gets sent.

## Troubleshooting Tips
- **`Credentials file not found`:** create `ai_materials/navigator_api_key.json` with
  `OPENAI_API_KEY` and `base_url`. Confirm it's valid JSON (commas, quotes).
- **Always offline / fallback mode:** the key file is missing/malformed, or `openai`
  isn't installed (`install("openai")` in `main.py`).
- **Empty or weird replies:** lower `temperature`, shorten the prompt, and confirm the
  `model` name matches what the endpoint serves (`mistral-7b-instruct`).
- **Accidentally committed your key:** rotate it immediately and confirm
  `ai_materials/navigator_api_key.json` is in `.gitignore`.
