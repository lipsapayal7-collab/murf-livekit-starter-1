'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { DashboardView } from '@/components/app/dashboard-view';
import { 
  Shield, 
  Landmark, 
  Wallet, 
  Headset, 
  Mic, 
  CheckCircle, 
  ShieldAlert,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  HelpCircle,
  Search,
  BookOpen,
  UserCheck,
  FileText,
  Building,
  ArrowLeft,
  Globe,
  Radio,
  ArrowRight,
  Check,
  Phone
} from 'lucide-react';


function HouseIcon({ active = false }: { active?: boolean }) {
  return (
    <svg
      width="23"
      height="23"
      viewBox="0 0 24 24"
      fill={active ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M3 10.5 12 3l9 7.5" />
      <path d="M5 9.5V21h14V9.5" />
      <path d="M9 21v-6h6v6" />
    </svg>
  );
}

function BarChartIcon({ active = false }: { active?: boolean }) {
  return (
    <svg
      width="23"
      height="23"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M4 20V10" />
      <path d="M10 20V4" />
      <path d="M16 20v-7" />
      <path d="M22 20V7" />
      {active && <path d="M2 21h20" />}
      {!active && <path d="M2 21h20" />}
    </svg>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
  isCallEnded?: boolean;
  onRestartCall?: () => void;
  micError?: boolean;
  onDismissMicError?: () => void;
  currentTab?: 'home' | 'schemes' | 'fraud' | 'complaint' | 'dashboard';
onTabChange?: (
  tab: 'home' | 'schemes' | 'fraud' | 'complaint' | 'dashboard'
) => void;
  callDuration?: number | null;
}

const TRANSLATIONS: Record<string, any> = {
  English: {
    platformTitle: "Jan Sahay (जन सहाय)",
    platformSubtitle: "Your Trusted Digital Saathi",
    navHome: "Home",
    navSchemes: "Schemes Search",
    navFraud: "Fraud Prevention",
    navComplaint: "Complaint Helpline",
    navDashboard: "Dashboard",
    heroTitle: "Discover Welfare Schemes & Prevent Digital Scams via Voice AI",
    heroDesc: "Start an encrypted voice call with our AI citizen advisor to ask queries in Hindi, English, and regional languages. Zero registration or login details required.",
    startCallLabel: "Click to start call",
    badgeSecure: "🛡️ 100% Secure",
    badgeVerified: "🏛️ Verified Scheme Data",
    badgeDirect: "📞 Direct Helpline Links",
    cardSchemesTitle: "Government Schemes",
    cardSchemesDesc: "Search criteria, documents, and application guides for welfare schemes.",
    cardFraudTitle: "Fraud Prevention",
    cardFraudDesc: "UPI collect scam warnings, OTP protection tips, and phishing safety.",
    cardFinancialTitle: "Financial Literacy",
    cardFinancialDesc: "Basic savings guides, direct benefit transfer (DBT) linking details.",
    cardComplaintTitle: "Complaint Helplines",
    cardComplaintDesc: "Step-by-step reporting to RBI Ombudsman or Cyber Crime Portal.",
    warningTitle: "🚨 Scam Warning Bulletin",
    warningFooter: "Defensive Action:",
    schemeSearchTitle: "🏛️ Scheme Search & Information",
    schemePlaceholder: "Search schemes by keywords...",
    eligibilityTitle: "Eligibility Requirements",
    documentsTitle: "Required Documents",
    applyTitle: "Application Process",
    backDashboard: "Back to Dashboard",
    noSchemes: "No schemes found",
    noSchemesDesc: "We couldn't find any government schemes matching the filter criteria.",
    fraudHubTitle: "🛡️ Fraud Prevention Hub",
    fraudBanner: "⚠️ Official Advisory: Keep your bank accounts secure. National authorities or bank officials will never contact you asking for your UPI PIN, banking passwords, or mobile OTP codes.",
    reportActiveBtn: "🚨 Report Active Fraud",
    defensiveStepTitle: "Defensive Step:",
    complaintHeader: "📞 Guided Complaint Assistance",
    complaintSub: "Select the category of complaint you wish to file below:",
    wizardTitle: "Grievance Helpline Wizard",
    stepText: "Step",
    complaintType1: "Cyber Crime or Phishing Link Fraud",
    complaintType1Sub: "Links claiming electricity bills, fake prize SMS, or OTP leaks.",
    complaintType2: "UPI transaction dispute or Banking Fraud",
    complaintType2Sub: "Unauthorized ATM withdrawals or money debited via UPI collect scam.",
    complaintType3: "Government Scheme Registration Issue",
    complaintType3Sub: "Installments not received on PM-Kisan or DBT link blockages.",
    btnBack: "Back to Selection",
    disclaimerText: "Disclaimer: Jan Sahay is an AI citizen assistance platform. Not affiliated directly with any state or federal government entity. Information is gathered from official public directories. All rights reserved.",
    footerDev: "System design and architecture developed by Lipsa for citizen awareness.",
    footerDirTitle: "National Directory Links",
    footerHelpTitle: "Emergency Helplines",
    footerDevTitle: "Developer Information",
    
    // Dynamic screen translation keys
    micBlockedTitle: "Microphone Permission Blocked",
    micBlockedDesc: "This voice assistant requires microphone permission to function. Please click the lock icon (🔒) in your browser's search bar, allow the microphone, and reload the webpage.",
    btnCancel: "Cancel",
    btnReload: "Reload Page",
    callCompletedTitle: "Consultation Completed",
    callCompletedDesc: "The voice call session has ended. You can start a new consultation below.",
    btnStartNew: "Start New Voice Call",
    btnReturnHome: "Return to Home Portal",
    callDurationLabel: "Call Duration:",
    secondsLabel: "seconds",
    minutesLabel: "minutes"
  },
  "Hindi (हिन्दी)": {
    platformTitle: "जन सहाय (Jan Sahay)",
    platformSubtitle: "आपका भरोसेमंद डिजिटल साथी",
    navHome: "मुख्य पृष्ठ",
    navSchemes: "योजनाएं खोजें",
    navFraud: "धोखाधड़ी से सुरक्षा",
    navComplaint: "शिकायत हेल्पलाइन",
    heroTitle: "वॉयस एआई के माध्यम से सरकारी योजनाओं की खोज करें और डिजिटल घोटालों से बचें",
    heroDesc: "हिंदी, अंग्रेजी और क्षेत्रीय भाषाओं में प्रश्न पूछने के लिए हमारे एआई नागरिक सलाहकार के साथ एक सुरक्षित वॉयस कॉल शुरू करें। कोई पंजीकरण या लॉगिन की आवश्यकता नहीं है।",
    startCallLabel: "कॉल शुरू करने के लिए क्लिक करें",
    badgeSecure: "🛡️ 100% सुरक्षित",
    badgeVerified: "🏛️ सत्यापित योजना डेटा",
    badgeDirect: "📞 सीधा हेल्पलाइन लिंक",
    cardSchemesTitle: "सरकारी योजनाएं",
    cardSchemesDesc: "कल्याणकारी योजनाओं के लिए खोज मानदंड, आवश्यक दस्तावेज और आवेदन गाइड।",
    cardFraudTitle: "धोखाधड़ी सुरक्षा",
    cardFraudDesc: "UPI कलेक्ट स्कैम चेतावनियां, ओटीपी सुरक्षा टिप्स और फ़िशिंग सुरक्षा।",
    cardFinancialTitle: "वित्तीय साक्षरता",
    cardFinancialDesc: "बुनियादी बचत गाइड, प्रत्यक्ष लाभ अंतरण (DBT) लिंकिंग विवरण।",
    cardComplaintTitle: "शिकायत हेल्पलाइन",
    cardComplaintDesc: "आरबीआई लोकपाल या साइबर क्राइम पोर्टल पर चरण-दर-चरण रिपोर्टिंग गाइड।",
    warningTitle: "🚨 घोटाला चेतावनी बुलेटिन",
    warningFooter: "सुरक्षात्मक कार्रवाई:",
    schemeSearchTitle: "🏛️ योजना खोज और जानकारी",
    schemePlaceholder: "मुख्य शब्दों द्वारा योजनाएं खोजें...",
    eligibilityTitle: "पात्रता मानदंड",
    documentsTitle: "आवश्यक दस्तावेज़",
    applyTitle: "आवेदन की प्रक्रिया",
    backDashboard: "डैशबोर्ड पर वापस जाएं",
    noSchemes: "कोई योजना नहीं मिली",
    noSchemesDesc: "हमें फ़िल्टर मानदंडों से मेल खाने वाली कोई सरकारी योजना नहीं मिली।",
    fraudHubTitle: "🛡️ धोखाधड़ी निवारण केंद्र",
    fraudBanner: "⚠️ आधिकारिक सलाह: अपने बैंक खातों को सुरक्षित रखें। राष्ट्रीय अधिकारी या बैंक अधिकारी कभी भी आपसे आपका UPI पिन, बैंकिंग पासवर्ड या मोबाइल OTP कोड नहीं मांगेंगे।",
    reportActiveBtn: "सक्रिय हमले की रिपोर्ट करें",
    defensiveStepTitle: "सुरक्षात्मक कदम:",
    complaintHeader: "📞 निर्देशित शिकायत सहायता",
    complaintSub: "नीचे दी गई शिकायत की श्रेणी का चयन करें जिसे आप दर्ज करना चाहते हैं:",
    wizardTitle: "शिकायत हेल्पलाइन विज़ार्ड",
    stepText: "चरण",
    complaintType1: "साइबर अपराध या फ़िशिंग लिंक धोखाधड़ी",
    complaintType1Sub: "बिजली बिल, नकली इनाम एसएमएस या ओटीपी लीक का दावा करने वाले लिंक।",
    complaintType2: "UPI लेनदेन विवाद या बैंकिंग धोखाधड़ी",
    complaintType2Sub: "अनधिकृत एटीएम निकासी या यूपीआई कलेक्ट घोटाले के माध्यम से डेबिट किए गए पैसे।",
    complaintType3: "सरकारी योजना पंजीकरण की समस्या",
    complaintType3Sub: "पीएम-किसान या डीबीटी लिंक ब्लॉक होने पर किस्तें नहीं मिलना।",
    btnBack: "चयन पर वापस जाएं",
    disclaimerText: "अस्वीकरण: जन सहाय एक एआई नागरिक सहायता मंच है। यह किसी भी राज्य या संघीय सरकारी संस्था से सीधे संबद्ध नहीं है। जानकारी आधिकारिक सार्वजनिक निर्देशिकाओं से एकत्र की गई है। सभी अधिकार सुरक्षित हैं।",
    footerDev: "नागरिक जागरूकता के लिए Lipsa द्वारा विकसित प्रणाली डिजाइन और वास्तुकला।",
    footerDirTitle: "राष्ट्रीय निर्देशिका लिंक",
    footerHelpTitle: "आपातकालीन हेल्पलाइन",
    footerDevTitle: "डेवलपर की जानकारी",
    
    // Dynamic screen translation keys
    micBlockedTitle: "माइक्रोफोन अनुमति अवरुद्ध",
    micBlockedDesc: "इस वॉयस असिस्टेंट को काम करने के लिए माइक्रोफोन अनुमति की आवश्यकता होती है। कृपया अपने ब्राउज़र के सर्च बार के पास लॉक आइकन (🔒) पर क्लिक करें, माइक्रोफोन की अनुमति दें और वेबपेज को फिर से लोड करें।",
    btnCancel: "रद्द करें",
    btnReload: "पेज रीलोड करें",
    callCompletedTitle: "परामर्श पूरा हुआ",
    callCompletedDesc: "वॉयस कॉल सत्र समाप्त हो गया है। आप नीचे एक नया परामर्श शुरू कर सकते हैं।",
    btnStartNew: "नया वॉयस कॉल शुरू करें",
    btnReturnHome: "होम पोर्टल पर वापस जाएं",
    callDurationLabel: "कॉल की अवधि:",
    secondsLabel: "सेकंड",
    minutesLabel: "मिनट"
  }
};

const FRAUD_TYPES = [
  {
    titleEn: "UPI Collect Request Fraud",
    titleHi: "यूपीआई कलेक्ट रिक्वेस्ट धोखाधड़ी",
    descEn: "Scammers send 'Collect Requests' via GPAY/PhonePe, telling you it is a refund or prize. Remember: You NEVER need to enter your UPI PIN to receive money.",
    descHi: "स्कैमर्स GPAY/PhonePe के जरिए 'कलेक्ट रिक्वेस्ट' भेजते हैं, और कहते हैं कि यह रिफंड या इनाम है। याद रखें: पैसे प्राप्त करने के लिए आपको कभी भी यूपीआई पिन दर्ज करने की आवश्यकता नहीं होती है।",
    prevEn: "Decline any unexpected requests. Only enter PIN to send money.",
    prevHi: "किसी भी अप्रत्याशित अनुरोध को अस्वीकार करें। केवल पैसे भेजने के लिए पिन दर्ज करें।",
    icon: Shield,
    alertLevel: "high"
  },
  {
    titleEn: "OTP & Banking Scams",
    titleHi: "ओटीपी और बैंकिंग घोटाले",
    descEn: "Fraudsters call masquerading as bank managers or government officials, warning that your account is blocked and demanding your OTP.",
    descHi: "धोखाधड़ी करने वाले बैंक प्रबंधकों या सरकारी अधिकारियों का रूप धारण करके कॉल करते हैं, चेतावनी देते हैं कि आपका खाता ब्लॉक हो गया है और आपके ओटीपी की मांग करते हैं।",
    prevEn: "Banks or government portals will never ask for your OTP. Keep it secret.",
    prevHi: "बैंक या सरकारी पोर्टल कभी भी आपका ओटीपी नहीं मांगेंगे। इसे गुप्त रखें।",
    icon: AlertTriangle,
    alertLevel: "high"
  },
  {
    titleEn: "Fake Electricity / Bill Links",
    titleHi: "फर्जी बिजली / बिल लिंक",
    descEn: "SMS warnings claiming your power will be cut tonight unless you click a link and pay a small registration fee or update KYC.",
    descHi: "एसएमएस चेतावनियां जिसमें दावा किया जाता है कि आज रात आपकी बिजली काट दी जाएगी जब तक कि आप एक लिंक पर क्लिक करके एक छोटा पंजीकरण शुल्क नहीं देते या केवाईसी अपडेट नहीं करते।",
    prevEn: "Never click links from personal mobile numbers. Verify via official bills.",
    prevHi: "व्यक्तिगत मोबाइल नंबरों के लिंक पर कभी क्लिक न करें। आधिकारिक बिलों के माध्यम से सत्यापित करें।",
    icon: Landmark,
    alertLevel: "medium"
  },
  {
    titleEn: "Fake Instant Loan Apps",
    titleHi: "फर्जी इंस्टेंट लोन ऐप्स",
    descEn: "Malicious mobile apps offering collateral-free loans instantly, which steal your phone contacts and harass you with blackmail.",
    descHi: "बिना गारंटी के तुरंत ऋण देने वाले दुर्भावनापूर्ण मोबाइल ऐप, जो आपके फोन संपर्कों को चुराते हैं और ब्लैकमेल करके आपको परेशान करते हैं।",
    prevEn: "Only use RBI-registered bank apps. Avoid downloading apps from web links.",
    prevHi: "केवल आरबीआई-पंजीकृत बैंक ऐप्स का उपयोग करें। वेब लिंक से ऐप्स डाउनलोड करने से बचें।",
    icon: Wallet,
    alertLevel: "high"
  }
];

const SCHEMES_DATA = [
  {
    nameEn: "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
    nameHi: "प्रधानमंत्री किसान सम्मान निधि (पीएम-किसान)",
    categoryEn: "Agriculture",
    categoryHi: "कृषि",
    descEn: "Provides ₹6,000 yearly income support to all landholding farmer families across India, paid in three equal installments of ₹2,000 direct to bank accounts.",
    descHi: "भारत भर के सभी भूमिधारक किसान परिवारों को ₹6,000 वार्षिक आय सहायता प्रदान करता है, जिसका भुगतान तीन समान किस्तों में सीधे बैंक खातों में किया जाता है।",
    eligibilityEn: "All landholder farmer families across the country.",
    eligibilityHi: "देश भर के सभी भूमिधारक किसान परिवार।",
    documentsEn: "Aadhaar Card, Land Holding Records, Bank Account Details.",
    documentsHi: "आधार कार्ड, भूमि धारक रिकॉर्ड, बैंक खाता विवरण।",
    applyEn: "Register on PM-Kisan portal or visit your nearest Common Service Centre (CSC).",
    applyHi: "पीएम-किसान पोर्टल पर पंजीकरण करें या अपने नजदीकी कॉमन सर्विस सेंटर (CSC) पर जाएं।"
  },
  {
    nameEn: "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
    nameHi: "प्रधानमंत्री जन धन योजना (पीएमजेडीवाई)",
    categoryEn: "Banking",
    categoryHi: "बैंकिंग",
    descEn: "National Mission for Financial Inclusion to ensure access to financial services like savings bank accounts, credit, insurance, and pensions affordably.",
    descHi: "बचत बैंक खातों, ऋण, बीमा और पेंशन जैसी वित्तीय सेवाओं तक किफायती पहुंच सुनिश्चित करने के लिए वित्तीय समावेशन का राष्ट्रीय मिशन।",
    eligibilityEn: "Any Indian citizen who does not have an active bank account.",
    eligibilityHi: "कोई भी भारतीय नागरिक जिसके पास सक्रिय बैंक खाता नहीं है।",
    documentsEn: "Aadhaar Card, PAN Card, or official identity documents.",
    documentsHi: "आधार कार्ड, पैन कार्ड, या आधिकारिक पहचान दस्तावेज।",
    applyEn: "Visit any commercial bank branch or authorized Bank Mitra.",
    applyHi: "किसी भी व्यावसायिक बैंक शाखा या अधिकृत बैंक मित्र से मिलें।"
  },
  {
    nameEn: "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
    nameHi: "प्रधानमंत्री सुरक्षा बीमा योजना (पीएमएसबीवाई)",
    categoryEn: "Insurance",
    categoryHi: "बीमा",
    descEn: "Accident insurance scheme offering ₹2 Lakh cover for accidental death or full disability at a premium of just ₹20 per year.",
    descHi: "दुर्घटना बीमा योजना जो मात्र ₹20 प्रति वर्ष के प्रीमियम पर आकस्मिक मृत्यु या पूर्ण विकलांगता के लिए ₹2 लाख का कवर प्रदान करती है।",
    eligibilityEn: "Citizens aged 18 to 70 years with active bank accounts.",
    eligibilityHi: "सक्रिय बैंक खातों वाले 18 से 70 वर्ष की आयु के नागरिक।",
    documentsEn: "Bank account linkage authorization form, Aadhaar Card.",
    documentsHi: "बैंक खाता लिंक प्राधिकरण फॉर्म, आधार कार्ड।",
    applyEn: "Apply via internet banking or fill the application at your savings bank.",
    applyHi: "इंटरनेट बैंकिंग के माध्यम से आवेदन करें या अपने बचत बैंक में आवेदन पत्र भरें।"
  },
  {
    nameEn: "Atal Pension Yojana (APY)",
    nameHi: "अटल पेंशन योजना (एपीवाई)",
    categoryEn: "Pension",
    categoryHi: "पेंशन",
    descEn: "Guaranteed pension scheme targeting unorganized sector workers, providing a monthly pension ranging from ₹1,000 to ₹5,000 after age 60.",
    descHi: "असंगठित क्षेत्र के श्रमिकों को लक्षित करने वाली गारंटीकृत पेंशन योजना, जो 60 वर्ष की आयु के बाद ₹1,000 से ₹5,000 तक की मासिक पेंशन प्रदान करती है।",
    eligibilityEn: "All citizens aged 18 to 40 years.",
    eligibilityHi: "18 से 40 वर्ष की आयु के सभी नागरिक।",
    documentsEn: "Savings bank account number, mobile number.",
    documentsHi: "बचत बैंक खाता संख्या, मोबाइल नंबर।",
    applyEn: "Submit the APY registration form to your primary bank branch.",
    applyHi: "अपनी प्राथमिक बैंक शाखा में एपीवाई पंजीकरण फॉर्म जमा करें।"
  }
];

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  isCallEnded = false,
  onRestartCall,
  micError = false,
  onDismissMicError,
  currentTab = 'home',
  onTabChange,
  ref,
  callDuration = null,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {

  const [activeFraudIdx, setActiveFraudIdx] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [textSize, setTextSize] = useState<'normal' | 'large'>('normal');
  const [selectedLanguage, setSelectedLanguage] = useState("English");

  // Complaint Wizard States
  const [complaintStep, setComplaintStep] = useState(1);
  const [selectedComplaintType, setSelectedComplaintType] = useState("");

  // Load Google Translate Widget dynamically on mount
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (document.getElementById('google-translate-script')) return;

    (window as any).googleTranslateElementInit = () => {
      new (window as any).google.translate.TranslateElement({
        pageLanguage: 'en',
        includedLanguages: 'en,hi,te,ta,mr,bn,gu,kn,ml,pa,ur',
        layout: (window as any).google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false
      }, 'google_translate_element');
    };

    const addScript = document.createElement('script');
    addScript.id = 'google-translate-script';
    addScript.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    document.body.appendChild(addScript);
  }, []);

  const handlePrevFraud = () => {
    setActiveFraudIdx((prev) => (prev - 1 + FRAUD_TYPES.length) % FRAUD_TYPES.length);
  };

  const handleNextFraud = () => {
    setActiveFraudIdx((prev) => (prev + 1) % FRAUD_TYPES.length);
  };

  // Determine active translation dictionary based on language state (must be set before returns)
  const isHindi = selectedLanguage === "Hindi (हिन्दी)";
  const t = isHindi ? TRANSLATIONS["Hindi (हिन्दी)"] : TRANSLATIONS["English"];

  // Formatter for dynamic call duration display
  const formatDuration = (secondsTotal: number | null) => {
    if (secondsTotal === null || secondsTotal === undefined) return "";
    const mins = Math.floor(secondsTotal / 60);
    const secs = secondsTotal % 60;
    
    if (mins > 0) {
      return `${mins} ${t.minutesLabel} ${secs} ${t.secondsLabel}`;
    }
    return `${secs} ${t.secondsLabel}`;
  };

  // Filter schemes based on search query and category
  const filteredSchemes = SCHEMES_DATA.filter((scheme) => {
    const name = isHindi ? scheme.nameHi : scheme.nameEn;
    const desc = isHindi ? scheme.descHi : scheme.descEn;
    const category = isHindi ? scheme.categoryHi : scheme.categoryEn;

    const matchesSearch = name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          desc.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === "All" || 
                            category === selectedCategory || 
                            (selectedCategory === "Agriculture" && category === "कृषि") ||
                            (selectedCategory === "Banking" && category === "बैंकिंग") ||
                            (selectedCategory === "Insurance" && category === "बीमा") ||
                            (selectedCategory === "Pension" && category === "पेंशन");
    return matchesSearch && matchesCategory;
  });

  const categories = ["All", "Agriculture", "Banking", "Insurance", "Pension"];

  if (micError) {
    return (
      <div ref={ref} className="min-h-screen bg-[#F1F5F9] flex flex-col font-sans w-full">
        {/* Top Banner Ribbon */}
        <div className="h-1.5 w-full bg-gradient-to-r from-[#FF9933] via-white to-[#2E7D32] shrink-0" />
        
        {/* Simplified strip for lang toggle */}
        <div className="bg-white py-3 px-4 border-b border-slate-200 flex justify-between items-center">
          <span className="font-bold text-[#0F4C81]">{t.platformTitle}</span>
          <div id="google_translate_element" className="border border-slate-200 rounded shadow-inner overflow-hidden text-xs bg-slate-50" />
        </div>

        <div className="flex-1 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-8 shadow-md border-t-4 border-rose-600 max-w-xl w-full text-left">
            <div className="w-12 h-12 bg-rose-100 rounded-full flex items-center justify-center mb-4 text-rose-650">
              <ShieldAlert className="w-6 h-6" />
            </div>

            <h2 className="text-xl font-bold text-slate-900 mb-2">{t.micBlockedTitle}</h2>
            <p className="text-slate-600 text-sm mb-6 leading-relaxed">
              {t.micBlockedDesc}
            </p>

            <div className="flex gap-4">
              {onDismissMicError && (
                <Button variant="outline" onClick={onDismissMicError} className="px-6 border-slate-300 text-slate-707 hover:bg-slate-50">
                  {t.btnCancel}
                </Button>
              )}
              <Button onClick={() => window.location.reload()} className="bg-[#2E7D32] hover:bg-[#1B5E20] text-white font-bold px-6">
                {t.btnReload}
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isCallEnded) {
    return (
      <div ref={ref} className="min-h-screen bg-[#F1F5F9] flex flex-col font-sans w-full">
        {/* Top Banner Ribbon */}
        <div className="h-1.5 w-full bg-gradient-to-r from-[#FF9933] via-white to-[#2E7D32] shrink-0" />
        
        {/* Simplified strip for lang toggle */}
        <div className="bg-white py-3 px-4 border-b border-slate-200 flex justify-between items-center">
          <span className="font-bold text-[#0F4C81]">{t.platformTitle}</span>
          <div id="google_translate_element" className="border border-slate-200 rounded shadow-inner overflow-hidden text-xs bg-slate-50" />
        </div>

        <div className="flex-1 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-8 shadow-md border-t-4 border-[#0F4C81] max-w-lg w-full text-left">
            <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mb-4 text-[#2E7D32]">
              <CheckCircle className="w-6 h-6" />
            </div>

            <h2 className="text-xl font-bold text-slate-900 mb-2">{t.callCompletedTitle}</h2>
            <p className="text-slate-600 text-sm mb-4">
              {t.callCompletedDesc}
            </p>

            {/* Display Call Duration here */}
            {callDuration !== null && (
              <div className="bg-slate-50 border border-slate-200 rounded p-3 text-xs font-bold text-slate-700 mb-6 flex items-center gap-2">
                <span>⏱️</span>
                <span>{t.callDurationLabel} <strong className="text-[#0F4C81]">{formatDuration(callDuration)}</strong></span>
              </div>
            )}

            <div className="flex flex-col gap-3">
              <Button 
                onClick={onRestartCall} 
                className="bg-[#2E7D32] hover:bg-[#1B5E20] text-white font-bold py-3"
              >
                {t.btnStartNew}
              </Button>
              <button 
                onClick={() => window.location.reload()} 
                className="text-xs text-slate-500 hover:underline font-semibold"
              >
                {t.btnReturnHome}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const fraudTitle = isHindi ? FRAUD_TYPES[activeFraudIdx].titleHi : FRAUD_TYPES[activeFraudIdx].titleEn;
  const fraudDesc = isHindi ? FRAUD_TYPES[activeFraudIdx].descHi : FRAUD_TYPES[activeFraudIdx].descEn;
  const fraudPrev = isHindi ? FRAUD_TYPES[activeFraudIdx].prevHi : FRAUD_TYPES[activeFraudIdx].prevEn;

  return (
    <div ref={ref} className={`min-h-screen bg-[#F1F5F9] text-slate-800 flex flex-col font-sans w-full overflow-x-hidden ${textSize === 'large' ? 'text-lg' : 'text-sm'}`}>
      
      {/* Top Banner Ribbon */}
      <div className="h-1.5 w-full bg-gradient-to-r from-[#FF9933] via-white to-[#2E7D32] shrink-0" />

      {/* Main Header Logo Strip */}
      <div className="bg-white py-4 px-4 border-b border-slate-200 shrink-0 shadow-sm">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 border border-slate-300 rounded-md flex flex-col items-center justify-center overflow-hidden shrink-0">
              <div className="h-1/3 w-full bg-[#FF9933]" />
              <div className="h-1/3 w-full bg-white flex items-center justify-center"><span className="text-[6px] text-blue-800">☸</span></div>
              <div className="h-1/3 w-full bg-[#2E7D32]" />
            </div>
            <div className="text-left">
              <h1 className="text-xl font-bold tracking-tight text-[#0F4C81]">{t.platformTitle}</h1>
              <p className="text-xs text-slate-550 font-bold uppercase tracking-wider">{t.platformSubtitle}</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Accessibility Font Sizers */}
            <div className="flex border border-slate-350 rounded overflow-hidden bg-white">
              <button 
                onClick={() => setTextSize('normal')} 
                className={`px-2.5 py-0.5 text-xs font-bold border-r border-slate-300 ${textSize === 'normal' ? 'bg-slate-200 text-slate-900' : 'bg-white hover:bg-slate-50'}`}
              >
                A
              </button>
              <button 
                onClick={() => setTextSize('large')} 
                className={`px-2.5 py-0.5 text-xs font-bold ${textSize === 'large' ? 'bg-slate-200 text-slate-900' : 'bg-white hover:bg-slate-50'}`}
              >
                A+
              </button>
            </div>

            {/* Google Translate Target Container */}
            <div id="google_translate_element" className="border border-slate-250 rounded shadow-inner overflow-hidden text-xs bg-slate-50" />
          </div>
        </div>
      </div>

      {/* Top Icon Navigation */}
      <nav className="shrink-0 border-b border-slate-200 bg-white shadow-sm">
        <div className="mx-auto flex max-w-5xl items-center justify-center overflow-x-auto">
          <button
            onClick={() => onTabChange?.('home')}
            aria-label={t.navHome}
            className={`flex min-w-[120px] flex-col items-center justify-center gap-1 border-b-4 px-5 py-3 transition-colors ${
              currentTab === 'home'
                ? 'border-[#FF9933] text-[#0F4C81]'
                : 'border-transparent text-slate-500 hover:text-[#0F4C81]'
            }`}
          >
            <HouseIcon active={currentTab === 'home'} />
            <span className="text-[11px] font-bold">{t.navHome}</span>
          </button>

          <button
            onClick={() => onTabChange?.('schemes')}
            aria-label={t.navSchemes}
            className={`flex min-w-[120px] flex-col items-center justify-center gap-1 border-b-4 px-5 py-3 transition-colors ${
              currentTab === 'schemes'
                ? 'border-[#FF9933] text-[#0F4C81]'
                : 'border-transparent text-slate-500 hover:text-[#0F4C81]'
            }`}
          >
            <Search size={23} strokeWidth={2.2} />
            <span className="text-[11px] font-bold">{t.navSchemes}</span>
          </button>

          <button
            onClick={() => onTabChange?.('fraud')}
            aria-label={t.navFraud}
            className={`flex min-w-[120px] flex-col items-center justify-center gap-1 border-b-4 px-5 py-3 transition-colors ${
              currentTab === 'fraud'
                ? 'border-[#FF9933] text-[#0F4C81]'
                : 'border-transparent text-slate-500 hover:text-[#0F4C81]'
            }`}
          >
            <Shield size={23} strokeWidth={2.2} />
            <span className="text-[11px] font-bold">{t.navFraud}</span>
          </button>

          <button
            onClick={() => onTabChange?.('complaint')}
            aria-label={t.navComplaint}
            className={`flex min-w-[120px] flex-col items-center justify-center gap-1 border-b-4 px-5 py-3 transition-colors ${
              currentTab === 'complaint'
                ? 'border-[#FF9933] text-[#0F4C81]'
                : 'border-transparent text-slate-500 hover:text-[#0F4C81]'
            }`}
          >
            <FileText size={23} strokeWidth={2.2} />
            <span className="text-[11px] font-bold">{t.navComplaint}</span>
          </button>

          <button
            onClick={() => onTabChange?.('dashboard')}
            aria-label={t.navDashboard}
            className={`flex min-w-[120px] flex-col items-center justify-center gap-1 border-b-4 px-5 py-3 transition-colors ${
              currentTab === 'dashboard'
                ? 'border-[#FF9933] text-[#0F4C81]'
                : 'border-transparent text-slate-500 hover:text-[#0F4C81]'
            }`}
          >
            <BarChartIcon active={currentTab === 'dashboard'} />
            <span className="text-[11px] font-bold">{t.navDashboard}</span>
          </button>
        </div>
      </nav>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-8">
        
        {currentTab === 'home' && (
          <div className="space-y-8">
            
            {/* HERO BANNER WITH INTERACTIVE DIAL ACTIVATOR */}
            <section className="bg-white rounded border border-slate-200 shadow-sm p-6 sm:p-10 flex flex-col lg:flex-row items-center justify-between gap-8 relative overflow-hidden">
              <div className="absolute left-0 top-0 bottom-0 w-2 bg-[#FF9933]" />
              
              <div className="space-y-4 max-w-2xl text-left">
                <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#0F4C81]">
                  {t.heroTitle}
                </h2>
                <p className="text-slate-655 text-sm leading-relaxed font-semibold">
                  {t.heroDesc}
                </p>
                <div className="flex flex-wrap gap-2 text-xs text-slate-505 font-bold">
                  <span className="bg-slate-50 border border-slate-200 px-3 py-1 rounded">{t.badgeSecure}</span>
                  <span className="bg-slate-50 border border-slate-200 px-3 py-1 rounded">{t.badgeVerified}</span>
                  <span className="bg-slate-50 border border-slate-200 px-3 py-1 rounded">{t.badgeDirect}</span>
                </div>
              </div>

              {/* Centered Circular Activator Dial */}
              <div className="shrink-0 w-full lg:w-auto flex items-center justify-center">
                <div 
                  onClick={onStartCall}
                  className="relative bg-slate-55 w-44 h-44 rounded-full flex flex-col items-center justify-center border border-slate-200 cursor-pointer hover:scale-[1.03] active:scale-95 transition-all shadow-[0_0_20px_rgba(46,125,50,0.15)] hover:shadow-[0_0_30px_rgba(46,125,50,0.25)] group"
                >
                  <div className="absolute w-[92%] h-[92%] border border-dashed border-slate-300 rounded-full animate-spin" style={{ animationDuration: '45s' }} />
                  <div className="absolute w-[82%] h-[82%] border border-[#2E7D32]/10 rounded-full animate-pulse" />
                  
                  <div className="w-24 h-24 bg-[#2E7D32] hover:bg-[#1B5E20] rounded-full flex items-center justify-center shadow-md group-hover:scale-105 transition-all border-2 border-white">
                    <Mic className="w-10 h-10 text-white" />
                  </div>
                  
                  <span className="mt-3 text-[9px] font-extrabold text-[#2E7D32] tracking-wider uppercase animate-pulse">
                    {t.startCallLabel}
                  </span>
                </div>
              </div>
            </section>

            {/* Quick Cards Grid - Elevate on Hover */}
            <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div 
                onClick={() => onTabChange?.('schemes')}
                className="bg-white rounded p-5 border border-slate-200 hover:border-[#0F4C81]/25 hover:shadow-lg transition-all duration-300 hover:-translate-y-1.5 cursor-pointer text-left space-y-4"
              >
                <div className="w-12 h-12 bg-slate-50 border border-slate-200 text-[#0F4C81] rounded flex items-center justify-center font-bold text-lg">🏛️</div>
                <h3 className="font-bold text-slate-905">{t.cardSchemesTitle}</h3>
                <p className="text-xs text-slate-600 leading-relaxed font-semibold">{t.cardSchemesDesc}</p>
              </div>

              <div 
                onClick={() => onTabChange?.('fraud')}
                className="bg-white rounded p-5 border border-slate-200 hover:border-[#0F4C81]/25 hover:shadow-lg transition-all duration-300 hover:-translate-y-1.5 cursor-pointer text-left space-y-4"
              >
                <div className="w-12 h-12 bg-slate-50 border border-slate-200 text-rose-600 rounded flex items-center justify-center font-bold text-lg">🚨</div>
                <h3 className="font-bold text-slate-905">{t.cardFraudTitle}</h3>
                <p className="text-xs text-slate-600 leading-relaxed font-semibold">{t.cardFraudDesc}</p>
              </div>

              <div className="bg-white rounded p-5 border border-slate-200 hover:shadow-lg transition-all duration-300 hover:-translate-y-1.5 text-left space-y-4">
                <div className="w-12 h-12 bg-slate-50 border border-slate-200 text-emerald-600 rounded flex items-center justify-center font-bold text-lg">💰</div>
                <h3 className="font-bold text-slate-905">{t.cardFinancialTitle}</h3>
                <p className="text-xs text-slate-600 leading-relaxed font-semibold">{t.cardFinancialDesc}</p>
              </div>

              <div 
                onClick={() => onTabChange?.('complaint')}
                className="bg-white rounded p-5 border border-slate-200 hover:border-[#0F4C81]/25 hover:shadow-lg transition-all duration-300 hover:-translate-y-1.5 cursor-pointer text-left space-y-4"
              >
                <div className="w-12 h-12 bg-slate-50 border border-slate-200 text-amber-600 rounded flex items-center justify-center font-bold text-lg">📞</div>
                <h3 className="font-bold text-slate-905">{t.cardComplaintTitle}</h3>
                <p className="text-xs text-slate-600 leading-relaxed font-semibold">{t.cardComplaintDesc}</p>
              </div>
            </section>

            {/* Slider Warning Banner - Elevate on Hover */}
            <section className="bg-white rounded border border-slate-200 p-6 text-left relative shadow-sm hover:shadow-md hover:border-slate-300 transition-all duration-300">
              <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
                <h3 className="font-bold text-[#0F4C81] text-base flex items-center gap-2">
                  <span>🚨</span> {t.warningTitle}
                </h3>
                <div className="flex items-center gap-1.5">
                  <button onClick={handlePrevFraud} className="p-1.5 rounded bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700">
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button onClick={handleNextFraud} className="p-1.5 rounded bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700">
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="min-h-24">
                <h4 className="font-bold text-slate-900 text-sm mb-1">{fraudTitle}</h4>
                <p className="text-xs text-slate-600 leading-relaxed mb-4 font-semibold">{fraudDesc}</p>
                <div className="bg-rose-50 border border-rose-200 rounded p-2.5 text-xs text-rose-900 font-bold">
                  {t.warningFooter} {fraudPrev}
                </div>
              </div>
            </section>

          </div>
        )}

        {/* TAB: SCHEMES DIRECTORY */}
        {currentTab === 'schemes' && (
          <div className="space-y-6">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
              <h2 className="text-xl font-bold text-[#0F4C81]">{t.schemeSearchTitle}</h2>
              <Button onClick={onStartCall} className="bg-[#2E7D32] hover:bg-[#1B5E20] text-white font-bold rounded flex items-center gap-2 border-0">
                <Mic className="w-4 h-4 animate-bounce" /> {t.btnStart}
              </Button>
            </div>

            {/* Filters */}
            <div className="bg-white rounded border border-slate-200 p-4 flex flex-col md:flex-row gap-4 items-center justify-between shadow-xs">
              <div className="relative w-full md:max-w-md">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-455" />
                <input 
                  type="text" 
                  placeholder={t.schemePlaceholder}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded text-xs text-slate-900 focus:outline-none focus:border-[#0F4C81] font-semibold bg-slate-50"
                />
              </div>

              <div className="flex flex-wrap gap-1.5 w-full md:w-auto">
                {categories.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`px-3 py-1.5 rounded text-xs font-bold border transition-colors ${
                      selectedCategory === cat 
                        ? 'bg-[#0F4C81] text-white border-[#0F4C81]' 
                        : 'bg-slate-50 text-slate-655 border-slate-250 hover:bg-slate-100'
                    }`}
                  >
                    {isHindi && cat === "Agriculture" ? "कृषि" : isHindi && cat === "Banking" ? "बैंकिंग" : isHindi && cat === "Insurance" ? "बीमा" : isHindi && cat === "Pension" ? "पेंशन" : cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Scheme Cards - Elevate on Hover */}
            {filteredSchemes.length > 0 ? (
              filteredSchemes.map((scheme, idx) => (
                <div key={idx} className="bg-white rounded border border-slate-200 shadow-sm p-6 text-left relative overflow-hidden hover:shadow-md hover:border-slate-350 transition-all duration-350 hover:-translate-y-1">
                  <div className="absolute top-0 left-0 bottom-0 w-1.5 bg-[#FF9933]" />
                  
                  <div className="flex items-center justify-between gap-3 mb-3">
                    <h3 className="font-bold text-slate-905 text-base">{isHindi ? scheme.nameHi : scheme.nameEn}</h3>
                    <span className="text-[10px] font-extrabold text-[#0F4C81] bg-[#0F4C81]/10 px-2.5 py-0.5 rounded border border-[#0F4C81]/25 uppercase tracking-wider">
                      {isHindi ? scheme.categoryHi : scheme.categoryEn}
                    </span>
                  </div>

                  <p className="text-slate-655 text-xs leading-relaxed mb-4 border-b border-slate-101 pb-3 font-semibold">
                    {isHindi ? scheme.descHi : scheme.descEn}
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs text-slate-700">
                    <div className="space-y-1.5">
                      <span className="font-extrabold text-[#0F4C81] block">{t.eligibilityTitle}</span>
                      <p className="bg-slate-55 p-3 rounded border border-slate-200 font-semibold leading-relaxed">{isHindi ? scheme.eligibilityHi : scheme.eligibilityEn}</p>
                    </div>
                    <div className="space-y-1.5">
                      <span className="font-extrabold text-[#0F4C81] block">{t.documentsTitle}</span>
                      <p className="bg-slate-55 p-3 rounded border border-slate-200 font-semibold leading-relaxed">{isHindi ? scheme.documentsHi : scheme.documentsEn}</p>
                    </div>
                    <div className="space-y-1.5">
                      <span className="font-extrabold text-[#0F4C81] block">{t.applyTitle}</span>
                      <p className="bg-slate-55 p-3 rounded border border-slate-200 font-semibold leading-relaxed">{isHindi ? scheme.applyHi : scheme.applyEn}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="bg-white rounded border border-slate-200 p-12 text-center shadow-xs">
                <BookOpen className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                <h3 className="text-lg font-bold text-slate-800 mb-1">{t.noSchemes}</h3>
                <p className="text-slate-500 text-sm font-semibold">{t.noSchemesDesc}</p>
              </div>
            )}
          </div>
        )}

        {/* TAB: FRAUD PROTECTION */}
        {currentTab === 'fraud' && (
          <div className="space-y-6 text-left">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
              <h2 className="text-xl font-bold text-[#0F4C81]">{t.fraudHubTitle}</h2>
              <Button 
                onClick={() => onTabChange?.('complaint')} 
                className="bg-rose-600 hover:bg-rose-705 text-white font-bold rounded border-0 shrink-0"
              >
                {t.reportActiveBtn}
              </Button>
            </div>
            
            <div className="bg-[#FFF9E6] border border-amber-300 rounded p-4 text-amber-900 text-xs font-bold leading-relaxed shadow-xs">
              {t.fraudBanner}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {FRAUD_TYPES.map((fraud, idx) => {
                const FraudIcon = fraud.icon;
                const title = isHindi ? fraud.titleHi : fraud.titleEn;
                const desc = isHindi ? fraud.descHi : fraud.descEn;
                const prev = isHindi ? fraud.prevHi : fraud.prevEn;

                return (
                  <div key={idx} className="bg-white rounded border border-slate-200 shadow-sm p-5 text-left relative overflow-hidden flex flex-col justify-between hover:shadow-lg hover:border-slate-350 transition-all duration-300 hover:-translate-y-1.5">
                    <div className="absolute top-0 left-0 right-0 h-1 bg-rose-600" />
                    
                    <div className="space-y-3">
                      <h3 className="font-bold text-slate-905 text-sm flex items-center gap-2">
                        <FraudIcon className="w-5 h-5 text-rose-600" /> {title}
                      </h3>
                      <p className="text-xs text-slate-600 leading-relaxed font-semibold">{desc}</p>
                    </div>

                    <div className="mt-6 pt-3 border-t border-slate-100 bg-slate-50 p-3 rounded border border-slate-200 text-xs font-bold text-slate-700">
                      {t.defensiveStepTitle} {prev}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB: COMPLAINT HELP */}
        {currentTab === 'complaint' && (
          <div className="max-w-2xl mx-auto space-y-6">
            <h2 className="text-xl font-bold text-[#0F4C81] text-left border-b border-slate-200 pb-4">{t.complaintHeader}</h2>
            
            <div className="bg-white rounded border border-slate-200 shadow-sm p-6 sm:p-8 text-left">
              <div className="mb-6">
                <h3 className="font-bold text-slate-900 text-base">{t.wizardTitle}</h3>
                <p className="text-xs text-slate-550 font-semibold">{t.complaintSub}</p>
              </div>

              {complaintStep === 1 ? (
                <div className="space-y-3">
                  <button 
                    onClick={() => {
                      setSelectedComplaintType("Cybercrime / Phishing Fraud");
                      setComplaintStep(2);
                    }}
                    className="w-full bg-slate-50 hover:bg-slate-100 p-4 rounded border border-slate-250 text-left text-xs font-bold text-slate-808 flex items-center justify-between transition-all hover:shadow-md hover:border-[#0F4C81]/30 hover:-translate-y-1 duration-300"
                  >
                    <div className="space-y-0.5">
                      <span className="block">{t.complaintType1}</span>
                      <span className="block text-[10px] text-slate-455 font-semibold">{t.complaintType1Sub}</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-455" />
                  </button>
                  <button 
                    onClick={() => {
                      setSelectedComplaintType("Banking & UPI Fraud");
                      setComplaintStep(2);
                    }}
                    className="w-full bg-slate-50 hover:bg-slate-100 p-4 rounded border border-slate-250 text-left text-xs font-bold text-slate-808 flex items-center justify-between transition-all hover:shadow-md hover:border-[#0F4C81]/30 hover:-translate-y-1 duration-300"
                  >
                    <div className="space-y-0.5">
                      <span className="block">{t.complaintType2}</span>
                      <span className="block text-[10px] text-slate-455 font-semibold">{t.complaintType2Sub}</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-455" />
                  </button>
                  <button 
                    onClick={() => {
                      setSelectedComplaintType("Government Scheme Issue");
                      setComplaintStep(2);
                    }}
                    className="w-full bg-slate-50 hover:bg-slate-100 p-4 rounded border border-slate-250 text-left text-xs font-bold text-slate-808 flex items-center justify-between transition-all hover:shadow-md hover:border-[#0F4C81]/30 hover:-translate-y-1 duration-300"
                  >
                    <div className="space-y-0.5">
                      <span className="block">{t.complaintType3}</span>
                      <span className="block text-[10px] text-slate-455 font-semibold">{t.complaintType3Sub}</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-slate-455" />
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-xs font-bold">
                    <span>{t.stepText} 2: <span className="text-primary">{selectedComplaintType}</span></span>
                    <button onClick={() => setComplaintStep(1)} className="text-slate-505 hover:underline">{isHindi ? "बदलें" : "Change"}</button>
                  </div>

                  <div className="bg-slate-50 border border-slate-200 rounded p-4 text-xs font-bold text-slate-705 space-y-3 leading-relaxed">
                    {selectedComplaintType === "Cybercrime / Phishing Fraud" && (
                      isHindi ? (
                        <>
                          <p>1. वित्तीय धोखाधड़ी की रिपोर्ट करने के लिए तुरंत राष्ट्रीय साइबर अपराध हेल्पलाइन <strong className="text-rose-650">1930</strong> पर कॉल करें।</p>
                          <p>2. आधिकारिक राष्ट्रीय साइबर अपराध रिपोर्टिंग पोर्टल पर एक औपचारिक शिकायत दर्ज करें: <a href="https://cybercrime.gov.in" target="_blank" className="text-primary underline">cybercrime.gov.in</a>.</p>
                        </>
                      ) : (
                        <>
                          <p>1. Contact the National Cyber Crime Hotline at <strong className="text-rose-650">1930</strong> immediately to report financial fraud transfers.</p>
                          <p>2. Prepare files and submit digital complaints directly at <a href="https://cybercrime.gov.in" target="_blank" className="text-primary underline">cybercrime.gov.in</a>.</p>
                        </>
                      )
                    )}
                    {selectedComplaintType === "Banking & UPI Fraud" && (
                      isHindi ? (
                        <>
                          <p>1. अपने बैंक के कस्टमर केयर नंबर पर कॉल करें और अपने एटीएम/डेबिट कार्ड को ब्लॉक करें।</p>
                          <p>2. यदि बैंक 30 दिनों के भीतर शिकायत का समाधान नहीं करता है, तो आरबीआई लोकपाल पोर्टल पर शिकायत दर्ज करें: <a href="https://cms.rbi.org.in" target="_blank" className="text-primary underline">cms.rbi.org.in</a>.</p>
                        </>
                      ) : (
                        <>
                          <p>1. Call customer service support numbers printed on the reverse side of bank cards.</p>
                          <p>2. If dispute issues remain open after 30 days, file claims with RBI's Ombudsman online: <a href="https://cms.rbi.org.in" target="_blank" className="text-primary underline">cms.rbi.org.in</a>.</p>
                        </>
                      )
                    )}
                    {selectedComplaintType === "Government Scheme Issue" && (
                      isHindi ? (
                        <>
                          <p>1. सुनिश्चित करें कि आपका बैंक खाता आधार से लिंक है और डीबीटी (डायरेक्ट बेनिफिट ट्रांसफर) सक्षम है।</p>
                          <p>2. यदि योजना का भुगतान विफल रहता है, तो केंद्रीकृत लोक शिकायत निवारण प्रणाली पर शिकायत दर्ज करें: <a href="https://pgportal.gov.in" target="_blank" className="text-primary underline">pgportal.gov.in</a>.</p>
                        </>
                      ) : (
                        <>
                          <p>1. Confirm that Aadhaar is mapped to your primary bank account (DBT enabled).</p>
                          <p>2. If scheme disbursements fail, submit online grievance tickets at <a href="https://pgportal.gov.in" target="_blank" className="text-primary underline">pgportal.gov.in</a>.</p>
                        </>
                      )
                    )}
                  </div>

                  <Button onClick={() => setComplaintStep(1)} className="w-full bg-slate-700 hover:bg-slate-600 text-white rounded text-xs py-3.5 border-0 font-bold">
                    {t.btnBack}
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
{/* TAB: DASHBOARD */}
{currentTab === 'dashboard' && (
  <DashboardView />
)}
      </main>
      {/* Directory Government Footer */}
      <footer className="bg-slate-900 text-slate-350 py-12 px-4 border-t border-slate-800 relative z-10 shrink-0 text-left">
        <div className="max-w-7xl mx-auto space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pb-8 border-b border-slate-800">
            <div className="space-y-3">
              <span className="text-base font-bold text-white block">{t.footerDirTitle}</span>
              <ul className="text-xs space-y-2 text-slate-400 font-semibold">
                <li><a href="https://india.gov.in" target="_blank" className="hover:underline">India Portal (india.gov.in)</a></li>
                <li><a href="https://cybercrime.gov.in" target="_blank" className="hover:underline">Cyber Crime Portal (cybercrime.gov.in)</a></li>
                <li><a href="https://pgportal.gov.in" target="_blank" className="hover:underline">Grievance Portal (pgportal.gov.in)</a></li>
              </ul>
            </div>
            
            <div className="space-y-3">
              <span className="text-base font-bold text-white block">{t.footerHelpTitle}</span>
              <ul className="text-xs space-y-2 text-slate-400 font-bold">
                <li>📞 Cyber Crime Helpline: 1930</li>
                <li>📞 Emergency Police Helpline: 112</li>
                <li>📞 Aadhaar Helpdesk: 1947</li>
              </ul>
            </div>

            <div className="space-y-3">
              <span className="text-base font-bold text-white block">{t.footerDevTitle}</span>
              <div className="text-xs text-slate-400 font-semibold bg-slate-950 p-4 rounded border border-white/5 shadow-inner">
                {t.footerDev}
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <p className="text-[10px] text-slate-500 font-medium leading-relaxed">
              {t.disclaimerText}
            </p>
            <p className="text-[10px] text-slate-500 font-bold">
              &copy; {new Date().getFullYear()} Jan Sahay. Developed by Lipsa. All Rights Reserved.
            </p>
          </div>
        </div>
      </footer>

    </div>
  );
};
