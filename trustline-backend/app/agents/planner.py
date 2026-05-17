from typing import Dict, List

class PlannerAgent:
    """Generates a list of instructions/rules for the chatbot agent based on the understanding."""

    def process(self, understanding: Dict) -> List[str]:
        rules = []
        suicide = understanding.get("suicide_risk", False)
        emotion = understanding.get("emotion_label", "neutral")
        # 1. Calm and validate
        rules.append(f"Step 1: Greet user by name if known. Calm and validate feelings. Say: 'You are not alone. This is not your fault.' Reflect emotion: {emotion}.")
        # 2. Explain TrustLine
        rules.append("Step 2: Briefly explain TrustLine helps victims of online harm and is here to support.")
        # 3. Encourage action
        if understanding.get("intent") in ("complaint", "cybercrime"):
            rules.append("Step 3: Encourage user to file a complaint/report. Offer to help draft and submit. Assure this is manageable and TrustLine will act quickly.")
        else:
            rules.append("Step 3: Offer support and ask if user wants to proceed with a complaint or just talk.")
        # 4. Collect info (stepwise)
        rules.append("Step 4: Collect info one at a time: full name, phone, address, guardian contact, platform, group/links/evidence, suspects/shared with.")
        # 5. Confirm complaint
        rules.append("Step 5: Confirm complaint submitted and assure quick action.")
        # 6. Safety check and adaptive follow-up
        rules.append("Step 6: Ask if someone is with user (family/friend). If not, offer extra support, hotline, and say TrustLine will reach out. If yes, encourage sharing with trusted family and reinforce victim is not at fault.")
        # 7. Escalation for suicide/self-harm
        if suicide:
            rules.append("PRIORITY: User shows suicide/self-harm risk. Use extra calming, non-judgmental language. Offer hotline (1898 Mithuru), avoid normalizing self-harm, and escalate for immediate support.")
        # 8. Always filter for safety
        rules.append("All replies must be filtered for safety, banned phrases, and hotline compliance before sending to user.")
        return rules
