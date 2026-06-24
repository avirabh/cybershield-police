from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


SCAM_CATEGORIES = {
    "OTP Fraud",
    "UPI Fraud",
    "Fake KYC/Bank Alert",
    "Phishing",
    "Fake Job Scam",
    "Work From Home Scam",
    "Fake Loan Scam",
    "Lottery/Prize Scam",
    "Investment Scam",
    "Fake Customer Care Scam",
    "Courier/Parcel Scam",
    "Impersonation Scam",
    "Fake Police/Legal Threat",
    "QR Code Scam",
    "Unknown Suspicious",
    "Likely Safe",
}

CATEGORY_ALIASES = {
    "Fake Job Offer": "Fake Job Scam",
    "Impersonation": "Impersonation Scam",
    "Suspicious Link": "Phishing",
    "Insufficient Input": "Likely Safe",
}

TRUSTED_DOMAINS = {
    "sbi.co.in",
    "hdfcbank.com",
    "icicibank.com",
    "axisbank.com",
    "cisce.org",
    "results.cisce.org",
    "rbi.org.in",
    "uidai.gov.in",
    "gov.in",
    "digilocker.gov.in",
    "umang.gov.in",
    "india.gov.in",
    "incometax.gov.in",
    "cybercrime.gov.in",
    "npci.org.in",
    "google.com",
    "microsoft.com",
    "amazon.in",
    "amazon.com",
}

SHORTENER_DOMAINS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "cutt.ly",
    "rebrand.ly",
    "shorturl.at",
    "s.id",
}

SUSPICIOUS_TLDS = {
    ".xyz",
    ".top",
    ".click",
    ".icu",
    ".buzz",
    ".loan",
    ".work",
    ".zip",
    ".mov",
    ".rest",
    ".cam",
    ".country",
    ".support",
}

INSTITUTION_WORDS = [
    "bank",
    "rbi",
    "police",
    "cyber cell",
    "government",
    "income tax",
    "customs",
    "courier",
    "electricity",
    "telecom",
    "uidai",
    "aadhaar",
    "company",
    "support team",
    "school office",
    "college office",
]


@dataclass(frozen=True)
class DetectionRule:
    code: str
    label: str
    weight: int
    patterns: tuple[str, ...]
    categories: tuple[str, ...]
    evidence: str


