"""
Topic definitions for the daily briefing.
Each topic has queries for Tavily search and context for Claude synthesis.
"""

TOPICS = [
    {
        "id": "gut_health",
        "emoji": "🧬",
        "title": "Gut Health & Microbiome",
        "queries": [
            "L reuteri probiotic latest research clinical trials 2026",
            "microbiome improvement foods strategies new studies",
            "foods that damage gut microbiome avoid emulsifiers",
            "L reuteri ATCC 17938 DSM 17938 benefits dosage",
        ],
        "context": (
            "Focus on L. reuteri specifically (strains, dosage, fermentation protocol), "
            "best foods to eat for microbiome diversity (fermented foods, prebiotic fibers), "
            "foods/ingredients to avoid (emulsifiers, seed oils, artificial sweeteners, ultra-processed), "
            "and recent clinical studies with actionable findings. Include specific strain names, "
            "CFU counts, and timing when available."
        ),
    },
    {
        "id": "netherlands",
        "emoji": "🇳🇱",
        "title": "Netherlands & Expat Life",
        "queries": [
            "Netherlands food safety recalls NVWA 2026",
            "organic biologic food market Lelystad Flevoland Netherlands",
            "best organic food delivery Netherlands online 2026",
            "expat Netherlands 30 percent ruling visa IND news 2026",
        ],
        "context": (
            "Jeff lives near Lelystad, Flevoland as an expat. "
            "Include: organic/biologic markets or farms near Lelystad (within 30km), "
            "best online organic food delivery services in NL, food safety news (NVWA recalls), "
            "expat-relevant tax/visa updates (30% ruling, IND), Dutch food culture news. "
            "Be practical — include store names, websites, locations."
        ),
    },
    {
        "id": "hardware",
        "emoji": "💻",
        "title": "Hardware & Gadgets",
        "queries": [
            "best laptop 2026 performance benchmark review buy",
            "new laptop release 2026 MacBook Lenovo ThinkPad Dell",
            "interesting tech gadgets new release 2026",
            "best GPU value performance March 2026",
        ],
        "context": (
            "Focus on: high-performance laptops with benchmark numbers (CPU, RAM, battery), "
            "best value-for-money options, notable new releases, "
            "interesting gadgets worth buying. Include prices in USD/EUR. "
            "Prioritize productivity and performance over gaming."
        ),
    },
    {
        "id": "wearables",
        "emoji": "⌚",
        "title": "Health Wearables",
        "queries": [
            "health wearables smart ring 2026 new release review",
            "Oura ring Ultrahuman Luna Ring new features 2026",
            "wearable health tracking HRV glucose sleep 2026",
            "best health wearable evidence based review 2026",
        ],
        "context": (
            "Focus on: smart rings (Oura, Ultrahuman Ring Air, Luna Ring Gen 2), "
            "health-focused watches, new sensor capabilities (continuous glucose, HRV, "
            "blood oxygen, body composition), peer-reviewed validation studies, "
            "practical tips on which metrics to track and how to act on them."
        ),
    },
    {
        "id": "ai",
        "emoji": "🤖",
        "title": "AI & Productivity",
        "queries": [
            "new AI tools apps launched this week 2026 try",
            "Claude GPT Gemini new model features update 2026",
            "AI side income make money freelance 2026 strategies",
            "AI productivity automation workflow tools 2026",
        ],
        "context": (
            "Jeff is a tech professional wanting to use AI for productivity and income. "
            "Prioritize: new tools/models launched THIS week worth trying immediately, "
            "practical workflows that save significant time, "
            "concrete ways AI generates side income (freelancing, automation, SaaS), "
            "agentic frameworks, coding assistants, business automation. "
            "Be specific — name the tool, what it does, and why it matters."
        ),
    },
    {
        "id": "jobs",
        "emoji": "✈️",
        "title": "Jobs & Australia Relocation",
        "queries": [
            "Australia cloud architect solutions architect jobs visa sponsorship 2026",
            "Australia 482 visa technology occupations sponsorship 2026",
            "remote cloud AWS DevOps jobs relocation Australia",
            "Australia tech salary cloud architect AUD 2026",
        ],
        "context": (
            "Jeff is a senior cloud/AWS architect interested in relocating to Australia. "
            "Focus on: cloud architect / solutions architect / DevOps/SRE roles in Australia "
            "with 482/494 visa sponsorship, salary ranges (AUD), companies actively hiring, "
            "Green List eligible occupations for fast-track residence, "
            "relocation packages (flights, housing allowance). "
            "Also include remote-to-relocate options. Be specific with company names and links."
        ),
    },
    {
        "id": "etf",
        "emoji": "📈",
        "title": "ETF & Markets",
        "queries": [
            "iShares Core MSCI World UCITS ETF IWDA IE00BK5BQT80 performance 2026",
            "MSCI World index outlook forecast 2026",
            "global equity market ETF trends March 2026",
            "US Europe stock market outlook economic data 2026",
        ],
        "context": (
            "Jeff holds the iShares Core MSCI World UCITS ETF (ISIN: IE00BK5BQT80, ticker: IWDA). "
            "Focus on: IWDA/MSCI World recent performance (%, price), key factors driving movement, "
            "analyst outlooks, macro data (inflation, Fed/ECB rates, earnings), "
            "any relevant global equity ETF news. Include specific numbers and percentages. "
            "Explain implications for a long-term DCA investor."
        ),
    },
    {
        "id": "health",
        "emoji": "🏥",
        "title": "Health Optimization",
        "queries": [
            "best daily supplements evidence longevity 2026 research",
            "improve sleep quality deep sleep tips 2026 study",
            "digestive health stomach issues prevention gut 2026",
            "longevity biohacking protocol daily routine 2026",
        ],
        "context": (
            "Focus on evidence-based, practical optimization: "
            "supplements with strong evidence (magnesium glycinate/threonate, vitamin D3+K2, "
            "omega-3, NMN/NR, NAC, creatine) — include dosages and timing; "
            "sleep optimization (light exposure, temperature, supplements like glycine/apigenin, "
            "consistent schedule); gut/digestive health prevention tips; "
            "longevity practices with best evidence. Prioritize actionable over theoretical."
        ),
    },
    {
        "id": "cloud",
        "emoji": "☁️",
        "title": "Cloud & DevOps",
        "queries": [
            "AWS new service launch announcement March 2026",
            "Azure Kubernetes cloud computing news 2026",
            "serverless Lambda container cloud architecture 2026",
            "AWS CDK Terraform IaC best practices update 2026",
        ],
        "context": (
            "Jeff is a senior cloud/AWS architect. "
            "Focus on: new AWS service launches and updates worth knowing, "
            "Azure/GCP news for cross-cloud context, "
            "Kubernetes/container ecosystem updates, "
            "serverless patterns, IaC (CDK, Terraform, SAM) improvements, "
            "cost optimization strategies, and practical architectural patterns. "
            "Prioritize things that change how you'd architect a solution today."
        ),
    },
]

# Additional topics you could add in the future:
# - 🧠 Mental Performance (nootropics, focus, cognitive enhancement)
# - 💰 Side Income & Freelance (passive income, consulting rates)
# - 🔐 Cybersecurity (cloud security, new CVEs, tools)
# - 🌿 Nutrition Science (specific foods, meal timing, macros research)
# - 🏋️ Exercise & Recovery (training science, HRV-guided recovery)
# - 🌍 Macro & Geopolitics (market-moving global events)
