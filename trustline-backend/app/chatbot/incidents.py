"""Incident type definitions and field schemas for Mithuru complaint intake.

Each incident type has a schema of prioritised fields with compassionate
question phrasing and extraction keywords for auto-detection from free text.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class IncidentType(str, Enum):
    PHOTO_LEAK = "photo_leak"
    SEXTORTION = "sextortion"
    PORN_SITE_UPLOAD = "porn_site_upload"
    BANK_FRAUD = "bank_fraud"
    ACCOUNT_HACK = "account_hack"
    SOCIAL_MEDIA_HACK = "social_media_hack"
    IMPERSONATION = "impersonation"
    CYBERBULLYING = "cyberbullying"
    HARASSMENT = "harassment"
    SCAM = "scam"
    BLACKMAIL = "blackmail"
    GENERAL_CYBERCRIME = "general_cybercrime"


class FieldPriority(int, Enum):
    FIRST = 0       # Personal identification — asked first (e.g., full name)
    URGENT = 1      # Determines immediate action
    HIGH = 2        # Core evidence / facts
    MEDIUM = 3      # Important context
    LOW = 4         # Nice to have
    CONTACT = 5     # Legacy


@dataclass
class FieldSpec:
    key: str
    label: str
    question: str                       # Compassionate phrasing for asking
    priority: FieldPriority
    field_type: str = "text"            # text | boolean | url | phone | date | amount | choice
    required: bool = True
    extraction_keywords: tuple = ()     # Keywords that hint at this field in free text
    choices: tuple = ()                 # For choice-type fields


# ─────────────────────────────────────────────────────────────
# Common contact fields (shared across all incident types)
# ─────────────────────────────────────────────────────────────

COMMON_CONTACT_FIELDS = [
    FieldSpec(
        key="victim_name",
        label="Full name",
        question="Can you tell me your full name so I can start your complaint?",
        priority=FieldPriority.FIRST,
        required=True,
    ),
    FieldSpec(
        key="victim_phone",
        label="Phone number",
        question="What phone number can our team reach you on?",
        priority=FieldPriority.MEDIUM,
        field_type="phone",
        required=True,
    ),
    FieldSpec(
        key="victim_address",
        label="Address",
        question="Can you share your address for the complaint record? You can skip this if you prefer.",
        priority=FieldPriority.LOW,
        required=False,
    ),
    FieldSpec(
        key="guardian_phone",
        label="Guardian or trusted-person phone",
        question="Is there a trusted person whose contact we could have just in case?",
        priority=FieldPriority.LOW,
        field_type="phone",
        required=False,
    ),
]


# ─────────────────────────────────────────────────────────────
# Photo-leak / Porn-site upload
# ─────────────────────────────────────────────────────────────

PHOTO_LEAK_FIELDS = [
    FieldSpec(
        key="content_still_live",
        label="Content still visible",
        question="Is the content still visible online right now? This helps us know how urgently we need to act.",
        priority=FieldPriority.URGENT,
        field_type="boolean",
        extraction_keywords=("still up", "still online", "still there", "still live",
                             "still visible", "taken down", "removed"),
    ),
    FieldSpec(
        key="platform_name",
        label="Platform or website",
        question="Which platform or website was the content shared on?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("telegram", "whatsapp", "facebook", "instagram", "twitter",
                             "tiktok", "snapchat", "reddit", "pornhub", "xvideos",
                             "onlyfans", "xhamster", "xnxx"),
    ),
    FieldSpec(
        key="content_type",
        label="Type of content",
        question="What kind of content was shared — photos, videos, or both?",
        priority=FieldPriority.HIGH,
        field_type="choice",
        choices=("photos", "videos", "both", "other"),
        extraction_keywords=("photo", "image", "picture", "video", "clip", "recording"),
    ),
    FieldSpec(
        key="platform_link",
        label="Link to content",
        question="If you have a link to where the content is posted, please share it. This helps us act faster. Don't worry if you don't have it.",
        priority=FieldPriority.HIGH,
        field_type="url",
        required=False,
        extraction_keywords=("http", "https", "www.", ".com", ".org", "link"),
    ),
    FieldSpec(
        key="when_discovered",
        label="When discovered",
        question="When did you first find out about this?",
        priority=FieldPriority.MEDIUM,
        field_type="date",
        extraction_keywords=("today", "yesterday", "last week", "found out",
                             "discovered", "noticed", "just now", "hours ago", "days ago"),
    ),
    FieldSpec(
        key="suspect_known",
        label="Suspect known",
        question="Do you have any idea who might have done this?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("ex", "boyfriend", "girlfriend", "ex-partner", "friend",
                             "someone i know", "stranger", "don't know", "no idea"),
    ),
    FieldSpec(
        key="suspect_relationship",
        label="Relationship to suspect",
        question="What is your relationship to this person?",
        priority=FieldPriority.MEDIUM,
        required=False,
        extraction_keywords=("ex-boyfriend", "ex-girlfriend", "ex-partner", "friend",
                             "colleague", "stranger", "classmate"),
    ),
    FieldSpec(
        key="blackmail_present",
        label="Blackmail involved",
        question="Is anyone threatening you or asking for something in exchange?",
        priority=FieldPriority.HIGH,
        field_type="boolean",
        extraction_keywords=("blackmail", "threaten", "demand", "pay", "money",
                             "asking for", "unless i", "or else"),
    ),
    FieldSpec(
        key="threats_present",
        label="Threats received",
        question="Have you received any direct threats related to this?",
        priority=FieldPriority.HIGH,
        field_type="boolean",
        required=False,
        extraction_keywords=("threat", "threaten", "kill", "hurt", "expose",
                             "spread", "share more"),
    ),
    FieldSpec(
        key="screenshots_available",
        label="Screenshots or evidence",
        question="Have you been able to take any screenshots or save any evidence? It's okay if you haven't yet.",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("screenshot", "screen shot", "saved", "evidence",
                             "proof", "recorded"),
    ),
]


# ─────────────────────────────────────────────────────────────
# Sextortion
# ─────────────────────────────────────────────────────────────

SEXTORTION_FIELDS = [
    FieldSpec(
        key="threats_ongoing",
        label="Threats ongoing",
        question="Is this person still actively threatening you?",
        priority=FieldPriority.URGENT,
        field_type="boolean",
        extraction_keywords=("still threatening", "keeps messaging", "won't stop", "ongoing"),
    ),
    FieldSpec(
        key="content_type",
        label="Content involved",
        question="What type of content are they threatening with — photos, videos, or conversations?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("photo", "video", "nude", "intimate", "private",
                             "conversation", "chat"),
    ),
    FieldSpec(
        key="demands",
        label="Their demands",
        question="What are they asking you to do or pay?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("money", "pay", "send more", "meet", "do something",
                             "bitcoin", "demanding"),
    ),
    FieldSpec(
        key="content_already_shared",
        label="Content already leaked",
        question="Have they already shared or posted any of your content somewhere?",
        priority=FieldPriority.HIGH,
        field_type="boolean",
        extraction_keywords=("already shared", "posted", "uploaded", "sent to friends", "leaked"),
    ),
    FieldSpec(
        key="suspect_known",
        label="Suspect identity",
        question="Do you know who this person is, or did you meet them online?",
        priority=FieldPriority.MEDIUM,
        extraction_keywords=("know them", "met online", "stranger", "dating app",
                             "ex", "someone i know"),
    ),
    FieldSpec(
        key="platform_used",
        label="Platform",
        question="Which platform did they contact you through?",
        priority=FieldPriority.MEDIUM,
        extraction_keywords=("telegram", "whatsapp", "instagram", "snapchat",
                             "facebook", "dating app", "tinder"),
    ),
    FieldSpec(
        key="money_paid",
        label="Money paid",
        question="Have you sent them any money already? It's okay — many people do under pressure. This is not your fault.",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        required=False,
        extraction_keywords=("paid", "sent money", "transferred"),
    ),
    FieldSpec(
        key="screenshots_available",
        label="Evidence",
        question="Have you been able to save any screenshots of their threats or messages?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("screenshot", "evidence", "saved", "proof"),
    ),
]


# ─────────────────────────────────────────────────────────────
# Bank fraud
# ─────────────────────────────────────────────────────────────

BANK_FRAUD_FIELDS = [
    FieldSpec(
        key="unauthorized_transactions_ongoing",
        label="Transactions still happening",
        question="Are unauthorized transactions still happening right now? If so, we need to act very quickly.",
        priority=FieldPriority.URGENT,
        field_type="boolean",
        extraction_keywords=("still happening", "still going", "ongoing",
                             "more transactions", "keep taking", "still taking",
                             "still transferring", "stopped"),
    ),
    FieldSpec(
        key="bank_name",
        label="Bank name",
        question="Which bank is your account with?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("boc", "nsb", "commercial bank", "hnb", "sampath",
                             "peoples bank", "seylan", "dfcc", "ndb",
                             "bank of ceylon", "nations trust", "pan asia"),
    ),
    FieldSpec(
        key="amount_lost",
        label="Amount lost",
        question="Do you know approximately how much money was taken?",
        priority=FieldPriority.HIGH,
        field_type="amount",
        extraction_keywords=("rs", "lkr", "rupees", "lakhs", "thousand",
                             "lost", "taken", "stolen", "missing"),
    ),
    FieldSpec(
        key="branch_name",
        label="Branch name",
        question="Which branch is the account linked to?",
        priority=FieldPriority.HIGH,
        required=False,
        extraction_keywords=("branch",),
    ),
    FieldSpec(
        key="account_number",
        label="Account number",
        question="What is the affected account number?",
        priority=FieldPriority.HIGH,
        required=False,
        extraction_keywords=("account number", "acc no", "account no"),
    ),
    FieldSpec(
        key="bank_contacted",
        label="Bank contacted",
        question="Have you contacted your bank about this yet?",
        priority=FieldPriority.HIGH,
        field_type="boolean",
        extraction_keywords=("called bank", "told bank", "bank said",
                             "bank knows", "reported to bank", "haven't told"),
    ),
    FieldSpec(
        key="transaction_time",
        label="When it happened",
        question="When did the unauthorized transaction happen — do you remember the date or time?",
        priority=FieldPriority.MEDIUM,
        field_type="date",
        extraction_keywords=("today", "yesterday", "last night", "morning", "hours ago"),
    ),
    FieldSpec(
        key="otp_shared",
        label="OTP or credentials shared",
        question="Did you happen to share any OTP codes, passwords, or login details with anyone recently? No judgment at all — this helps us understand how it happened.",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("otp", "password", "pin", "code", "gave",
                             "shared", "told someone", "link clicked", "phishing"),
    ),
    FieldSpec(
        key="transaction_reference",
        label="Transaction reference",
        question="Do you have a transaction reference number or receipt? You can share it later if you don't have it now.",
        priority=FieldPriority.MEDIUM,
        required=False,
        extraction_keywords=("reference", "receipt", "transaction id", "ref no"),
    ),
    FieldSpec(
        key="compromised_device",
        label="Device compromised",
        question="Do you think your phone or computer might have been compromised — for example, did you install any unfamiliar app recently?",
        priority=FieldPriority.LOW,
        required=False,
        extraction_keywords=("phone", "computer", "laptop", "app", "installed",
                             "malware", "virus", "hacked device"),
    ),
    FieldSpec(
        key="screenshots_available",
        label="Evidence",
        question="Do you have screenshots of the transactions or any messages related to this?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("screenshot", "screen shot", "saved", "evidence", "proof"),
    ),
]


# ─────────────────────────────────────────────────────────────
# Account hack / Social media hack
# ─────────────────────────────────────────────────────────────

ACCOUNT_HACK_FIELDS = [
    FieldSpec(
        key="still_has_access",
        label="Still have access",
        question="Can you still log into your account right now, or have you been locked out?",
        priority=FieldPriority.URGENT,
        field_type="boolean",
        extraction_keywords=("locked out", "cant login", "can't log in", "no access",
                             "still have access", "changed password", "password changed"),
    ),
    FieldSpec(
        key="platform_name",
        label="Platform",
        question="Which platform or account was hacked?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("facebook", "instagram", "whatsapp", "gmail", "email",
                             "twitter", "tiktok", "snapchat", "linkedin", "youtube"),
    ),
    FieldSpec(
        key="email_changed",
        label="Email changed by hacker",
        question="Has the email address linked to your account been changed?",
        priority=FieldPriority.HIGH,
        field_type="boolean",
        extraction_keywords=("email changed", "new email", "different email", "can't recover"),
    ),
    FieldSpec(
        key="phone_changed",
        label="Phone changed by hacker",
        question="Has the phone number linked to your account been changed?",
        priority=FieldPriority.HIGH,
        field_type="boolean",
        required=False,
        extraction_keywords=("phone changed", "new number", "different phone"),
    ),
    FieldSpec(
        key="suspicious_posts",
        label="Suspicious activity",
        question="Has anything been posted or sent from your account that you didn't do?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("posted", "sent messages", "spam", "weird messages",
                             "scam messages", "asked friends for money"),
    ),
    FieldSpec(
        key="friends_targeted",
        label="Contacts targeted",
        question="Have your friends or contacts been targeted from your hacked account?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        required=False,
        extraction_keywords=("friends", "contacts", "messaged people",
                             "scam messages to friends"),
    ),
    FieldSpec(
        key="username_or_link",
        label="Account link or username",
        question="Can you share the username or link of the hacked account?",
        priority=FieldPriority.MEDIUM,
        required=False,
        extraction_keywords=("username", "profile", "account name", "@", "link"),
    ),
    FieldSpec(
        key="screenshots_available",
        label="Evidence",
        question="Do you have any screenshots showing the hack or suspicious activity?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("screenshot", "screen shot", "evidence", "proof"),
    ),
]


# ─────────────────────────────────────────────────────────────
# Blackmail
# ─────────────────────────────────────────────────────────────

BLACKMAIL_FIELDS = [
    FieldSpec(
        key="threats_ongoing",
        label="Threats ongoing",
        question="Is the person still actively threatening you right now?",
        priority=FieldPriority.URGENT,
        field_type="boolean",
        extraction_keywords=("still threatening", "keeps messaging",
                             "won't stop", "ongoing", "continues"),
    ),
    FieldSpec(
        key="blackmail_content_type",
        label="What they are using",
        question="What are they using to threaten you — photos, videos, personal information, or something else?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("photo", "video", "information", "secret",
                             "message", "chat", "data"),
    ),
    FieldSpec(
        key="demands",
        label="What they are demanding",
        question="What are they asking for — money, more content, or something else?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("money", "pay", "send", "more photos",
                             "meet", "do something", "demanding"),
    ),
    FieldSpec(
        key="suspect_known",
        label="Suspect known",
        question="Do you know who this person is?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("know them", "don't know", "stranger",
                             "anonymous", "ex", "someone online"),
    ),
    FieldSpec(
        key="platform_used",
        label="Platform for threats",
        question="Which platform are they contacting you through?",
        priority=FieldPriority.MEDIUM,
        extraction_keywords=("telegram", "whatsapp", "instagram", "email",
                             "phone", "sms", "messenger"),
    ),
    FieldSpec(
        key="money_paid",
        label="Money already paid",
        question="Have you already sent them any money? Please don't feel ashamed — this is very common and not your fault.",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        required=False,
        extraction_keywords=("paid", "sent money", "transferred", "gave money"),
    ),
    FieldSpec(
        key="evidence_available",
        label="Evidence saved",
        question="Have you saved the conversations or threats as screenshots?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("screenshot", "saved", "evidence", "proof", "recorded"),
    ),
]


# ─────────────────────────────────────────────────────────────
# Cyberbullying
# ─────────────────────────────────────────────────────────────

CYBERBULLYING_FIELDS = [
    FieldSpec(
        key="harassment_ongoing",
        label="Still happening",
        question="Is this still happening right now?",
        priority=FieldPriority.URGENT,
        field_type="boolean",
        extraction_keywords=("still happening", "keeps going", "every day",
                             "ongoing", "won't stop", "stopped"),
    ),
    FieldSpec(
        key="platform_name",
        label="Platform",
        question="Which platform is this happening on?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("facebook", "instagram", "tiktok", "twitter",
                             "whatsapp", "snapchat"),
    ),
    FieldSpec(
        key="harassment_type",
        label="Type of bullying",
        question="Can you tell me a bit more about what they're doing — is it name-calling, spreading rumors, threats, or something else?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("insults", "name calling", "rumors", "spreading lies",
                             "fake accounts", "hate messages", "mocking"),
    ),
    FieldSpec(
        key="suspect_known",
        label="Bully known",
        question="Do you know who is doing this?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("classmate", "school", "friend", "ex",
                             "know them", "don't know", "anonymous"),
    ),
    FieldSpec(
        key="frequency",
        label="How often",
        question="How often is this happening?",
        priority=FieldPriority.MEDIUM,
        extraction_keywords=("every day", "daily", "all the time", "constantly",
                             "once", "sometimes", "frequently"),
    ),
    FieldSpec(
        key="reported_to_platform",
        label="Reported to platform",
        question="Have you reported this on the platform itself?",
        priority=FieldPriority.LOW,
        field_type="boolean",
        required=False,
        extraction_keywords=("reported", "flagged", "blocked", "platform won't help"),
    ),
    FieldSpec(
        key="screenshots_available",
        label="Screenshots",
        question="Do you have screenshots of the bullying messages or posts?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("screenshot", "evidence", "saved", "proof"),
    ),
]


# ─────────────────────────────────────────────────────────────
# Harassment
# ─────────────────────────────────────────────────────────────

HARASSMENT_FIELDS = [
    FieldSpec(
        key="harassment_ongoing",
        label="Still happening",
        question="Is this person still contacting or harassing you?",
        priority=FieldPriority.URGENT,
        field_type="boolean",
        extraction_keywords=("still", "keeps", "won't stop", "ongoing", "continues"),
    ),
    FieldSpec(
        key="platform_name",
        label="Platform",
        question="Where is the harassment happening — which platform or method?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("facebook", "instagram", "whatsapp", "phone",
                             "email", "sms", "in person", "calls"),
    ),
    FieldSpec(
        key="harassment_type",
        label="Type of harassment",
        question="What kind of harassment is this — threatening messages, stalking, unwanted contact, or something else?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("stalk", "follow", "threat", "unwanted",
                             "creepy", "messages", "calls", "showing up"),
    ),
    FieldSpec(
        key="suspect_known",
        label="Harasser known",
        question="Do you know who is doing this?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("know them", "ex", "stranger", "colleague", "neighbor"),
    ),
    FieldSpec(
        key="threats_present",
        label="Threats received",
        question="Have they made any threats toward you or your family?",
        priority=FieldPriority.HIGH,
        field_type="boolean",
        extraction_keywords=("threat", "kill", "hurt", "harm", "destroy"),
    ),
    FieldSpec(
        key="screenshots_available",
        label="Evidence",
        question="Do you have screenshots or recordings of the harassment?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("screenshot", "recording", "evidence", "saved"),
    ),
]


# ─────────────────────────────────────────────────────────────
# Impersonation
# ─────────────────────────────────────────────────────────────

IMPERSONATION_FIELDS = [
    FieldSpec(
        key="platform_name",
        label="Platform",
        question="Which platform is the fake account on?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("facebook", "instagram", "whatsapp", "tiktok", "twitter"),
    ),
    FieldSpec(
        key="fake_account_link",
        label="Fake account link",
        question="Can you share the link or username of the fake account?",
        priority=FieldPriority.HIGH,
        field_type="url",
        extraction_keywords=("link", "profile", "username", "@", "account"),
    ),
    FieldSpec(
        key="impersonated_who",
        label="Who is being impersonated",
        question="Is this account pretending to be you, or someone you know?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("me", "my name", "my photos", "pretending to be",
                             "using my identity"),
    ),
    FieldSpec(
        key="purpose",
        label="Purpose of fake account",
        question="Do you know what the fake account is being used for — scamming people, damaging your reputation, or something else?",
        priority=FieldPriority.MEDIUM,
        extraction_keywords=("scam", "money", "reputation", "defame",
                             "harass", "trick people"),
    ),
    FieldSpec(
        key="reported_to_platform",
        label="Reported to platform",
        question="Have you reported the fake account to the platform?",
        priority=FieldPriority.LOW,
        field_type="boolean",
        required=False,
        extraction_keywords=("reported", "flagged", "platform", "nothing happened"),
    ),
    FieldSpec(
        key="contacts_targeted",
        label="People affected",
        question="Has anyone been contacted or scammed through the fake account?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        required=False,
        extraction_keywords=("friends", "family", "contacts",
                             "asked for money", "messaged"),
    ),
    FieldSpec(
        key="screenshots_available",
        label="Evidence",
        question="Do you have screenshots of the fake account?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("screenshot", "evidence", "saved"),
    ),
]


# ─────────────────────────────────────────────────────────────
# Scam
# ─────────────────────────────────────────────────────────────

SCAM_FIELDS = [
    FieldSpec(
        key="money_lost",
        label="Money lost",
        question="Did you lose any money? Do you know how much?",
        priority=FieldPriority.URGENT,
        field_type="boolean",
        extraction_keywords=("lost", "paid", "transferred", "sent money",
                             "rs", "lkr", "amount"),
    ),
    FieldSpec(
        key="scam_type",
        label="Type of scam",
        question="Can you describe what kind of scam this was — an investment scam, fake product, phishing link, lottery scam, or something else?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("investment", "bitcoin", "crypto", "fake product",
                             "phishing", "lottery", "job offer", "prize", "gift card"),
    ),
    FieldSpec(
        key="platform_or_method",
        label="How they contacted you",
        question="How did the scammer contact you — social media, phone, email, or a website?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("facebook", "whatsapp", "phone call", "email",
                             "website", "sms", "link"),
    ),
    FieldSpec(
        key="scammer_contact_info",
        label="Scammer details",
        question="Do you have any details about the scammer — a phone number, username, account, or website?",
        priority=FieldPriority.MEDIUM,
        required=False,
        extraction_keywords=("number", "username", "account", "website", "profile"),
    ),
    FieldSpec(
        key="transaction_details",
        label="Transaction info",
        question="If you sent money, do you remember the method — bank transfer, card payment, or cryptocurrency?",
        priority=FieldPriority.MEDIUM,
        required=False,
        extraction_keywords=("bank transfer", "card", "bitcoin", "crypto",
                             "western union", "cash"),
    ),
    FieldSpec(
        key="screenshots_available",
        label="Evidence",
        question="Do you have screenshots of the scam messages, website, or transactions?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("screenshot", "evidence", "saved", "proof"),
    ),
]


# ─────────────────────────────────────────────────────────────
# General cybercrime (catch-all)
# ─────────────────────────────────────────────────────────────

GENERAL_FIELDS = [
    FieldSpec(
        key="incident_description",
        label="What happened",
        question="Can you tell me more about what happened?",
        priority=FieldPriority.HIGH,
    ),
    FieldSpec(
        key="platform_or_method",
        label="Platform or method",
        question="Where or how did this happen — which platform, app, or method?",
        priority=FieldPriority.HIGH,
        extraction_keywords=("facebook", "instagram", "whatsapp", "email",
                             "phone", "website"),
    ),
    FieldSpec(
        key="suspect_known",
        label="Suspect known",
        question="Do you know or suspect who is behind this?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
    ),
    FieldSpec(
        key="evidence_available",
        label="Evidence",
        question="Do you have any evidence or screenshots related to this?",
        priority=FieldPriority.MEDIUM,
        field_type="boolean",
        extraction_keywords=("screenshot", "evidence", "proof"),
    ),
    FieldSpec(
        key="police_contacted",
        label="Police contacted",
        question="Have you reported this to the police or any other authority?",
        priority=FieldPriority.LOW,
        field_type="boolean",
        required=False,
        extraction_keywords=("police", "reported", "authorities", "filed"),
    ),
]


# ─────────────────────────────────────────────────────────────
# Schema registry
# ─────────────────────────────────────────────────────────────

INCIDENT_SCHEMAS: dict[str, list[FieldSpec]] = {
    IncidentType.PHOTO_LEAK.value: PHOTO_LEAK_FIELDS,
    IncidentType.PORN_SITE_UPLOAD.value: PHOTO_LEAK_FIELDS,       # same schema
    IncidentType.SEXTORTION.value: SEXTORTION_FIELDS,
    IncidentType.BANK_FRAUD.value: BANK_FRAUD_FIELDS,
    IncidentType.ACCOUNT_HACK.value: ACCOUNT_HACK_FIELDS,
    IncidentType.SOCIAL_MEDIA_HACK.value: ACCOUNT_HACK_FIELDS,    # same schema
    IncidentType.IMPERSONATION.value: IMPERSONATION_FIELDS,
    IncidentType.CYBERBULLYING.value: CYBERBULLYING_FIELDS,
    IncidentType.HARASSMENT.value: HARASSMENT_FIELDS,
    IncidentType.SCAM.value: SCAM_FIELDS,
    IncidentType.BLACKMAIL.value: BLACKMAIL_FIELDS,
    IncidentType.GENERAL_CYBERCRIME.value: GENERAL_FIELDS,
}


# ── Helpers ──

def get_schema_for_incident(incident_type: str) -> list[FieldSpec]:
    return INCIDENT_SCHEMAS.get(incident_type, GENERAL_FIELDS)


def get_required_fields(incident_type: str) -> list[str]:
    return [f.key for f in get_schema_for_incident(incident_type) if f.required]


def get_all_field_keys(incident_type: str) -> list[str]:
    return [f.key for f in get_schema_for_incident(incident_type)]


def get_field_spec(incident_type: str, field_key: str) -> Optional[FieldSpec]:
    for f in get_schema_for_incident(incident_type):
        if f.key == field_key:
            return f
    for f in COMMON_CONTACT_FIELDS:
        if f.key == field_key:
            return f
    return None
