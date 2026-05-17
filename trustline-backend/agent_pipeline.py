"""Interactive agent pipeline that wires ML predictors, agents, and an LLM adapter.

Usage:
  - Update `.env` with LLM_MODE and model paths (or use `.env.example`).
  - Run: `python agent_pipeline.py`

This script will attempt to load local ML models if available; otherwise it falls back to safe stubs.
"""
import os
from dotenv import load_dotenv

load_dotenv()

def make_predictors_from_conversation_test():
    try:
        import conversation_test as conv

        # attempt to load models from env paths
        distress_path = os.getenv("DISTRESS_MODEL_PATH", "./ml_models/suicide_model_distilbert_cpu_v2")
        emotion_path = os.getenv("EMOTION_MODEL_PATH", "./ml_models/emotion_model_distilbert_cpu_4class_best")
        try:
            dt_tokenizer, dt_model = conv.load_model_and_tokenizer(distress_path)
            em_tokenizer, em_model = conv.load_model_and_tokenizer(emotion_path)

            def distress_predictor(text: str):
                return conv.predict(dt_model, dt_tokenizer, text, max_length=256)

            def emotion_predictor(text: str):
                return conv.predict(em_model, em_tokenizer, text, max_length=128)

            return distress_predictor, emotion_predictor
        except Exception:
            # If loading fails, fall through to stub
            pass
    except Exception:
        pass

    # stub predictors
    def distress_stub(text: str):
        return ("non-suicide", 0.0)

    def emotion_stub(text: str):
        return ("neutral", 0.0)

    return distress_stub, emotion_stub