TEXT_RULES: tuple[DetectionRule, ...] = (
    DetectionRule(
        code="multilingual_high_risk_phrase",
        label="Multilingual scam phrase match",
        weight=22,
        patterns=(
            r"ఓటీపీ.*(?:చెప్ప|ఇవ్వ|షేర్|పంప)",
            r"(?:ओटीपी|पिन|पासवर्ड).*(?:बताओ|भेजो|शेयर|डालो)",
            r"(?:ওটিপি|পিন|পাসওয়ার্ড).*(?:বলুন|পাঠান|শেয়ার|দিন)",
            r"(?:ఖాతా|అకౌంట్).*(?:బ్లాక్|మూసివేయ|ఫ్రీజ్)",
            r"(?:खाता|अकाउंट).*(?:ब्लॉक|बंद|फ्रीज)",
            r"(?:খাতা|অ্যাকাউন্ট).*(?:ব্লক|বন্ধ|ফ্রিজ)",
            r"యూపీఐ.*(?:రిఫండ్|పిన్|క్యూ\s*ఆర్)",
            r"यूपीआई.*(?:रिफंड|पिन|क्यूआर)",
            r"ইউপিআই.*(?:রিফান্ড|পিন|কিউআর)",
            r"(?:డిజిటల్\s+అరెస్ట్|అరెస్ట్).*(?:డబ్బు|చెల్లించ|సెటిల్)",
            r"(?:डिजिटल\s+अरेस्ट|गिरफ्तार).*(?:पैसे|भुगतान|सेटल)",
            r"(?:ডিজিটাল\s+অ্যারেস্ট|গ্রেফতার).*(?:টাকা|পেমেন্ট|সেটেল)",
            r"(?:ఉద్యోగం|नौकरी|চাকরি).*(?:ఫీజు|fee|शुल्क|টাকা|রেজিস্ট্রেশন)",
            r"(?:లోన్|लोन|ऋण|ঋণ).*(?:processing|ప్రాసెసింగ్|प्रोसेसिंग|প্রসেসিং|fee|फीस)",
            r"(?:పెట్టుబడి|निवेश|বিনিয়োগ).*(?:guaranteed|గ్యారంటీ|गारंटी|গ্যারান্টি|profit|లాభం|लाभ)",
            r"(?:కస్టమర్\s+కేర్|कस्टमर\s+केयर|কাস্টমার\s+কেয়ার).*(?:రిఫండ్|रिफंड|রিফান্ড|remote|రిమోట్)",
        ),
        categories=(
            "OTP Fraud",
            "UPI Fraud",
            "Fake KYC/Bank Alert",
            "Fake Police/Legal Threat",
            "Fake Job Scam",
            "Fake Loan Scam",
            "Investment Scam",
            "Fake Customer Care Scam",
        ),
        evidence="Matches common Telugu, Hindi, or Bengali scam phrases for OTP, KYC, UPI, digital arrest, job, loan, investment, or customer-care fraud.",
    ),
    DetectionRule(
        code="otp_code_request",
        label="OTP or verification code request",
        weight=28,
        patterns=(
            r"\botp\b",
            r"ओटीपी",
            r"ఓటీపీ",
            r"ওটিপি",
            r"one[-\s]?time\s+password",
            r"verification\s+code",
            r"सत्यापन\s+कोड",
            r"వెరిఫికేషన్\s+కోడ్",
            r"যাচাই\s+কোড",
            r"six[-\s]?digit\s+code",
            r"share\s+(?:your\s+)?(?:code|otp)",
            r"tell\s+(?:me|us)\s+(?:the\s+)?(?:code|otp)",
            r"enter\s+(?:the\s+)?otp",
        ),
        categories=("OTP Fraud", "UPI Fraud", "Phishing"),
        evidence="Requests an OTP or verification code, which should never be shared with callers or messages.",
    ),
    DetectionRule(
        code="pin_cvv_password_request",
        label="PIN, CVV, password, or credential request",
        weight=28,
        patterns=(
            r"\bupi\s*pin\b",
            r"\batm\s*pin\b",
            r"\bpin\b",
            r"पिन",
            r"పిన్",
            r"পিন",
            r"\bcvv\b",
            r"password",
            r"पासवर्ड",
            r"పాస్‌వర్డ్",
            r"పాస్వర్డ్",
            r"পাসওয়ার্ড",
            r"passcode",
            r"net\s*banking",
            r"login\s+(?:id|password|details)",
            r"card\s+(?:number|details)",
            r"debit\s+card",
            r"credit\s+card",
            r"credential",
        ),
        categories=("OTP Fraud", "UPI Fraud", "Phishing", "Fake KYC/Bank Alert"),
        evidence="Attempts to collect financial or account secrets such as PIN, CVV, passwords, or card details.",
    ),
    DetectionRule(
        code="kyc_account_threat",
        label="KYC or account-blocking threat",
        weight=30,
        patterns=(
            r"\bkyc\b",
            r"केवाईसी",
            r"కేవైసీ",
            r"కెవైసి",
            r"কেওয়াইসি",
            r"\baadhaar\b",
            r"\bpan\b",
            r"account\s+(?:will\s+be\s+)?(?:block|blocked|freeze|frozen|suspend|suspended|closed)",
            r"(?:खाता|अकाउंट).*(?:बंद|ब्लॉक|फ्रीज)",
            r"(?:ఖాతా|అకౌంట్).*(?:బ్లాక్|మూసి|ఫ్రీజ్)",
            r"(?:অ্যাকাউন্ট|খাতা).*(?:ব্লক|বন্ধ|ফ্রিজ)",
            r"(?:bank|wallet|sim)\s+(?:verification|reverification)",
            r"identity\s+verification",
            r"reactivate\s+(?:your\s+)?account",
            r"update\s+(?:your\s+)?(?:kyc|pan|aadhaar)",
        ),
        categories=("Fake KYC/Bank Alert", "Phishing", "Impersonation Scam"),
        evidence="Uses KYC, Aadhaar, PAN, or account blocking language common in fake bank and SIM alerts.",
    ),
    DetectionRule(
        code="phishing_login_verification",
        label="Login or account verification phishing request",
        weight=30,
        patterns=(
            r"login\s+to\s+verify",
            r"secure\s+login",
            r"verify\s+(?:your\s+)?(?:account|mailbox|profile|password)",
            r"password\s+verification",
            r"mailbox\s+(?:storage|security|verification)",
            r"account\s+security\s+check",
            r"update\s+(?:your\s+)?password",
        ),
        categories=("Phishing",),
        evidence="Pushes the user to login, verify, or update account credentials, a common phishing pattern.",
    ),
    DetectionRule(
        code="credential_harvesting_private_data",
        label="Private data or identity-document harvesting",
        weight=28,
        patterns=(
            r"upload\s+(?:your\s+)?(?:id|identity|aadhaar|pan|documents?)",
            r"submit\s+(?:your\s+)?(?:aadhaar|pan|bank\s+details|account\s+number|ifsc|dob|date\s+of\s+birth)",
            r"enter\s+(?:your\s+)?(?:aadhaar|pan|bank\s+details|account\s+number|ifsc|date\s+of\s+birth)",
            r"selfie\s+verification",
            r"document\s+verification",
            r"complete\s+(?:your\s+)?profile\s+verification",
            r"bank\s+login\s+and\s+otp",
        ),
        categories=("Phishing", "Fake KYC/Bank Alert", "Impersonation Scam"),
        evidence="Requests private identity, bank, or document data that can be used for account takeover or fraud.",
    ),
    DetectionRule(
        code="fake_result_certificate_pressure",
        label="Fake result, marksheet, or certificate pressure",
        weight=24,
        patterns=(
            r"(?:result|marksheet|certificate).*(?:blocked|locked|hold|withheld|release|download)",
            r"(?:student|exam).*(?:otp|fee|payment|verify)",
            r"(?:cisce|icse|isc).*(?:otp|fee|payment|blocked|verify)",
            r"(?:download|release)\s+(?:marksheet|certificate).*otp",
        ),
        categories=("Phishing", "Impersonation Scam"),
        evidence="Uses exam result or certificate language with blocking, fee, OTP, or forced verification pressure.",
    ),
    DetectionRule(
        code="fake_government_notice",
        label="Fake government, subsidy, tax, or benefit notice",
        weight=26,
        patterns=(
            r"(?:government|govt|subsidy|benefit|pension|tax|challan).*(?:verify|login|otp|pay|blocked|stop)",
            r"(?:electricity|sim|ration|gas).*(?:kyc|verify|otp|blocked|suspended)",
            r"(?:aadhaar|digilocker|umang).*(?:otp|password|pay|urgent|blocked)",
        ),
        categories=("Phishing", "Impersonation Scam", "Fake KYC/Bank Alert"),
        evidence="Impersonates an official notice to pressure the user into login, payment, OTP, or private-data sharing.",
    ),
    DetectionRule(
        code="digital_arrest_link_pressure",
        label="Digital arrest link or settlement pressure",
        weight=30,
        patterns=(
            r"digital\s+arrest.*(?:link|verify|pay|settlement|case\s+file)",
            r"(?:cyber\s+cell|police).*(?:stay\s+on\s+call|secret|settlement|pay|verify)",
            r"(?:case\s+file|legal\s+notice).*(?:link|payment|otp|verify)",
        ),
        categories=("Fake Police/Legal Threat", "Phishing", "Impersonation Scam"),
        evidence="Uses a fake police/legal link, case file, secrecy, or settlement demand to intimidate the target.",
    ),
    DetectionRule(
        code="upi_refund_collect",
        label="UPI refund, collect request, or payment manipulation",
        weight=32,
        patterns=(
            r"\bupi\b",
            r"यूपीआई",
            r"యూపీఐ",
            r"ইউপিআই",
            r"upi\s*id",
            r"collect\s+request",
            r"approve\s+(?:the\s+)?request",
            r"payment\s+request",
            r"refund",
            r"रिफंड",
            r"రిఫండ్",
            r"রিফান্ড",
            r"cashback",
            r"receive\s+money.*pin",
            r"wrong\s+payment",
            r"reverse\s+(?:a\s+)?(?:payment|transaction)",
            r"payment\s+gateway",
        ),
        categories=("UPI Fraud", "QR Code Scam", "Fake Customer Care Scam"),
        evidence="Mentions UPI, refund, collect request, or transaction reversal steps that can move money out.",
    ),
    DetectionRule(
        code="qr_code_trap",
        label="QR code payment trap",
        weight=32,
        patterns=(
            r"scan\s+(?:the\s+)?qr",
            r"qr\s+code",
            r"क्यूआर",
            r"క్యూ\s*ఆర్",
            r"কিউআর",
            r"scan\s+and\s+(?:receive|collect|approve)",
            r"receive\s+(?:money|refund).*qr",
            r"qr\s+(?:refund|verification|payment)",
        ),
        categories=("QR Code Scam", "UPI Fraud"),
        evidence="Asks the user to scan or approve a QR flow, a common trick for unauthorized payment.",
    ),
    DetectionRule(
        code="fake_job_offer",
        label="Fake job or recruitment offer",
        weight=30,
        patterns=(
            r"\bjob\b",
            r"hiring",
            r"recruitment",
            r"interview\s+selected",
            r"joining\s+kit",
            r"joining\s+fee",
            r"hr\s+(?:team|department|manager)",
            r"offer\s+letter",
            r"registration\s+fee",
            r"security\s+deposit",
        ),
        categories=("Fake Job Scam",),
        evidence="Uses recruitment or joining language often paired with advance-fee job scams.",
    ),
    DetectionRule(
        code="work_from_home_task",
        label="Work-from-home task income lure",
        weight=30,
        patterns=(
            r"work\s+from\s+home",
            r"part[-\s]?time",
            r"daily\s+income",
            r"earn\s+(?:rs\.?|inr)",
            r"typing\s+job",
            r"rating\s+job",
            r"like\s+(?:videos|posts)",
            r"telegram\s+task",
            r"prepaid\s+task",
            r"salary\s+release",
        ),
        categories=("Work From Home Scam", "Fake Job Scam", "Investment Scam"),
        evidence="Promises easy remote income, ratings, likes, or prepaid tasks often used in task scams.",
    ),
    DetectionRule(
        code="fake_loan_approval",
        label="Fake loan approval or processing-fee request",
        weight=30,
        patterns=(
            r"loan\s+approved",
            r"लोन",
            r"లోన్",
            r"ঋণ",
            r"instant\s+loan",
            r"pre[-\s]?approved",
            r"zero\s+cibil",
            r"low\s+interest",
            r"disbursal",
            r"loan\s+limit",
            r"no\s+documents",
            r"processing\s+(?:fee|charge)",
            r"insurance\s+charge",
        ),
        categories=("Fake Loan Scam",),
        evidence="Mentions easy loan approval, CIBIL bypass, disbursal, or advance charges used in loan scams.",
    ),
    DetectionRule(
        code="lottery_prize_reward",
        label="Unexpected prize, lottery, reward, or gift claim",
        weight=30,
        patterns=(
            r"won\b",
            r"winner",
            r"lottery",
            r"लॉटरी",
            r"లాటరీ",
            r"লটারি",
            r"lucky\s+draw",
            r"prize",
            r"इनाम",
            r"బహుమతి",
            r"পুরস্কার",
            r"reward",
            r"gift\s+card",
            r"claim\s+now",
            r"congratulations",
            r"processing\s+(?:fee|charge)",
        ),
        categories=("Lottery/Prize Scam",),
        evidence="Promises unexpected winnings, gifts, or rewards to lure payment or data sharing.",
    ),
    DetectionRule(
        code="investment_returns",
        label="Guaranteed investment or trading profit claim",
        weight=32,
        patterns=(
            r"investment",
            r"double\s+(?:your\s+)?money",
            r"guaranteed\s+(?:return|profit)",
            r"daily\s+profit",
            r"crypto",
            r"forex",
            r"trading\s+plan",
            r"stock\s+tip",
            r"profit\s+scheme",
            r"risk[-\s]?free\s+return",
        ),
        categories=("Investment Scam",),
        evidence="Uses guaranteed-profit, trading, crypto, or double-money claims associated with investment fraud.",
    ),
    DetectionRule(
        code="courier_parcel_script",
        label="Courier, customs, or parcel pressure script",
        weight=30,
        patterns=(
            r"parcel",
            r"courier",
            r"customs",
            r"delivery\s+hold",
            r"address\s+verification",
            r"illegal\s+(?:items|goods)",
            r"restricted\s+(?:items|goods)",
            r"package\s+seized",
            r"imported\s+gift",
        ),
        categories=("Courier/Parcel Scam", "Impersonation Scam", "Fake Police/Legal Threat"),
        evidence="Matches parcel, courier, or customs scripts used for payment pressure and impersonation.",
    ),
    DetectionRule(
        code="fake_customer_care",
        label="Fake customer care or remote support",
        weight=32,
        patterns=(
            r"customer\s+care",
            r"helpline",
            r"support\s+(?:agent|executive|desk|team)",
            r"refund\s+team",
            r"download\s+(?:app|support\s+app|remote)",
            r"screen\s+share",
            r"remote\s+access",
            r"anydesk",
            r"quick\s+support",
        ),
        categories=("Fake Customer Care Scam", "UPI Fraud", "Phishing"),
        evidence="Uses support or refund language that may lead to remote access, credential theft, or UPI fraud.",
    ),
    DetectionRule(
        code="fake_police_legal_threat",
        label="Fake police, legal, FIR, or arrest threat",
        weight=28,
        patterns=(
            r"\bpolice\b",
            r"पुलिस",
            r"పోలీస్",
            r"পুলিশ",
            r"cyber\s+cell",
            r"\bfir\b",
            r"arrest\s+warrant",
            r"गिरफ्तार",
            r"అరెస్ట్",
            r"গ্রেফতার",
            r"legal\s+notice",
            r"court\s+case",
            r"money\s+laundering",
            r"digital\s+arrest",
            r"case\s+file",
            r"settlement\s+amount",
        ),
        categories=("Fake Police/Legal Threat", "Impersonation Scam"),
        evidence="Threatens police, FIR, court, arrest, or settlement action to force quick compliance.",
    ),
    DetectionRule(
        code="impersonation_claim",
        label="Bank, government, company, or family impersonation",
        weight=28,
        patterns=tuple(re.escape(word) for word in INSTITUTION_WORDS)
        + (
            r"i\s+am\s+(?:your\s+)?(?:son|daughter|brother|sister|boss|manager|teacher|officer)",
            r"speaking\s+from\s+(?:bank|government|police|company|support)",
            r"official\s+(?:department|notice|account|verification)",
            r"family\s+emergency",
            r"new\s+number",
            r"changed\s+my\s+phone",
        ),
        categories=("Impersonation Scam", "Fake Customer Care Scam", "Fake KYC/Bank Alert"),
        evidence="Claims authority or a trusted relationship such as bank, government, company, police, or family.",
    ),
    DetectionRule(
        code="urgent_fear_language",
        label="Urgency, fear, or deadline pressure",
        weight=18,
        patterns=(
            r"\burgent\b",
            r"\bimmediate(?:ly)?\b",
            r"within\s+\d+\s*(?:hours?|hrs?|days?|minutes?|mins?)",
            r"last\s+chance",
            r"expires?\s+(?:today|soon|in)",
            r"today\s+only",
            r"avoid\s+(?:block|arrest|penalty|fine)",
            r"final\s+warning",
            r"do\s+not\s+delay",
        ),
        categories=("Phishing", "Fake KYC/Bank Alert", "Fake Police/Legal Threat", "Unknown Suspicious"),
        evidence="Uses pressure, fear, or deadlines to reduce careful verification.",
    ),
    DetectionRule(
        code="upfront_fee",
        label="Upfront fee, deposit, or transfer request",
        weight=22,
        patterns=(
            r"\bpay\b",
            r"भुगतान",
            r"చెల్లించ",
            r"చెల్లింపు",
            r"পেমেন্ট",
            r"টাকা",
            r"transfer",
            r"deposit",
            r"advance\s+(?:fee|payment)",
            r"processing\s+(?:fee|charge)",
            r"registration\s+fee",
            r"verification\s+charge",
            r"security\s+deposit",
            r"settlement\s+amount",
            r"wallet\s+top[-\s]?up",
            r"rs\.?\s*\d+",
            r"inr\s*\d+",
        ),
        categories=(
            "UPI Fraud",
            "Fake Job Scam",
            "Work From Home Scam",
            "Fake Loan Scam",
            "Lottery/Prize Scam",
            "Investment Scam",
            "Impersonation Scam",
        ),
        evidence="Requests a payment, fee, deposit, transfer, or money-linked action before verification.",
    ),
    DetectionRule(
        code="secrecy_demand",
        label="Secrecy or isolation demand",
        weight=16,
        patterns=(
            r"do\s+not\s+(?:tell|inform|share)",
            r"keep\s+(?:this\s+)?secret",
            r"confidential",
            r"no\s+need\s+to\s+tell",
            r"without\s+informing",
            r"stay\s+on\s+(?:call|line)",
        ),
        categories=("Impersonation Scam", "Fake Police/Legal Threat", "Investment Scam", "Unknown Suspicious"),
        evidence="Asks the target to keep the conversation secret or stay isolated from trusted people.",
    ),
    DetectionRule(
        code="emotional_manipulation",
        label="Emotional manipulation or emergency pressure",
        weight=15,
        patterns=(
            r"medical\s+emergency",
            r"hospital",
            r"accident",
            r"stuck\s+(?:at|in)",
            r"please\s+help\s+fast",
            r"crying",
            r"need\s+money\s+now",
            r"family\s+problem",
            r"student\s+fees\s+urgent",
        ),
        categories=("Impersonation Scam", "Unknown Suspicious"),
        evidence="Uses emergency or emotional pressure to push quick payment or secrecy.",
    ),
    DetectionRule(
        code="unusual_payment_instruction",
        label="Unusual payment instruction",
        weight=18,
        patterns=(
            r"gift\s+card",
            r"voucher",
            r"crypto\s+wallet",
            r"wallet\s+top[-\s]?up",
            r"split\s+payment",
            r"pay\s+to\s+(?:this|new)\s+account",
            r"temporary\s+account",
            r"merchant\s+qr",
            r"agent\s+wallet",
        ),
        categories=("UPI Fraud", "Investment Scam", "Impersonation Scam", "QR Code Scam"),
        evidence="Requests an unusual payment route instead of a normal verified channel.",
    ),
    DetectionRule(
        code="suspicious_grammar_formatting",
        label="Suspicious grammar, typo pattern, or formatting",
        weight=10,
        patterns=(
            r"!!!",
            r"@@@",
            r"\$\$\$",
            r"verfy",
            r"immediatly",
            r"recieve",
            r"acccount",
            r"lotery",
            r"passwrod",
            r"kindly\s+do\s+needful\s+urgent",
            r"dear\s+user\s+your",
            r"\bplz\b",
        ),
        categories=("Unknown Suspicious", "Phishing"),
        evidence="Contains typo patterns, generic wording, or unusual emphasis often seen in scam templates.",
    ),
)

