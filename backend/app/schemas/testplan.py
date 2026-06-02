from typing import Any

from pydantic import BaseModel, Field


class UploadedFileReference(BaseModel):
    fileId: str | None = None
    fileName: str | None = None
    name: str | None = None


class GenerateTestPlanRequest(BaseModel):
    files: list[UploadedFileReference] = Field(default_factory=list)


class TestCase(BaseModel):
    id: str
    requirementIds: list[str] = Field(default_factory=list)
    category: str | None = None
    testType: str | None = None
    title: str
    priority: str
    preconditions: list[str] = Field(default_factory=list)
    testData: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    expected: str


class TestPlanSections(BaseModel):
    scope: str
    objectives: list[str]
    featuresToTest: list[str]
    featuresNotToTest: list[str]
    testStrategy: str
    functionalTesting: list[str]
    nonFunctionalTesting: list[str]
    securityTesting: list[str]
    apiTesting: list[str]
    uiTesting: list[str]
    regressionTesting: list[str]
    requirementsTraceability: list[str] = Field(default_factory=list)
    testEnvironment: list[str] = Field(default_factory=list)
    entryCriteria: list[str] = Field(default_factory=list)
    exitCriteria: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    risks: list[str]
    deliverables: list[str]
    testCases: list[TestCase]


class GenerateTestPlanResponse(BaseModel):
    id: str
    createdAt: str
    sourceFiles: list[str]
    sections: TestPlanSections
    confidence_score: int
    confidence_level: str
    reason: str


class ExportPayload(BaseModel):
    root: dict[str, Any]

    model_config = {"arbitrary_types_allowed": True}
# 
