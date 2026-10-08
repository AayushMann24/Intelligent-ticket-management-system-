"""Retrieval evaluation framework for knowledge base RAG.

Provides a deterministic evaluation dataset and metrics for measuring
retrieval quality without requiring live embedding services.
"""

from dataclasses import dataclass
from typing import Optional

from slugify import slugify
from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeArticle, ArticleStatus, ArticleCategory
from app.models.knowledge_chunk import KnowledgeChunk
from app.services.retrieval import (
    search_similar_chunks_pgvector,
    search_keyword_chunks,
    hybrid_search,
    RetrievalResult,
)
from app.services.embeddings import EmbeddingProvider


# ============================================================
# Evaluation Dataset
# ============================================================

@dataclass
class EvalQuery:
    """A single evaluation query with expected relevant articles."""
    query: str
    # Expected article titles that should be retrieved (in order of relevance)
    expected_articles: list[str]
    # Category this query belongs to (for analysis)
    category: str
    # Description of the query intent
    description: str


# Representative ITSM knowledge queries
EVAL_QUERIES: list[EvalQuery] = [
    EvalQuery(
        query="password reset",
        expected_articles=[
            "How to Reset Your Password",
            "Password Policy and Requirements",
            "Account Lockout Troubleshooting",
        ],
        category="Account",
        description="User needs to reset their password",
    ),
    EvalQuery(
        query="laptop not connecting to wifi",
        expected_articles=[
            "Troubleshooting WiFi Connection Issues",
            "Laptop Network Configuration Guide",
            "Corporate WiFi Setup Instructions",
        ],
        category="Network",
        description="Laptop cannot connect to wireless network",
    ),
    EvalQuery(
        query="vpn troubleshooting",
        expected_articles=[
            "VPN Connection Troubleshooting Guide",
            "Remote Access VPN Setup",
            "Common VPN Error Codes and Solutions",
        ],
        category="Network",
        description="VPN connection problems",
    ),
    EvalQuery(
        query="printer problem",
        expected_articles=[
            "Printer Troubleshooting Steps",
            "Network Printer Configuration",
            "Print Queue Management",
        ],
        category="Hardware",
        description="Printer not working or printing incorrectly",
    ),
    EvalQuery(
        query="account locked",
        expected_articles=[
            "Account Lockout Troubleshooting",
            "How to Unlock Your Account",
            "Password Policy and Requirements",
        ],
        category="Account",
        description="User account is locked after failed login attempts",
    ),
    EvalQuery(
        query="software installation",
        expected_articles=[
            "Software Installation Request Process",
            "Approved Software Catalog",
            "Self-Service Software Portal Guide",
        ],
        category="Software",
        description="Need to install new software on work computer",
    ),
    EvalQuery(
        query="network issue",
        expected_articles=[
            "Network Connectivity Troubleshooting",
            "DNS Resolution Problems",
            "Network Outage Reporting Procedure",
        ],
        category="Network",
        description="General network connectivity problems",
    ),
    EvalQuery(
        query="email not syncing",
        expected_articles=[
            "Email Sync Troubleshooting",
            "Outlook Configuration Guide",
            "Mobile Email Setup Instructions",
        ],
        category="Software",
        description="Email client not synchronizing messages",
    ),
    EvalQuery(
        query="blue screen error",
        expected_articles=[
            "BSOD Troubleshooting Guide",
            "Windows Crash Dump Analysis",
            "Hardware Diagnostic Procedures",
        ],
        category="Hardware",
        description="Computer showing blue screen of death",
    ),
    EvalQuery(
        query="phishing email",
        expected_articles=[
            "Identifying Phishing Emails",
            "Reporting Suspicious Emails",
            "Security Awareness Training",
        ],
        category="Security",
        description="Received suspicious email, need to verify",
    ),
]


# ============================================================
# Mock Embedding Provider for Deterministic Testing
# ============================================================

class MockEmbeddingProvider(EmbeddingProvider):
    """Mock embedding provider that returns deterministic vectors for testing."""

    def __init__(self, dimension: int = 768):
        self._dimension = dimension
        self._cache: dict[str, list[float]] = {}

    @property
    def dimension(self) -> int:
        return self._dimension

    def _text_to_vector(self, text: str) -> list[float]:
        """Generate a deterministic pseudo-random vector from text."""
        import hashlib
        # Create deterministic hash from text
        hash_obj = hashlib.md5(text.lower().encode())
        hash_bytes = hash_obj.digest()

        # Expand to required dimension
        vector = []
        for i in range(self._dimension):
            byte_idx = i % len(hash_bytes)
            # Normalize to [-1, 1] range
            vector.append((hash_bytes[byte_idx] - 127.5) / 127.5)

        return vector

    def embed_text(self, text: str) -> list[float]:
        if text not in self._cache:
            self._cache[text] = self._text_to_vector(text)
        return self._cache[text]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]