URL_RISK_CATEGORIES = ("Phishing", "Fake KYC/Bank Alert", "Fake Customer Care Scam")


def _normalize(text: str | None) -> str:
    return (text or "").strip()


def _combined(text: str | None, url: str | None) -> str:
    return f"{_normalize(text)} {_normalize(url)}".strip().lower()


def _normalize_category(category: str | None) -> str:
    value = CATEGORY_ALIASES.get(category or "", category or "Unknown Suspicious")
    return value if value in SCAM_CATEGORIES else "Unknown Suspicious"


def _domain_from_url(url: str | None) -> str:
    value = _normalize(url)
    if not value:
        return ""
    if "://" not in value:
        value = f"https://{value}"
    parsed = urlparse(value)
    domain = (parsed.netloc or parsed.path).split("/")[0].lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def _url_text(url: str | None) -> str:
    value = _normalize(url)
    if not value:
        return ""
    if "://" not in value:
        value = f"https://{value}"
    parsed = urlparse(value)
    return f"{parsed.netloc} {parsed.path} {parsed.query}".lower()


def _is_trusted_domain(domain: str) -> bool:
    return any(domain == trusted or domain.endswith(f".{trusted}") for trusted in TRUSTED_DOMAINS)


def _has_suspicious_tld(domain: str) -> bool:
    return any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS)