def main():
    # Import agents and ML shims lazily to avoid side-effects on import
    from app.agents.understanding import UnderstandingAgent
    from app.agents.planner import PlannerAgent
    from app.agents.chatbot_agent import ChatbotAgent
    from app.agents.filter_agent import FilterAgent
    from app.agents.llm_adapter import LLMAdapter
    from app.ml.fake_ml import FakeML

    distress_pred, emotion_pred = make_predictors_from_conversation_test()
    ml = FakeML(distress_pred, emotion_pred)

    understanding_agent = UnderstandingAgent(ml)
    planner_agent = PlannerAgent()
    chatbot_agent = ChatbotAgent()
    filter_agent = FilterAgent()
    llm = LLMAdapter()

    print("Agent pipeline ready. Type messages (type 'exit' to quit).")
    # Track current conversation's linked case (avoid creating duplicates)
    session_case_id = None

    def _looks_like_existing_case_message(text: str) -> bool:
        low = (text or '').lower()
        keys = ["case created", "complaint submitted", "already submitted", "already created", "case already created", "complaint submitted"]
        return any(k in low for k in keys)

    def _user_needs_support(text: str, understanding: dict) -> bool:
        low = (text or '').lower()
        if any(p in low for p in ("i dont have", "i'm alone", "im alone", "i have no", "no friend", "alone")):
            return True
        # elevated distress from detector
        try:
            if understanding.get('distress_label') and understanding.get('distress_conf', 0) > 0.65:
                return True
        except Exception:
            pass
        return False


    def _is_greeting_or_help(text: str) -> bool:
        low = (text or '').strip().lower()
        greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
        help_phrases = ["can you help", "need help", "help me", "anyone there", "is anyone there", "are you there", "can i get help", "can i talk to someone"]
        # Problem keywords that indicate a real issue
        problem_keywords = [
            "photo", "leak", "expose", "cyber", "scam", "bully", "hacked", "account", "fraud", "stolen", "threat", "blackmail", "abuse", "harass", "money", "lost", "suicide", "self-harm", "kill myself", "end my life", "i want to die"
        ]
        # If message is just a greeting
        if any(low == g for g in greetings):
            return True
        # If message is just a help phrase
        if any(low == p for p in help_phrases):
            return True
        # If message contains help phrase but also a problem keyword, treat as a real problem
        if any(p in low for p in help_phrases):
            if any(k in low for k in problem_keywords):
                return False
            return True
        return False

    # Track if a complaint has been submitted in this session
    complaint_submitted = False
    post_complaint_mode = False

    while True:
        try:
            text = input("\nYou: ")
        except EOFError:
            break
        if not text:
            continue
        if text.strip().lower() in {"exit", "quit"}:
            print("Exiting.")
            break

        # Only use greeting/help short-circuit if no complaint has been submitted yet and message is not a real problem
        if not complaint_submitted and _is_greeting_or_help(text):
            print("\nAssistant:")
            if any(w in text.lower() for w in ["help", "can you"]):
                print("Hello, this is Mithuru from TrustLine. Yes, I can help you. Please tell me what you're going through or how I can support you.")
            else:
                print("Hi, this is Mithuru from TrustLine. How can I help you today?")
            continue

        understanding = understanding_agent.process(text)
        # If in post-complaint mode, use special rules for concise, context-aware replies
        if post_complaint_mode:
            # Only generate a concise, context-aware, emotion-sensitive reply (no greeting, no intro, no metadata prompts)
            rules = [
                "Reply ONLY with a concise, natural, friend-style message based on the user's message and detected emotion.",
                "Do NOT repeat the greeting, TrustLine intro, or ask for info already collected.",
                "Do NOT output rules, JSON, or metadata prompts.",
                "If the user asks for advice, give practical, situation-specific advice.",
                "If the user just wants to talk, listen and validate their feelings.",
                "If the case is missing a truly critical field (e.g., phone for urgent contact), gently ask for it, but never repeat prompts for info already provided.",
                "If the user explicitly says they want to file a new complaint, restart the intake flow. Otherwise, stay in adaptive support mode."
            ]
            candidate_prompt = chatbot_agent.process(text, understanding, rules)
            # Run LLM and filter output for friend-style reply only
            raw_reply = llm.generate(candidate_prompt)
            # Remove any rules, JSON, or metadata prompts from LLM output
            import re
            def extract_friend_reply(s: str):
                # Remove JSON blocks
                s = re.sub(r"```json[\s\S]*?```", "", s)
                s = re.sub(r"\{[\s\S]*?\}", "", s)
                # Remove lines that look like rules or instructions
                lines = s.splitlines()
                filtered = []
                for line in lines:
                    if re.match(r"^(step|always|adapt|all replies|at the end|follow|collect|explain|encourage|never|do not|if the user|after collecting|ask if|tone:|safety:|offer|initial response|json response|metadata:|please respond|please let me know|summary:|user message:|intent:|distress detected:|emotion detected:|suicide/self-harm risk:)", line.strip().lower()):
                        continue
                    if line.strip().startswith("-") or line.strip().startswith("*"):
                        continue
                    if not line.strip():
                        continue
                    filtered.append(line)
                return " ".join(filtered).strip()
            friend_reply = extract_friend_reply(raw_reply)
            checked = filter_agent.process(friend_reply, understanding)
            print("\nAssistant:")
            if checked.get("ok"):
                print(checked.get("reply") or friend_reply or "[No reply generated]")
            else:
                print("(filtered)")
                print("I'm concerned about your safety. I recommend contacting a trusted person or the Mithuru hotline (1898). [Filter reason: {}]".format(checked.get("reason")))
            continue
        else:
            rules = planner_agent.process(understanding)
            candidate_prompt = chatbot_agent.process(text, understanding, rules)

        # Generate with LLM adapter
        try:
            raw_reply = llm.generate(candidate_prompt)
            # Try to extract structured JSON if provided by the LLM
            import json, re

            def extract_json(s: str):
                # Find the last JSON object in the string
                idx = s.rfind('{')
                if idx == -1:
                    return None
                try:
                    return json.loads(s[idx:])
                except Exception:
                    # Try to find a JSON-looking substring via regex
                    m = re.search(r"\{[\s\S]*\}\s*$", s)
                    if m:
                        try:
                            return json.loads(m.group(0))
                        except Exception:
                            return None
                    return None

            structured = extract_json(raw_reply)
            # If the LLM didn't return structured JSON, synthesize a safe fallback so the system
            # can proceed as a caring friend and draft a complaint on the user's behalf.
            def synthesize_fallback(raw: str, message: str, understanding: dict):
                # Ensure friend-style reply contains encouragement to report when intent is complaint/cybercrime
                friend = raw.strip()
                low = friend.lower()
                if understanding.get('intent') in ('complaint', 'cybercrime') and not any(k in low for k in ("report", "complain", "file", "reporting", "report to", "report it")):
                    friend = friend + "\n\nI encourage you to report this incident to your bank and the platform's abuse team; I can help draft a complaint for you." 

                # Build a simple complaint draft from available info
                who = ""
                what = message
                when = ""
                where = ""
                evidence = "Screenshots of suspicious activity, transaction records, timestamps, message headers if available."
                desired = "Refund/chargeback and investigation" if 'money' in message.lower() or 'transaction' in message.lower() else "Investigation and remedial action"

                complaint = (
                    f"Complaint summary:\nUser reports: {what}\n\nSuggested actions:\n1) Contact your bank's fraud department and request a chargeback.\n2) Report the incident to the platform via their abuse/report form.\n3) Preserve evidence: {evidence}\n4) Change passwords and enable 2FA.\n\nDesired outcome: {desired}\n"
                )

                metadata = {"who": who, "what": what, "when": when, "where": where, "evidence": evidence, "desired_outcome": desired}
                return {"friend_reply": friend, "complaint_draft": complaint, "metadata": metadata}

            if structured and isinstance(structured, dict) and 'friend_reply' in structured:
                candidate_reply = structured.get('friend_reply', '')
            else:
                structured = synthesize_fallback(raw_reply, text, understanding)
                candidate_reply = structured.get('friend_reply', '')
        except Exception as e:
            candidate_reply = "I'm sorry, I'm having trouble generating a reply right now. Please reach out to a trusted person or emergency services if you're in immediate danger."

        checked = filter_agent.process(candidate_reply, understanding)
        if checked.get("ok"):
            print("\nAssistant:")
            # Sanitize reply: replace external hotline mentions with TrustLine contact
            def sanitize_reply(text: str) -> str:
                low = text.lower()
                # common external hotline phrases to remove
                bad_phrases = [
                    'national suicide prevention',
                    '1-800-273-talk',
                    '741741',
                    'crisis text line',
                    'national domestic violence hotline',
                    '1-800-799-7233',
                    'national center for victims of crime',
                ]
                for bp in bad_phrases:
                    if bp in low:
                        # simple removal: replace occurrences using case-insensitive approach
                        import re

                        text = re.sub(re.escape(bp), 'TrustLine (see contact below)', text, flags=re.IGNORECASE)
                # Ensure TrustLine demo contact appears
                if 'trustline' not in text.lower():
                    text = text + "\n\nTrustLine Helpline (demo): +94-11-0000000 | Email: support@trustline.example"
                return text

            reply_to_show = sanitize_reply(checked.get("reply") or "")
            print(reply_to_show)
            # If the LLM provided structured complaint data, consider creating or updating a case
            try:
                if structured and isinstance(structured, dict):
                    complaint = structured.get('complaint_draft', '').strip()
                    metadata = structured.get('metadata', {}) or {}
                    if complaint or any(v for v in metadata.values()):
                        from app.utils.complaint_handler import create_case, update_case, find_duplicate, load_case
                        import os

                        record = {
                            'user_input': text,
                            'understanding': understanding,
                            'complaint_draft': complaint,
                            'metadata': metadata,
                        }

                        # If this conversation already has a linked case, update it instead
                        if session_case_id:
                            cid = session_case_id
                            # merge into existing case
                            update_case(cid, record)
                            print(f"\n[Case updated: {cid}]")
                        else:
                            # If user message suggests they already submitted a case, ask before creating another
                            if _looks_like_existing_case_message(text):
                                try:
                                    resp_link = input("Mithuru: It sounds like you already submitted a case. Would you like me to link this conversation to that case? (yes/no)\nYou: ")
                                except EOFError:
                                    resp_link = "no"
                                if resp_link and resp_link.strip().lower().startswith('y'):
                                    try:
                                        ask_id = input("Mithuru: Please paste the case id (e.g. TL-20260326-1234) or type 'no' to cancel:\nYou: ")
                                    except EOFError:
                                        ask_id = ""
                                    if ask_id and ask_id.strip().lower() not in ('no', 'skip'):
                                        cid_try = ask_id.strip()
                                        # verify file exists
                                        cpath = os.path.join(os.getcwd(), 'complaints', f"{cid_try}.json")
                                        if os.path.exists(cpath):
                                            session_case_id = cid_try
                                            update_case(session_case_id, record)
                                            print(f"\n[Linked and updated existing case: {session_case_id}]")
                                            cid = session_case_id
                                        else:
                                            print("Mithuru: I couldn't find that case id. I'll create a new case unless you say otherwise.")
                                            cid = create_case(record)
                                            session_case_id = cid
                                            print(f"\n[Case created: {cid}]")
                                    else:
                                        # user declined to provide id; create new case
                                        cid = create_case(record)
                                        session_case_id = cid
                                        print(f"\n[Case created: {cid}]")
                                else:
                                    cid = create_case(record)
                                    session_case_id = cid
                                    print(f"\n[Case created: {cid}]")
                            else:
                                # If the user seems to need immediate emotional support (alone/distressed), defer case creation
                                if _user_needs_support(text, understanding):
                                    cid = None
                                    print("\n[Mithuru: I hear you — let's focus on supporting you right now before submitting or updating any case.]")
                                else:
                                    # Prevent duplicate complaint creation for same incident
                                    dup_cid = find_duplicate(record)
                                    if dup_cid:
                                        session_case_id = dup_cid
                                        update_case(session_case_id, record)
                                        print(f"\n[Duplicate detected: updated existing case {session_case_id}]")
                                    else:
                                        cid = create_case(record)
                                        session_case_id = cid
                                        print(f"\n[Case created: {cid}]")
                        # Mark that a complaint has been submitted in this session
                        complaint_submitted = True
                        post_complaint_mode = True

                        # Adaptive friend-style follow-up for missing but useful fields
                        intent = understanding.get('intent', '')
                        # Default: always ask for name, phone, address, guardian
                        missing_prompts = [
                            ("who", "If you're comfortable, may I have your full name? (or type 'skip')"),
                            ("phone", "Can you share a phone number we can reach you at? (or type 'skip')"),
                            ("address", "If you're comfortable, please share an address for the report (or type 'skip')"),
                            ("guardian_phone", "If you'd like, provide a guardian or family member phone number we can contact (or type 'skip')"),
                        ]
                        # For cybercrime/financial cases, ask for evidence and platform, but skip group/photo/ex-partner
                        if intent == "cybercrime" or ("bank" in text.lower() or "account" in text.lower() or "money" in text.lower()):
                            missing_prompts += [
                                ("platform", "Which platform or service was affected (e.g., bank name, website, app)? (or type 'skip')"),
                                ("evidence", "Do you have transaction records, screenshots, or other evidence? (or type 'skip')"),
                            ]
                        # For privacy/photo leak/harassment, ask for group, links, publisher, shared_with, evidence
                        elif any(k in text.lower() for k in ["photo", "leak", "expose", "image", "video", "harass", "bully", "porn", "group", "channel"]):
                            missing_prompts += [
                                ("platform", "Which platform was the content shared on (e.g., Telegram, website)? (or type 'skip')"),
                                ("group_name", "Do you know the name of the group or channel where the photos/videos were shared? (or type 'skip')"),
                                ("links", "If you have direct links to the posts or group, please paste them now (or type 'skip')"),
                                ("publisher_name", "Do you know who published these (a username or real name)? (or type 'skip')"),
                                ("shared_with", "Did you previously share these photos/videos with anyone you know (e.g., ex-partner)? (please answer or type 'skip')"),
                                ("evidence", "Do you have screenshots or other evidence you can upload or paste? (or type 'skip')"),
                            ]
                        # For general support/distress, only ask for contact info if needed
                        else:
                            pass  # Only the default prompts

                        updates = {}
                        for key, prompt_text in missing_prompts:
                            # If metadata already has value, skip
                            if metadata.get(key):
                                continue
                            try:
                                resp = input(f"\nMithuru: {prompt_text}\nYou: ")
                            except EOFError:
                                resp = "skip"
                            if not resp or resp.strip().lower() == "skip":
                                continue
                            updates.setdefault('metadata', {})
                            updates['metadata'][key] = resp.strip()
                            metadata[key] = resp.strip()
                            # Persist update to case file
                            if cid:
                                update_case(cid, {'metadata': metadata})

                        if updates and cid:
                            print(f"\n[Case {cid} updated with additional info]")

                        # Determine whether to run calming follow-ups: run if we have a case OR user needs support
                        need_support = _user_needs_support(text, understanding)
                        if cid or need_support:
                            # Continue the conversation with calming follow-ups (friend-style)
                            try:
                                # Ask gentle wellbeing questions
                                resp = input("\nMithuru: Thank you — your complaint is submitted and our team will review it. Do you feel safe right now? (yes/no or describe)\nYou: ")
                            except EOFError:
                                resp = ""
                            if resp and resp.strip().lower() in ("no", "not safe", "unsafe"):
                                # Use LLM to generate a concise, caring follow-up message and request permission to contact a trusted person.
                                try:
                                    follow_prompt = (
                                        "You are Mithuru, a caring TrustLine assistant. The user reports they do not feel safe right now. "
                                        "Produce a short (1-2 sentences) empathetic message offering immediate calming steps and ask: 'May we contact a trusted person or your listed contact now? (yes/skip)'. "
                                        "Do NOT mention emergency services or external crisis hotlines. Keep tone gentle and concise."
                                    )
                                    follow = llm.generate(follow_prompt, max_tokens=120)
                                except Exception:
                                    follow = "I'm sorry you're not feeling safe. May we contact a trusted person you listed now? (yes/skip)"
                                print("Mithuru: " + follow)
                                try:
                                    contact_now = input("You: ")
                                except EOFError:
                                    contact_now = "skip"
                                if contact_now and contact_now.strip().lower() == "yes":
                                    print("Mithuru: Our TrustLine team will reach out using the contact details you provided.")
                                    if cid:
                                        update_case(cid, {"status": "escalated_contact_requested"})
                                else:
                                    print("Mithuru: Okay — I'm here with you. If you'd like, I can stay and talk, or we can try other steps to help you feel safer.")
                        else:
                            # Ask a concise follow-up via LLM: are you with someone you trust?
                            try:
                                follow_prompt2 = (
                                    "You are Mithuru, a caring TrustLine assistant. Ask the user one short question: 'Are you currently with someone you trust who can stay with you? (yes/no)'. "
                                    "Keep the prompt gentle and no more than one sentence."
                                )
                                q = llm.generate(follow_prompt2, max_tokens=40)
                            except Exception:
                                q = "Are you currently with someone you trust who can stay with you? (yes/no)"
                            try:
                                resp2 = input(f"Mithuru: {q}\nYou: ")
                            except EOFError:
                                resp2 = ""
                            if resp2 and resp2.strip().lower() in ("no", "n"):
                                try:
                                    ask_prompt = (
                                        "You are Mithuru. Provide one short sentence offering to contact a trusted person the user listed, and a second short sentence offering to stay with them in chat. Keep both sentences concise and kind."
                                    )
                                    offer = llm.generate(ask_prompt, max_tokens=80)
                                except Exception:
                                    offer = "If you'd like, we can try to contact a trusted person you listed; otherwise I can stay here and continue to help you."
                                print("Mithuru: " + offer)
                                try:
                                    stay = input("You: ")
                                except EOFError:
                                    stay = ""
                                if stay and stay.strip().lower() in ("yes", "ok", "please"):
                                    print("Mithuru: I'll note that and our team will follow up. You're not alone.")
                                    update_case(cid, {"support_requested": True})
                        # End calming follow-ups
            except Exception as e:
                # Keep pipeline robust; print debug message but continue
                try:
                    print("[Warning] case logging failed:", str(e))
                except Exception:
                    pass
        else:
            # If filter failed, produce safe fallback and flag escalation
            print("\nAssistant: (filtered)")
            print("I'm concerned about your safety. I recommend contacting local emergency services or a trusted person right now.")
            print(f"[Filter reason: {checked.get('reason')}]")


if __name__ == "__main__":
    main()