# ============================================================
# Evaluation Metrics
# ============================================================

@dataclass
class RetrievalMetrics:
    """Metrics for a single query evaluation."""
    query: str
    retrieved_articles: list[str]
    expected_articles: list[str]
    hit_at_k: dict[int, bool]  # k -> whether any expected article was in top-k
    recall_at_k: dict[int, float]  # k -> recall@k
    precision_at_k: dict[int, float]  # k -> precision@k
    mrr: float  # Mean Reciprocal Rank

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "retrieved_articles": self.retrieved_articles,
            "expected_articles": self.expected_articles,
            "hit_at_k": self.hit_at_k,
            "recall_at_k": self.recall_at_k,
            "precision_at_k": self.precision_at_k,
            "mrr": self.mrr,
        }


@dataclass
class EvaluationSummary:
    """Aggregate evaluation results."""
    total_queries: int
    avg_recall_at_1: float
    avg_recall_at_3: float
    avg_recall_at_5: float
    avg_precision_at_1: float
    avg_precision_at_3: float
    avg_precision_at_5: float
    avg_mrr: float
    hit_rate_at_1: float
    hit_rate_at_3: float
    hit_rate_at_5: float
    per_query: list[RetrievalMetrics]

    def to_dict(self) -> dict:
        return {
            "total_queries": self.total_queries,
            "avg_recall_at_1": self.avg_recall_at_1,
            "avg_recall_at_3": self.avg_recall_at_3,
            "avg_recall_at_5": self.avg_recall_at_5,
            "avg_precision_at_1": self.avg_precision_at_1,
            "avg_precision_at_3": self.avg_precision_at_3,
            "avg_precision_at_5": self.avg_precision_at_5,
            "avg_mrr": self.avg_mrr,
            "hit_rate_at_1": self.hit_rate_at_1,
            "hit_rate_at_3": self.hit_rate_at_3,
            "hit_rate_at_5": self.hit_rate_at_5,
            "per_query": [m.to_dict() for m in self.per_query],
        }


def compute_metrics(
    retrieved: list[RetrievalResult],
    expected: list[str],
    ks: list[int] = None,
) -> RetrievalMetrics:
    """Compute retrieval metrics for a single query."""
    if ks is None:
        ks = [1, 3, 5, 10]

    retrieved_titles = [r.article_title for r in retrieved]
    expected_set = set(expected)

    hit_at_k = {}
    recall_at_k = {}
    precision_at_k = {}

    for k in ks:
        top_k = retrieved_titles[:k]
        hits = sum(1 for t in top_k if t in expected_set)
        hit_at_k[k] = hits > 0
        recall_at_k[k] = hits / len(expected) if expected else 0.0
        precision_at_k[k] = hits / k if k > 0 else 0.0

    # Mean Reciprocal Rank
    mrr = 0.0
    for i, title in enumerate(retrieved_titles, 1):
        if title in expected_set:
            mrr = 1.0 / i
            break

    return RetrievalMetrics(
        query="",  # Filled by caller
        retrieved_articles=retrieved_titles,
        expected_articles=expected,
        hit_at_k=hit_at_k,
        recall_at_k=recall_at_k,
        precision_at_k=precision_at_k,
        mrr=mrr,
    )