def _has_ip_domain(domain: str) -> bool:
    return bool(re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", domain))


def _domain_uses_risky_words(domain: str) -> bool:
    risky_words = [
        "bank",
        "secure",
        "verify",
        "kyc",
        "aadhaar",
        "upi",
        "reward",
        "loan",
        "support",
        "refund",
        "police",
        "customs",
        "courier",
        "login",
        "update",
        "pay",
        "prize",
        "job",
        "investment",
        "result",
        "results",
        "certificate",
        "cisce",
        "icse",
        "digilocker",
        "umang",
        "sbi",
        "hdfc",
        "icici",
        "axis",
        "phonepe",
        "paytm",
        "gpay",
        "googlepay",
        "whatsapp",
        "telegram",
        "amazon",
        "flipkart",
        "irctc",
        "income",
        "tax",
    ]
    return any(word in domain for word in risky_words)


def _domain_has_unusual_unknown_pattern(domain: str) -> bool:
    base = domain.split(".")[0]
    if not base:
        return False
    has_letters = bool(re.search(r"[a-z]", base))
    has_digits = bool(re.search(r"\d", base))
    if has_letters and has_digits and len(base) <= 18:
        return True
    if re.search(r"\d{2,}", base) and len(base) <= 24:
        return True
    if len(re.findall(r"[bcdfghjklmnpqrstvwxyz]{5,}", base)) >= 1:
        return True
    return False


def _matching_patterns(value: str, patterns: tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    seen: set[str] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, value, flags=re.IGNORECASE):
            snippet = " ".join(match.group(0).strip().split())
            if snippet and snippet not in seen:
                matches.append(snippet)
                seen.add(snippet)
            break
    return matches


def _is_prevention_or_normal_context(value: str) -> bool:
    safe_patterns = (
        r"\bnever\s+share\b",
        r"\bdo\s+not\s+share\b",
        r"\bdon't\s+share\b",
        r"\bno\s+(?:payment|otp|pin|password|fee)\s+(?:is\s+)?(?:needed|required|requested)\b",
        r"\bno\s+payment\s+or\s+otp\s+is\s+needed\b",
        r"\bno\s+documents\s+are\s+required\b",
        r"\bno\s+urgent\s+action\b",
        r"\bpay\s+at\s+counter\s+only\b",
        r"\bofficial\s+(?:branch|channels?|classroom|portal|display)\b",
        r"\bofficial\s+(?:website|app|portal)\b",
        r"\bawareness\s+(?:note|message|reminder)\b",
        r"\bresults?\s+(?:are|is|now)?\s*(?:available|declared|published)\b",
        r"\bexam\s+results?\b",
        r"\bcertificate\s+(?:is|will\s+be|has\s+been)?\s*(?:available|issued|published)\b",
        r"\bschool\s+meeting\s+(?:notice|reminder)\b",
        r"\bmeeting\s+(?:notice|reminder)\b",
        r"\belectricity\s+bill\s+(?:has\s+been|is)?\s*(?:generated|available)\b",
        r"\bbank\s+statement\s+(?:has\s+been|is|now)?\s*(?:available|generated)\b",
        r"\border\s+is\s+ready\b",
        r"\bpackage\s+will\s+arrive\b",
        r"\bcourier\s+was\s+left\b",
        r"\bmeeting\s+invite\b",
        r"\bassignment\s+feedback\b",
    )
    return any(re.search(pattern, value, flags=re.IGNORECASE) for pattern in safe_patterns)


def _add_factor(
    factors: list[dict[str, Any]],
    code: str,
    label: str,
    weight: int,
    evidence: str,
    categories: tuple[str, ...],
    matched_patterns: list[str] | None = None,
    source: str = "text",
) -> None:
    if any(factor["code"] == code and factor.get("source") == source for factor in factors):
        return
    factors.append(
        {
            "code": code,
            "label": label,
            "weight": weight,
            "evidence": evidence,
            "categories": [_normalize_category(category) for category in categories],
            "matched_patterns": matched_patterns or [],
            "source": source,
        }
    )


def _has_meaningful_metadata(metadata: dict[str, Any] | None) -> bool:
    metadata = metadata or {}
    return any(
        metadata.get(key) not in (None, "", 0, "0")
        for key in ("platform", "victim_age_group", "age_group", "target_group", "amount_involved", "amount")
    )


def signal_sources(text: str | None, url: str | None, metadata: dict[str, Any] | None = None) -> dict[str, bool]:
    return {
        "text": bool(_normalize(text)),
        "url": bool(_normalize(url)),
        "metadata": _has_meaningful_metadata(metadata),
    }


def detection_mode(text: str | None, url: str | None, metadata: dict[str, Any] | None = None) -> str:
    sources = signal_sources(text, url, metadata)
    active = [name for name, used in sources.items() if used]
    if not active:
        return "empty_or_weak_input"
    if active == ["text"]:
        return "text_only"
    if active == ["url"]:
        return "url_only"
    if active == ["metadata"]:
        return "metadata_only"
    return "hybrid_" + "_".join(active)


def extract_text_risk_factors(text: str | None) -> list[dict[str, Any]]:
    value = _normalize(text).lower()
    factors: list[dict[str, Any]] = []
    if not value:
        return factors
    prevention_context = _is_prevention_or_normal_context(value)

    for rule in TEXT_RULES:
        hits = _matching_patterns(value, rule.patterns)
        if hits and prevention_context and rule.code in {
            "otp_code_request",
            "pin_cvv_password_request",
            "urgent_fear_language",
            "upfront_fee",
            "fake_customer_care",
            "courier_parcel_script",
            "phishing_login_verification",
            "credential_harvesting_private_data",
            "fake_result_certificate_pressure",
            "fake_government_notice",
            "digital_arrest_link_pressure",
            "impersonation_claim",
            "fake_loan_approval",
            "fake_police_legal_threat",
        }:
            hits = []
        if hits:
            _add_factor(factors, rule.code, rule.label, rule.weight, rule.evidence, rule.categories, hits[:6], "text")

    uppercase_count = len(re.findall(r"[A-Z]", _normalize(text)))
    original = _normalize(text)
    if len(original) >= 50 and uppercase_count > 22 and uppercase_count > len(original) * 0.32:
        _add_factor(
            factors,
            "excessive_caps",
            "Excessive capital letters",
            8,
            "Uses unusually high capitalization, often combined with urgency or intimidation.",
            ("Unknown Suspicious", "Phishing"),
            source="text",
        )

    return factors


def extract_url_risk_factors(url: str | None) -> list[dict[str, Any]]:
    factors: list[dict[str, Any]] = []
    domain = _domain_from_url(url)
    if not domain:
        return factors

    url_value = _url_text(url)
    trusted_domain = _is_trusted_domain(domain)
    action_patterns = (
        r"login",
        r"verify",
        r"secure",
        r"kyc",
        r"password",
        r"upi",
        r"refund",
        r"claim",
        r"pay",
        r"prize",
        r"loan",
    )
    if trusted_domain:
        action_patterns = (
            r"password",
            r"kyc",
            r"upi",
            r"refund",
            r"pay",
            r"prize",
            r"loan",
        )
    path_hits = _matching_patterns(
        url_value,
        action_patterns,
    )
    if path_hits:
        _add_factor(
            factors,
            "url_action_words",
            "URL contains login, verification, payment, or claim words",
            17,
            "The submitted URL contains terms commonly used in phishing, KYC, payment, refund, or prize pages.",
            URL_RISK_CATEGORIES,
            path_hits[:6],
            "url",
        )

    if domain in SHORTENER_DOMAINS:
        _add_factor(
            factors,
            "shortened_url",
            "Shortened URL",
            22,
            f"Uses URL shortener domain: {domain}. Short links hide the final destination.",
            ("Phishing",),
            source="url",
        )
    elif not trusted_domain:
        reasons = [f"Submitted domain: {domain}."]
        weight = 8
        suspicious_domain = False
        if _has_suspicious_tld(domain):
            reasons.append("The top-level domain is often seen in disposable or suspicious links.")
            suspicious_domain = True
            weight += 8
        if _has_ip_domain(domain):
            reasons.append("The link uses a raw IP address instead of a recognizable domain.")
            suspicious_domain = True
            weight += 8
        if _domain_uses_risky_words(domain):
            reasons.append("The domain uses trust-seeking words such as secure, verify, bank, support, reward, job, or loan.")
            suspicious_domain = True
            weight += 8
        if _domain_has_unusual_unknown_pattern(domain):
            reasons.append("The domain mixes numbers and letters or has an unusual machine-generated pattern.")
            suspicious_domain = True
            weight += 16
        if not suspicious_domain:
            _add_factor(
                factors,
                "untrusted_domain_context",
                "Untrusted domain context",
                6,
                f"Submitted domain {domain} is not in the trusted-domain list. Verify before using it.",
                ("Unknown Suspicious",),
                source="url",
            )
            return factors
        _add_factor(
            factors,
            "unusual_unknown_domain" if _domain_has_unusual_unknown_pattern(domain) and not _domain_uses_risky_words(domain) else "unknown_or_lookalike_domain",
            "Unusual unknown domain" if _domain_has_unusual_unknown_pattern(domain) and not _domain_uses_risky_words(domain) else "Unknown, lookalike, or suspicious domain",
            min(weight, 28),
            " ".join(reasons),
            ("Unknown Suspicious", "Phishing") if _domain_has_unusual_unknown_pattern(domain) and not _domain_uses_risky_words(domain) else URL_RISK_CATEGORIES,
            source="url",
        )

    return factors


def extract_hybrid_risk_factors(text: str | None, url: str | None) -> list[dict[str, Any]]:
    factors: list[dict[str, Any]] = []
    value = _normalize(text).lower()
    domain = _domain_from_url(url)
    if not value or not domain:
        return factors
    trusted_domain = _is_trusted_domain(domain)

    if not trusted_domain and re.search(r"\b(?:check|click|open|visit|use|tap|verify|login|claim)\b.{0,25}\b(?:link|url|website|site|portal|page)\b", value):
        _add_factor(
            factors,
            "unknown_domain_click_prompt",
            "Unknown-domain click prompt",
            14,
            f"The message asks the user to open or check a link, but the submitted domain {domain} is not trusted.",
            ("Unknown Suspicious", "Phishing"),
            matched_patterns=[domain],
            source="hybrid",
        )

    if not trusted_domain and re.search(r"\b(?:official|bank|government|govt|support|customer care|police|board|result|certificate|refund|kyc|upi)\b", value):
        _add_factor(
            factors,
            "untrusted_domain_with_authority_context",
            "Untrusted domain used with authority or service context",
            16,
            f"The text suggests an official/service context, but the submitted domain {domain} is not on the trusted list.",
            ("Phishing", "Impersonation Scam", "Unknown Suspicious"),
            matched_patterns=[domain],
            source="hybrid",
        )

    org_rules = (
        (
            "cisce_domain_mismatch",
            ("cisce", "icse", "isc result", "isc exam"),
            ("cisce.org", "results.cisce.org"),
            "CISCE/ICSE/ISC",
        ),
        (
            "digilocker_domain_mismatch",
            ("digilocker",),
            ("digilocker.gov.in",),
            "DigiLocker",
        ),
        (
            "umang_domain_mismatch",
            ("umang",),
            ("umang.gov.in",),
            "UMANG",
        ),
    )
    for code, tokens, allowed_domains, org_name in org_rules:
        if any(token in value for token in tokens) and not any(
            domain == allowed or domain.endswith(f".{allowed}") for allowed in allowed_domains
        ):
            _add_factor(
                factors,
                code,
                "Claimed organization does not match submitted domain",
                28,
                f"The message claims {org_name}, but the submitted domain is {domain}, not an official expected domain.",
                ("Phishing", "Impersonation Scam"),
                matched_patterns=[domain, org_name],
                source="hybrid",
            )

    return factors


def extract_risk_factors(text: str | None, url: str | None) -> list[dict[str, Any]]:
    """Return explainable weighted rules found in the submitted text or URL."""
    factors = extract_text_risk_factors(text) + extract_url_risk_factors(url) + extract_hybrid_risk_factors(text, url)
    return sorted(factors, key=lambda item: item["weight"], reverse=True)


def _metadata_risk_factors(metadata: dict[str, Any] | None) -> list[dict[str, Any]]:
    metadata = metadata or {}
    factors: list[dict[str, Any]] = []

    amount = metadata.get("amount_involved") or metadata.get("amount")
    try:
        amount_value = float(amount) if amount not in (None, "") else 0.0
    except (TypeError, ValueError):
        amount_value = 0.0

    if amount_value >= 100000:
        _add_factor(
            factors,
            "high_amount_exposure",
            "High reported financial exposure",
            15,
            "The reported amount is Rs. 100,000 or higher, so financial containment may be time-sensitive.",
            ("UPI Fraud", "Fake Loan Scam", "Investment Scam", "Impersonation Scam"),
            source="metadata",
        )
    elif amount_value >= 10000:
        _add_factor(
            factors,
            "medium_amount_exposure",
            "Moderate reported financial exposure",
            9,
            "The reported amount is Rs. 10,000 or higher.",
            ("UPI Fraud", "Fake Loan Scam", "Investment Scam", "Unknown Suspicious"),
            source="metadata",
        )
    elif amount_value > 0:
        _add_factor(
            factors,
            "amount_involved",
            "Money amount reported",
            5,
            "A monetary amount was reported, increasing the need for caution and evidence preservation.",
            ("UPI Fraud", "Fake Job Scam", "Fake Loan Scam", "Unknown Suspicious"),
            source="metadata",
        )

    age_group = str(
        metadata.get("victim_age_group") or metadata.get("age_group") or metadata.get("target_group") or ""
    ).lower()
    if any(term in age_group for term in ["senior", "elder", "60"]):
        _add_factor(
            factors,
            "vulnerable_age_senior",
            "Senior citizen risk context",
            6,
            "The target group is marked as senior citizen, so prevention and follow-up should be prioritized.",
            ("Unknown Suspicious",),
            source="metadata",
        )
    elif any(term in age_group for term in ["teen", "minor", "student", "job seeker"]):
        _add_factor(
            factors,
            "vulnerable_age_student",
            "Student, minor, or job-seeker risk context",
            5,
            "The target group suggests student, minor, or job-seeker vulnerability.",
            ("Unknown Suspicious", "Fake Job Scam", "Work From Home Scam"),
            source="metadata",
        )
    elif "business" in age_group:
        _add_factor(
            factors,
            "business_target_context",
            "Business owner target context",
            4,
            "Business owners can be targeted with payment, parcel, vendor, or impersonation scams.",
            ("Unknown Suspicious", "Impersonation Scam", "Courier/Parcel Scam"),
            source="metadata",
        )

    platform = str(metadata.get("platform") or "").lower()
    if platform in {"whatsapp", "telegram", "sms"}:
        _add_factor(
            factors,
            "high_velocity_platform",
            "High-forwarding-risk platform",
            4,
            "The report came through SMS, WhatsApp, or Telegram, where scam templates can spread quickly.",
            ("Unknown Suspicious",),
            source="metadata",
        )

    return factors


def _category_scores(factors: list[dict[str, Any]]) -> dict[str, int]:
    scores: dict[str, int] = {}
    for factor in factors:
        for category in factor.get("categories") or ["Unknown Suspicious"]:
            normalized = _normalize_category(category)
            scores[normalized] = scores.get(normalized, 0) + int(factor.get("weight", 0))

    codes = {factor.get("code") for factor in factors}
    priority_boosts = {
        "otp_code_request": ("OTP Fraud", 90),
        "pin_cvv_password_request": ("OTP Fraud", 16),
        "kyc_account_threat": ("Fake KYC/Bank Alert", 60),
        "upi_refund_collect": ("UPI Fraud", 62),
        "qr_code_trap": ("QR Code Scam", 92),
        "fake_job_offer": ("Fake Job Scam", 64),
        "work_from_home_task": ("Work From Home Scam", 86),
        "fake_loan_approval": ("Fake Loan Scam", 70),
        "lottery_prize_reward": ("Lottery/Prize Scam", 86),
        "investment_returns": ("Investment Scam", 74),
        "courier_parcel_script": ("Courier/Parcel Scam", 92),
        "fake_customer_care": ("Fake Customer Care Scam", 92),
        "fake_police_legal_threat": ("Fake Police/Legal Threat", 92),
        "impersonation_claim": ("Impersonation Scam", 22),
        "phishing_login_verification": ("Phishing", 26),
        "credential_harvesting_private_data": ("Phishing", 36),
        "fake_result_certificate_pressure": ("Phishing", 34),
        "fake_government_notice": ("Phishing", 34),
        "digital_arrest_link_pressure": ("Fake Police/Legal Threat", 42),
        "url_action_words": ("Phishing", 18),
        "shortened_url": ("Phishing", 22),
        "unknown_or_lookalike_domain": ("Phishing", 18),
        "cisce_domain_mismatch": ("Phishing", 34),
        "digilocker_domain_mismatch": ("Phishing", 34),
        "umang_domain_mismatch": ("Phishing", 34),
    }
    for code, (category, boost) in priority_boosts.items():
        if code in codes:
            scores[category] = scores.get(category, 0) + boost
    if "otp_code_request" in codes and "upi_refund_collect" not in codes and "qr_code_trap" not in codes:
        scores["OTP Fraud"] = max(scores.get("OTP Fraud", 0), max(scores.values() or [0]) + 8)
    if "fake_police_legal_threat" in codes and "courier_parcel_script" not in codes:
        scores["Fake Police/Legal Threat"] = max(
            scores.get("Fake Police/Legal Threat", 0),
            max(scores.values() or [0]) + 8,
        )

    return scores


CRITICAL_SCAM_CODES = {
    "otp_code_request",
    "pin_cvv_password_request",
    "kyc_account_threat",
    "upi_refund_collect",
    "qr_code_trap",
    "upfront_fee",
    "fake_customer_care",
    "fake_police_legal_threat",
    "impersonation_claim",
    "shortened_url",
    "unknown_or_lookalike_domain",
    "credential_harvesting_private_data",
    "fake_result_certificate_pressure",
    "fake_government_notice",
    "digital_arrest_link_pressure",
    "cisce_domain_mismatch",
    "digilocker_domain_mismatch",
    "umang_domain_mismatch",
}

MEANINGFUL_PHISHING_CODES = {
    "otp_code_request",
    "pin_cvv_password_request",
    "kyc_account_threat",
    "phishing_login_verification",
    "upfront_fee",
    "shortened_url",
    "unknown_or_lookalike_domain",
    "credential_harvesting_private_data",
    "fake_result_certificate_pressure",
    "fake_government_notice",
    "digital_arrest_link_pressure",
    "cisce_domain_mismatch",
    "digilocker_domain_mismatch",
    "umang_domain_mismatch",
}


def _has_critical_scam_factor(factors: list[dict[str, Any]]) -> bool:
    return any(factor.get("code") in CRITICAL_SCAM_CODES for factor in factors)


def _has_meaningful_phishing_evidence(factors: list[dict[str, Any]]) -> bool:
    return any(factor.get("code") in MEANINGFUL_PHISHING_CODES for factor in factors)


def risk_band(score: int) -> str:
    if score <= 25:
        return "Likely Safe"
    if score <= 50:
        return "Low/Moderate Suspicious"
    if score <= 75:
        return "High Risk"
    return "Critical Risk"


def _correct_categories_for_score(
    score: int,
    factors: list[dict[str, Any]],
    categories: list[dict[str, Any]],
    sources: dict[str, bool],
) -> list[dict[str, Any]]:
    has_text_or_url = sources.get("text") or sources.get("url")
    has_critical = _has_critical_scam_factor(factors)
    primary = categories[0]["name"] if categories else "Unknown Suspicious"

    if has_text_or_url and score <= 25 and not has_critical:
        return [{"name": "Likely Safe", "score": score, "confidence": 90}]

    if primary == "Phishing" and score <= 50 and not _has_meaningful_phishing_evidence(factors):
        non_phishing = [category for category in categories if category["name"] != "Phishing"]
        if non_phishing:
            return non_phishing
        return [{"name": "Unknown Suspicious", "score": score, "confidence": 55}]

    return categories


def _all_factors(text: str | None, url: str | None, metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return sorted(
        extract_risk_factors(text, url) + _metadata_risk_factors(metadata),
        key=lambda item: item["weight"],
        reverse=True,
    )


def detect_categories(text: str | None, url: str | None, metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    factors = _all_factors(text, url, metadata)
    sources = signal_sources(text, url, metadata)
    if not any(sources.values()):
        return [{"name": "Likely Safe", "score": 0, "confidence": 0}]

    content_factors = [factor for factor in factors if factor.get("source") in {"text", "url", "hybrid"}]
    metadata_score = sum(factor["weight"] for factor in factors if factor.get("source") == "metadata")
    if (sources["text"] or sources["url"]) and not content_factors and metadata_score < 15:
        return [{"name": "Likely Safe", "score": metadata_score, "confidence": 78}]

    scores = _category_scores(factors)
    if not scores:
        return [{"name": "Likely Safe", "score": 0, "confidence": 82}]

    if not sources["text"] and not sources["url"] and sources["metadata"]:
        return [{"name": "Unknown Suspicious", "score": sum(f["weight"] for f in factors), "confidence": 42}]

    max_score = max(scores.values()) or 1
    categories = [
        {
            "name": name,
            "score": score,
            "confidence": max(1, min(99, round((score / max_score) * 100))),
        }
        for name, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)
        if score >= max(10, max_score * 0.25)
    ]
    categories = categories[:5] or [{"name": "Unknown Suspicious", "score": 0, "confidence": 20}]
    score_estimate = min(100, sum(int(factor.get("weight", 0)) for factor in factors))
    if sources["text"] and sources["url"]:
        score_estimate = min(100, score_estimate + 5)
    return _correct_categories_for_score(score_estimate, factors, categories, sources)


def detect_category(text: str | None, url: str | None, metadata: dict[str, Any] | None = None) -> str:
    return detect_categories(text, url, metadata)[0]["name"]


def calculate_risk_score(text: str | None, url: str | None, metadata: dict[str, Any] | None = None) -> int:
    factors = _all_factors(text, url, metadata)
    sources = signal_sources(text, url, metadata)
    if not any(sources.values()):
        return 0
    if not factors:
        return 0
    content_factors = [factor for factor in factors if factor.get("source") in {"text", "url", "hybrid"}]
    metadata_score = sum(factor["weight"] for factor in factors if factor.get("source") == "metadata")
    if (sources["text"] or sources["url"]) and not content_factors and metadata_score < 15:
        return 0

    score = sum(int(factor["weight"]) for factor in factors)
    codes = {factor.get("code") for factor in factors}
    categories = [category["name"] for category in detect_categories(text, url, metadata)]

    if len(factors) >= 4:
        score += 9
    if {"urgent_fear_language", "impersonation_claim"} <= codes:
        score += 7
    if {"upfront_fee", "secrecy_demand"} <= codes:
        score += 7
    if {"otp_code_request", "pin_cvv_password_request"} & codes and (
        {"upi_refund_collect", "kyc_account_threat", "impersonation_claim"} & codes
    ):
        score += 12
    if sources["text"] and sources["url"]:
        score += 5
    if "Likely Safe" in categories:
        score = min(score, 10)
    if not sources["text"] and not sources["url"] and sources["metadata"]:
        score = min(score, 38)

    return max(0, min(100, int(score)))


def risk_level(score: int) -> str:
    if score >= 76:
        return "Critical"
    if score >= 51:
        return "High"
    if score >= 26:
        return "Medium"
    return "Low"


def classify_police_triage_priority(score: int, category: str) -> dict[str, str]:
    category = _normalize_category(category)
    immediate_categories = {
        "OTP Fraud",
        "UPI Fraud",
        "Fake KYC/Bank Alert",
        "Fake Customer Care Scam",
        "Fake Police/Legal Threat",
        "QR Code Scam",
        "Impersonation Scam",
    }
    high_attention_categories = immediate_categories | {
        "Phishing",
        "Fake Loan Scam",
        "Investment Scam",
        "Courier/Parcel Scam",
    }
    review_categories = high_attention_categories | {
        "Fake Job Scam",
        "Work From Home Scam",
        "Lottery/Prize Scam",
        "Unknown Suspicious",
    }

    if score >= 85 or (score >= 75 and category in immediate_categories):
        return {
            "priority": "Critical Immediate Triage",
            "explanation": (
                f"Risk score {score}/100 with {category} indicators suggests urgent potential harm, "
                "so police should preserve evidence and review containment steps immediately."
            ),
        }
    if score >= 60 or (score >= 50 and category in high_attention_categories):
        return {
            "priority": "High Priority",
            "explanation": (
                f"Risk score {score}/100 and {category} pattern indicate likely fraud activity, "
                "so the case should be reviewed quickly for financial or credential exposure."
            ),
        }
    if score >= 30 or category in review_categories:
        return {
            "priority": "Review Recommended",
            "explanation": (
                f"Risk score {score}/100 or the detected {category} pattern warrants human review, "
                "especially if money, OTP, PIN, passwords, QR approvals, or screenshots were shared."
            ),
        }
    return {
        "priority": "Low Priority",
        "explanation": (
            f"Risk score {score}/100 with {category} classification shows limited automated fraud indicators, "
            "so record it for awareness unless new evidence is added."
        ),
    }


def calculate_confidence_score(
    score: int,
    factors: list[dict[str, Any]],
    categories: list[dict[str, Any]],
    has_signal: bool,
) -> int:
    if not has_signal:
        return 0
    if not factors:
        return 82 if categories and categories[0]["name"] == "Likely Safe" else 20

    primary_category_confidence = categories[0]["confidence"] if categories else 20
    factor_strength = min(42, len(factors) * 6)
    score_strength = min(34, score * 0.34)
    source_bonus = min(12, len({factor.get("source") for factor in factors}) * 4)
    confidence = 12 + factor_strength + score_strength + primary_category_confidence * 0.12 + source_bonus
    if categories and categories[0]["name"] == "Unknown Suspicious":
        confidence -= 12
    return max(1, min(98, round(confidence)))


def flatten_matched_patterns(factors: list[dict[str, Any]]) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for factor in factors:
        for pattern in factor.get("matched_patterns") or []:
            matches.append(
                {
                    "rule": str(factor.get("label", "")),
                    "code": str(factor.get("code", "")),
                    "pattern": str(pattern),
                    "source": str(factor.get("source", "")),
                }
            )
    return matches


def analyze_url_trust(url: str | None, factors: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    domain = _domain_from_url(url)
    if not domain:
        return {
            "domain": "",
            "is_trusted_domain": False,
            "status": "No URL submitted",
            "reason": "The scanner used message text only because no URL was submitted.",
        }

    factors = factors or []
    codes = {factor.get("code") for factor in factors}
    trusted = _is_trusted_domain(domain)
    critical = bool(CRITICAL_SCAM_CODES & codes)
    suspicious_domain = (
        domain in SHORTENER_DOMAINS
        or _has_suspicious_tld(domain)
        or _has_ip_domain(domain)
        or _domain_uses_risky_words(domain)
        or any(code in codes for code in {"cisce_domain_mismatch", "digilocker_domain_mismatch", "umang_domain_mismatch"})
    )

    if trusted and critical:
        return {
            "domain": domain,
            "is_trusted_domain": True,
            "status": "Trusted domain with risky request",
            "reason": "The domain is trusted, but OTP, PIN, password, money, QR, urgency, or private-data indicators were still detected.",
        }
    if trusted:
        return {
            "domain": domain,
            "is_trusted_domain": True,
            "status": "Trusted domain, no critical request",
            "reason": "The domain is in the trusted list and no critical credential/payment indicator was detected.",
        }
    if suspicious_domain:
        return {
            "domain": domain,
            "is_trusted_domain": False,
            "status": "Suspicious or lookalike domain",
            "reason": "The domain is not trusted and contains shortener, lookalike, risky wording, IP, mismatch, or suspicious-TLD signals.",
        }
    return {
        "domain": domain,
        "is_trusted_domain": False,
        "status": "Untrusted domain, verify manually",
        "reason": "The domain is not on the trusted list. Verify through official channels before opening or entering details.",
    }


def _top_factor_labels(factors: list[dict[str, Any]]) -> str:
    return ", ".join(factor["label"].lower() for factor in factors[:4])


def generate_citizen_explanation(result: dict[str, Any]) -> str:
    if result.get("input_status") == "empty":
        return (
            "No message, URL, or useful context was provided. Paste the suspicious SMS, WhatsApp message, "
            "email text, call note, URL, or basic case context so CyberShield can check for fraud indicators."
        )

    factors = result.get("risk_factors") or []
    category = result.get("category", "Unknown Suspicious")
    level = result.get("risk_level", "Low")
    confidence = result.get("confidence_score", 0)
    mode = result.get("detection_mode", "unknown")

    if category == "Likely Safe" or not factors:
        return (
            f"This report is rated {level} with {confidence}% confidence using {mode.replace('_', ' ')} signals. "
            "No strong scam indicators were found, but unsolicited requests should still be verified through official channels."
        )

    return (
        f"This looks like a possible {category} case and is rated {level} with {confidence}% confidence. "
        f"The main warning signs are {_top_factor_labels(factors)}. Do not click unknown links, share OTP/PIN/password/CVV, "
        "scan QR codes, install remote-support apps, or pay fees based only on an unsolicited message or call."
    )


def generate_police_summary(result: dict[str, Any]) -> str:
    if result.get("input_status") == "empty":
        return (
            "No analyzable message, URL, or metadata was submitted. Ask the complainant for the original message, "
            "sender details, URL, screenshots, call notes, payment context, and transaction references."
        )

    factor_labels = [factor["label"] for factor in result.get("risk_factors", [])]
    categories = ", ".join(category["name"] for category in result.get("categories", [])[:4])
    evidence = "; ".join(factor_labels[:8]) if factor_labels else "No high-confidence automated indicators found"
    sources = ", ".join(result.get("signal_sources", [])) or "none"
    return (
        f"Automated triage classified this report as {result.get('category')} with risk score "
        f"{result.get('risk_score')}/100 ({result.get('risk_level')}) and confidence "
        f"{result.get('confidence_score')}%. Detection mode: {result.get('detection_mode')} using {sources} signals. "
        f"Related categories: {categories or 'None'}. Triggered indicators: {evidence}. Preserve original content and "
        "correlate sender, URL, UPI ID, QR flow, phone number, account, device/app context, and transaction references with similar reports."
    )


def recommend_police_action(score: int, category: str) -> str:
    category = _normalize_category(category)
    if score >= 80:
        base = "Critical priority: preserve evidence immediately, capture sender IDs, URLs, timestamps, transaction references, and screenshots."
    elif score >= 60:
        base = "High priority: preserve the report, verify payment or credential exposure, and correlate with recent similar complaints."
    elif score >= 26:
        base = "Medium priority: advise prevention steps, keep the report for pattern analysis, and escalate if money or credentials were shared."
    else:
        base = "Low priority: record as awareness or suspicious-contact input unless additional evidence is provided."

    category_steps = {
        "OTP Fraud": "Check whether OTP/PIN disclosure occurred and advise immediate bank/payment-app lock or dispute workflow.",
        "UPI Fraud": "Look for UPI IDs, collect requests, QR codes, phone numbers, and transaction IDs for rapid financial containment.",
        "Fake KYC/Bank Alert": "Validate the claimed institution and capture sender IDs, call notes, and any KYC collection flow.",
        "Phishing": "Review submitted domains, credential prompts, and hosting details where legally permitted.",
        "Fake Job Scam": "Check for recruitment fee demands, fake offer letters, mule-account requests, and job-seeker targeting.",
        "Work From Home Scam": "Check for prepaid task deposits, Telegram groups, wallet ledgers, and staged profit screenshots.",
        "Fake Loan Scam": "Check for advance fees, loan app names, account details, and harassment or data-theft risk.",
        "Lottery/Prize Scam": "Check for prize-fee payment requests, fake winner notices, and bank-detail collection.",
        "Investment Scam": "Check for guaranteed-return claims, payment wallets, group admins, and repeated campaign templates.",
        "Fake Customer Care Scam": "Check for fake helpline numbers, remote-access app prompts, refund scripts, and linked UPI handles.",
        "Courier/Parcel Scam": "Document parcel/customs claims, threat script, settlement demand, and impersonated agency.",
        "Impersonation Scam": "Document claimed identity, emotional pressure, new-number claims, and money destination.",
        "Fake Police/Legal Threat": "Preserve call/message evidence and verify claimed FIR, warrant, or digital-arrest script.",
        "QR Code Scam": "Capture QR screenshots, payment app flow, UPI ID, and transaction reference if scanned.",
    }
    return f"{base} {category_steps.get(category, 'Use the triggered rules to decide whether cyber cell escalation is needed.')}"


def recommend_citizen_action(score: int, category: str) -> str:
    category = _normalize_category(category)
    if score >= 80:
        return (
            "Do not respond. Do not click links, scan QR codes, share OTP/PIN/password/CVV/card details, install remote apps, "
            "or pay any fee. Preserve screenshots and contact the official bank/payment app or cybercrime channel if anything was shared."
        )
    if score >= 60:
        return (
            "Treat this as high risk. Stop the conversation, verify only through official apps/websites/known numbers, "
            "and report it if the sender asks for money, OTP, PIN, credentials, QR approval, secrecy, or remote access."
        )
    if score >= 26:
        return "Be cautious. Verify independently before acting, avoid sharing sensitive details, and keep screenshots if the sender continues."
    if category == "Likely Safe":
        return "No strong scam indicators were found. Still avoid sharing OTPs, PINs, passwords, CVV, or UPI PINs in unsolicited conversations."
    return "Low risk based on current content, but continue to verify requests through official channels."


def recommend_action(score: int, category: str) -> str:
    """Backward-compatible citizen action used by older UI fields."""
    return recommend_citizen_action(score, category)


def analyze_scam(text: str | None, url: str | None, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata = metadata or {}
    sources_dict = signal_sources(text, url, metadata)
    sources = [source for source, used in sources_dict.items() if used]
    mode = detection_mode(text, url, metadata)
    has_signal = bool(sources)
    factors = _all_factors(text, url, metadata)
    score = calculate_risk_score(text, url, metadata)
    categories = detect_categories(text, url, metadata)
    categories = _correct_categories_for_score(score, factors, categories, sources_dict)
    category = _normalize_category(categories[0]["name"])
    level = risk_level(score)
    confidence = calculate_confidence_score(score, factors, categories, has_signal)
    triage = classify_police_triage_priority(score, category)

    result = {
        "input_status": "ok" if has_signal else "empty",
        "risk_score": score,
        "risk_level": level,
        "risk_band": risk_band(score),
        "confidence_score": confidence,
        "category": category,
        "categories": categories,
        "police_triage_priority": triage["priority"],
        "police_triage_explanation": triage["explanation"],
        "risk_factors": factors,
        "triggered_rules": factors,
        "matched_patterns": flatten_matched_patterns(factors),
        "signal_sources": sources,
        "detection_mode": mode,
        "signal_summary": {
            "text": sources_dict["text"],
            "url": sources_dict["url"],
            "metadata": sources_dict["metadata"],
            "mode": mode,
        },
    }
    result["citizen_explanation"] = generate_citizen_explanation(result)
    result["police_summary"] = generate_police_summary(result)
    result["recommended_police_action"] = recommend_police_action(score, category)
    result["recommended_citizen_action"] = recommend_citizen_action(score, category)
    result["recommended_action"] = result["recommended_citizen_action"]
    return result
