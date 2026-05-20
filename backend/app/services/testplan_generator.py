import re
from collections import Counter
from datetime import datetime, timezone
from uuid import uuid4


STOP_WORDS = {
    "shall",
    "should",
    "must",
    "will",
    "with",
    "from",
    "that",
    "this",
    "into",
    "when",
    "where",
    "user",
    "system",
    "application",
    "requirement",
    "requirements",
}


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [part.strip(" -\t") for part in parts if len(part.strip()) > 18]


def _keywords(text: str, limit: int = 8) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())
    counts = Counter(word for word in words if word not in STOP_WORDS)
    return [word.replace("_", " ").title() for word, _ in counts.most_common(limit)]


def _matching_lines(sentences: list[str], terms: tuple[str, ...], fallback: list[str]) -> list[str]:
    matched = [
        sentence[:180]
        for sentence in sentences
        if any(term in sentence.lower() for term in terms)
    ]
    return matched[:5] or fallback


def generate_plan(document_text: str, source_files: list[str]) -> dict:
    sentences = _sentences(document_text)
    keywords = _keywords(document_text)
    primary_features = keywords[:5] or [
        "Authentication",
        "Document Upload",
        "AI Test Plan Generation",
        "Export Workflow",
    ]

    functional = _matching_lines(
        sentences,
        ("shall", "must", "create", "update", "delete", "submit", "upload", "generate"),
        [
            "Validate all documented user journeys using positive and negative test data.",
            "Verify field validation, workflow transitions, and backend response handling.",
            "Confirm generated test plan sections map back to source requirements.",
        ],
    )

    api = _matching_lines(
        sentences,
        ("api", "endpoint", "request", "response", "integration", "service"),
        [
            "Validate request and response contracts for login, upload, generation, and export endpoints.",
            "Check authentication headers, validation errors, and service unavailable responses.",
        ],
    )

    security = _matching_lines(
        sentences,
        ("security", "auth", "token", "password", "permission", "role", "access"),
        [
            "Verify protected routes and APIs reject unauthenticated requests.",
            "Validate role-based access, token expiration, and secure logout behavior.",
            "Confirm uploaded files are validated before processing.",
        ],
    )

    test_cases = [
        {
            "id": "TC-001",
            "title": "Upload supported SRS document",
            "priority": "High",
            "expected": "PDF, DOCX, or TXT files are stored and returned with a file identifier.",
        },
        {
            "id": "TC-002",
            "title": "Generate structured test plan",
            "priority": "High",
            "expected": "All required test plan sections are generated from uploaded requirements.",
        },
        {
            "id": "TC-003",
            "title": "Preview generated test plan",
            "priority": "Medium",
            "expected": "Generated sections render in the document preview without missing content.",
        },
        {
            "id": "TC-004",
            "title": "Export generated test plan",
            "priority": "Medium",
            "expected": "PDF and DOCX downloads contain the current generated test plan.",
        },
    ]

    return {
        "id": str(uuid4()),
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "sourceFiles": source_files,
        "sections": {
            "scope": (
                "Validate the software behavior described in the uploaded SRS documents: "
                f"{', '.join(source_files)}. The plan covers functional, integration, "
                "security, usability, regression, and export readiness checks."
            ),
            "objectives": [
                "Convert source requirements into executable QA coverage.",
                "Identify high-risk areas and validation priorities.",
                "Provide a review-ready test plan for QA sign-off.",
            ],
            "featuresToTest": primary_features,
            "featuresNotToTest": [
                "Third-party services outside the application boundary unless explicitly documented.",
                "Unsupported file formats and infrastructure managed by external teams.",
            ],
            "testStrategy": (
                "Apply risk-based testing with requirement review, scenario design, API validation, "
                "UI verification, security checks, non-functional checks, and regression confirmation."
            ),
            "functionalTesting": functional,
            "nonFunctionalTesting": [
                "Measure response time for upload, parsing, generation, and export workflows.",
                "Validate resilience when large documents or slow AI responses are encountered.",
                "Confirm responsive behavior across desktop, tablet, and mobile breakpoints.",
            ],
            "securityTesting": security,
            "apiTesting": api,
            "uiTesting": [
                "Validate drag-and-drop upload, progress display, and error states.",
                "Confirm generated cards are readable and complete for every required section.",
                "Check profile menu, settings controls, and logout behavior.",
            ],
            "regressionTesting": [
                "Run smoke coverage for login, upload, generation, export, and history flows.",
                "Re-run previous SRS samples after parser, model, or prompt changes.",
                "Confirm new changes do not break JWT-protected navigation.",
            ],
            "risks": [
                "Ambiguous SRS language may produce incomplete test coverage.",
                "Scanned PDFs without OCR may not expose readable text.",
                "Large files may require backend chunking and longer AI processing windows.",
            ],
            "deliverables": [
                "Master test plan",
                "Prioritized test scenarios",
                "Exported PDF and DOCX reports",
                "Review notes for missing or ambiguous requirements",
            ],
            "testCases": test_cases,
           # "Summary": [
            #    f"Test Plan Summary: Total {len(test_cases)} test cases defined for comprehensive coverage.",
            #   f"Risk Profile: {len([r for r in primary_features])} primary features identified with {len([r for r in source_files])} source documents analyzed.",
            #    f"Critical Risks (3): Ambiguous requirements, OCR limitations, and large file processing delays require priority attention.",
            #    "Priority Execution: Execute High-priority test cases first (TC-001, TC-002, TC-003) to validate core workflows.",
             #   "Focus areas include functional workflows, security controls, API contracts, and UI responsiveness.",
              #  "Execution should follow the prioritized test case sequence with risk-based testing approach.",
            #],
        },
    }