def evaluate_retrieval(
    db: Session,
    queries: list[EvalQuery] = None,
    retrieval_fn=None,
    user_role: str = "Employee",
    top_k: int = 10,
    ks: list[int] = None,
) -> EvaluationSummary:
    """
    Run retrieval evaluation on a set of queries.

    Args:
        db: Database session
        queries: List of evaluation queries (uses EVAL_QUERIES if None)
        retrieval_fn: Retrieval function to test (uses hybrid_search if None)
        user_role: Role for visibility filtering
        top_k: Number of results to retrieve per query
        ks: K values for metrics

    Returns:
        EvaluationSummary with aggregate and per-query metrics
    """
    if queries is None:
        queries = EVAL_QUERIES

    if retrieval_fn is None:
        retrieval_fn = lambda **kwargs: hybrid_search(db=db, **kwargs)

    if ks is None:
        ks = [1, 3, 5, 10]

    per_query_metrics = []

    for eval_query in queries:
        results = retrieval_fn(
            query=eval_query.query,
            top_k=top_k,
            user_role=user_role,
        )

        metrics = compute_metrics(results, eval_query.expected_articles, ks)
        metrics.query = eval_query.query
        per_query_metrics.append(metrics)

    # Aggregate
    total = len(per_query_metrics)

    def avg(metric_name: str, k: int) -> float:
        return sum(getattr(m, metric_name).get(k, 0.0) for m in per_query_metrics) / total

    def hit_rate(k: int) -> float:
        return sum(1 for m in per_query_metrics if m.hit_at_k.get(k, False)) / total

    return EvaluationSummary(
        total_queries=total,
        avg_recall_at_1=avg("recall_at_k", 1),
        avg_recall_at_3=avg("recall_at_k", 3),
        avg_recall_at_5=avg("recall_at_k", 5),
        avg_precision_at_1=avg("precision_at_k", 1),
        avg_precision_at_3=avg("precision_at_k", 3),
        avg_precision_at_5=avg("precision_at_k", 5),
        avg_mrr=sum(m.mrr for m in per_query_metrics) / total,
        hit_rate_at_1=hit_rate(1),
        hit_rate_at_3=hit_rate(3),
        hit_rate_at_5=hit_rate(5),
        per_query=per_query_metrics,
    )


def create_test_articles(db: Session, admin_user_id: int) -> list[KnowledgeArticle]:
    """
    Create the test articles used by the evaluation dataset.

    This should be called in test setup to populate the knowledge base
    with articles matching the expected titles in EVAL_QUERIES.

    Returns:
        List of created articles
    """
    test_articles_data = [
        {
            "title": "How to Reset Your Password",
            "summary": "Step-by-step guide to reset your account password",
            "content": "To reset your password, go to the login page and click 'Forgot Password'. Enter your email address and follow the link sent to your inbox. Create a new password meeting the requirements: at least 12 characters, uppercase, lowercase, number, and special character.",
            "category": ArticleCategory.ACCOUNT,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Password Policy and Requirements",
            "summary": "Corporate password policy and complexity requirements",
            "content": "All passwords must be at least 12 characters long and contain uppercase letters, lowercase letters, numbers, and special characters. Passwords expire every 90 days. You cannot reuse your last 5 passwords. Account locks after 5 failed attempts.",
            "category": ArticleCategory.ACCOUNT,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Account Lockout Troubleshooting",
            "summary": "What to do when your account gets locked",
            "content": "If your account is locked after 5 failed login attempts, wait 30 minutes for automatic unlock or contact IT support. You can also use the self-service unlock portal at unlock.company.com with your employee ID and registered phone number.",
            "category": ArticleCategory.ACCOUNT,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Troubleshooting WiFi Connection Issues",
            "summary": "Common WiFi problems and solutions",
            "content": "If your laptop won't connect to WiFi, first toggle WiFi off and on. Check if other devices can connect. Forget the network and reconnect. Update wireless drivers. Check if you're in range of an access point. Contact IT if the issue persists.",
            "category": ArticleCategory.NETWORK,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Laptop Network Configuration Guide",
            "summary": "Configuring network settings on company laptops",
            "content": "Company laptops use DHCP by default. For static IP configuration, go to Network Settings > Ethernet/WiFi > Properties > IPv4. Use the IP range 10.0.x.x with subnet 255.255.255.0. Gateway is 10.0.0.1. DNS servers: 10.0.0.10, 10.0.0.11.",
            "category": ArticleCategory.NETWORK,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Corporate WiFi Setup Instructions",
            "summary": "How to connect to the corporate wireless network",
            "content": "Select 'Corporate-WiFi' from available networks. Enter your domain credentials (username@company.com and password). Accept the certificate if prompted. For personal devices, use the guest network 'Corporate-Guest' with daily rotating password posted in break rooms.",
            "category": ArticleCategory.NETWORK,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "VPN Connection Troubleshooting Guide",
            "summary": "Fix common VPN connection problems",
            "content": "If VPN won't connect, check your internet connection first. Verify VPN client is updated. Try different VPN server locations. Check if split tunneling is enabled. Common errors: 800 (authentication), 619 (port blocked), 720 (protocol mismatch). Contact IT for certificate issues.",
            "category": ArticleCategory.NETWORK,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Remote Access VPN Setup",
            "summary": "Setting up VPN for remote work",
            "content": "Download the VPN client from the IT portal. Install with default settings. Launch and enter your domain credentials. Select 'Corporate-Full' tunnel for full access or 'Corporate-Split' for only internal resources. Save credentials for auto-connect.",
            "category": ArticleCategory.NETWORK,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Common VPN Error Codes and Solutions",
            "summary": "Reference for VPN error codes",
            "content": "Error 800: Authentication failed - check credentials. Error 619: Port blocked - check firewall. Error 720: Protocol mismatch - reinstall VPN client. Error 809: Server unreachable - check internet. Error 13801: Certificate error - reimport certificate.",
            "category": ArticleCategory.NETWORK,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Printer Troubleshooting Steps",
            "summary": "Diagnose and fix common printer issues",
            "content": "If printer isn't working: 1) Check power and cables. 2) Verify printer is online (not paused/offline). 3) Clear print queue: Services > Print Spooler > Restart. 4) Reinstall driver from IT portal. 5) For network printers, verify IP address. 6) Print test page from printer menu.",
            "category": ArticleCategory.HARDWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Network Printer Configuration",
            "summary": "Adding network printers to your computer",
            "content": "To add a network printer: Settings > Devices > Printers > Add Printer. Select 'The printer I want isn't listed'. Enter printer IP or hostname. Select driver from list or download from manufacturer. Print test page to verify.",
            "category": ArticleCategory.HARDWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Print Queue Management",
            "summary": "Managing stuck print jobs",
            "content": "If documents are stuck in queue: Open Print Queue from taskbar. Right-click stuck job > Cancel. If it won't cancel, restart Print Spooler service (services.msc > Print Spooler > Restart). Then try printing again.",
            "category": ArticleCategory.HARDWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "How to Unlock Your Account",
            "summary": "Self-service account unlock procedure",
            "content": "Visit unlock.company.com. Enter employee ID and answer security questions. Or use the registered phone number for SMS code. Account unlocks immediately. If self-service fails, contact IT helpdesk with your employee ID and government ID for verification.",
            "category": ArticleCategory.ACCOUNT,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Software Installation Request Process",
            "summary": "How to request new software installation",
            "content": "Submit a software request ticket in the IT portal. Include software name, version, business justification, and license information. IT reviews for security, compatibility, and licensing. Approved software is deployed via SCCM/Intune within 2 business days.",
            "category": ArticleCategory.SOFTWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Approved Software Catalog",
            "summary": "List of pre-approved software for self-installation",
            "content": "Pre-approved software available in Self-Service Portal: Office 365, Teams, Chrome, Firefox, 7-Zip, Notepad++, VLC, Adobe Reader, Zoom, Slack, VS Code, Python, Git, Docker Desktop. No ticket needed for these.",
            "category": ArticleCategory.SOFTWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Self-Service Software Portal Guide",
            "summary": "Using the self-service software portal",
            "content": "Open Software Center (Windows) or Self Service (Mac). Browse or search for applications. Click Install. Monitor progress in the portal. Some apps require reboot. Contact IT if installation fails with error code.",
            "category": ArticleCategory.SOFTWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Network Connectivity Troubleshooting",
            "summary": "Diagnose general network issues",
            "content": "If you have network issues: 1) Check if other sites work. 2) Try wired connection. 3) Run 'ipconfig /flushdns' and 'ipconfig /renew'. 4) Ping 8.8.8.8 to test internet. 5) Ping gateway 10.0.0.1. 6) Check VPN status. 7) Contact IT with traceroute output.",
            "category": ArticleCategory.NETWORK,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "DNS Resolution Problems",
            "summary": "Fix DNS-related connectivity issues",
            "content": "If websites don't load but ping works: 1) Flush DNS: ipconfig /flushdns. 2) Change DNS to 8.8.8.8 / 8.8.4.4 temporarily. 3) Check hosts file (C:\\Windows\\System32\\drivers\\etc\\hosts). 4) Restart DNS Client service. 5) Contact IT if internal domains fail.",
            "category": ArticleCategory.NETWORK,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Network Outage Reporting Procedure",
            "summary": "How to report network outages",
            "content": "If you suspect a network outage: 1) Check with colleagues. 2) Try different network jack or WiFi. 3) Report via IT portal or call helpdesk. Provide: location, affected devices, start time, error messages. IT will investigate and post updates on status page.",
            "category": ArticleCategory.NETWORK,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Email Sync Troubleshooting",
            "summary": "Fix email synchronization issues",
            "content": "If email isn't syncing: 1) Check internet connection. 2) Restart Outlook. 3) Check Send/Receive settings. 4) Verify mailbox isn't full (quota). 5) Recreate Outlook profile. 6) For mobile, remove and re-add account. 7) Check if OWA works at mail.company.com.",
            "category": ArticleCategory.SOFTWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Outlook Configuration Guide",
            "summary": "Setting up Outlook with corporate email",
            "content": "Outlook auto-configures with domain credentials. For manual setup: File > Add Account > Enter email. Server: outlook.office365.com. Port 993 (IMAP) / 587 (SMTP) with TLS. Use domain credentials. Enable Cached Exchange Mode for offline access.",
            "category": ArticleCategory.SOFTWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Mobile Email Setup Instructions",
            "summary": "Configure corporate email on mobile devices",
            "content": "iOS: Settings > Mail > Accounts > Add Account > Microsoft Exchange. Enter email and password. Android: Gmail app > Add Account > Exchange. Enter email, password, domain\\username. Server: outlook.office365.com. Enable sync for Mail, Contacts, Calendar.",
            "category": ArticleCategory.SOFTWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "BSOD Troubleshooting Guide",
            "summary": "Diagnose Windows blue screen errors",
            "content": "When BSOD occurs: 1) Note the stop code (e.g., CRITICAL_PROCESS_DIED). 2) Check Event Viewer > System for BugCheck events. 3) Analyze memory dump: %SystemRoot%\\MEMORY.DMP. 4) Run Windows Memory Diagnostic. 5) Update drivers. 6) Check for recent hardware/software changes.",
            "category": ArticleCategory.HARDWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Windows Crash Dump Analysis",
            "summary": "Analyzing crash dump files",
            "content": "Install Windows Debugger (WinDbG). Open dump file. Run !analyze -v. Look for MODULE_NAME, IMAGE_NAME, BUCKET_ID. Common causes: ntoskrnl.exe (kernel), nvlddmkm.sys (NVIDIA), usbport.sys (USB). Search bucket ID for known issues.",
            "category": ArticleCategory.HARDWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Hardware Diagnostic Procedures",
            "summary": "Running hardware diagnostics",
            "content": "Built-in diagnostics: Dell (F12 at boot), HP (F2), Lenovo (F10). Test: Memory, CPU, Disk, Fans, Battery. Third-party: MemTest86 (RAM), CrystalDiskInfo (SSD/HDD), FurMark (GPU). Document results for IT support ticket.",
            "category": ArticleCategory.HARDWARE,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Identifying Phishing Emails",
            "summary": "How to spot phishing attempts",
            "content": "Red flags: Urgent action required, sender address doesn't match domain, poor grammar/spelling, generic greetings, suspicious links (hover to check), unexpected attachments. Legitimate IT emails never ask for passwords. Report suspicious emails to security@company.com.",
            "category": ArticleCategory.SECURITY,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Reporting Suspicious Emails",
            "summary": "How to report phishing and spam",
            "content": "Forward suspicious emails to security@company.com. Use the 'Report Phishing' button in Outlook if available. Delete the email. Don't click links or open attachments. IT will analyze and block sender if malicious. You won't be penalized for reporting.",
            "category": ArticleCategory.SECURITY,
            "status": ArticleStatus.PUBLISHED,
        },
        {
            "title": "Security Awareness Training",
            "summary": "Annual security training requirements",
            "content": "All employees must complete annual security training by Q4. Topics: Phishing, password security, data classification, incident reporting, remote work security. Access via Learning Portal. Completion tracked in HR system. Non-compliance may restrict system access.",
            "category": ArticleCategory.SECURITY,
            "status": ArticleStatus.PUBLISHED,
        },
    ]

    articles = []
    for data in test_articles_data:
        # Generate unique slug
        base_slug = slugify(data["title"])
        if not base_slug:
            base_slug = "article"
        slug = base_slug
        counter = 1
        while True:
            existing = db.query(KnowledgeArticle).filter(KnowledgeArticle.slug == slug).first()
            if not existing:
                break
            counter += 1
            slug = f"{base_slug}-{counter}"

        article = KnowledgeArticle(
            title=data["title"],
            slug=slug,
            summary=data["summary"],
            content=data["content"],
            category=data["category"],
            status=data["status"],
            author_id=admin_user_id,
        )
        db.add(article)
        articles.append(article)

    db.commit()
    for article in articles:
        db.refresh(article)

    return articles