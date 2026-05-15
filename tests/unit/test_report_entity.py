from datetime import datetime
from src.domain.entities.report import Report, ReportComponent, ReportRisk, ReportRecommendation


def test_report_create():
    report = Report.create(
        upload_id="upload-id-1",
        summary="Microservices architecture",
        components=[ReportComponent("API GW", "Gateway", "Entry point", "Kong")],
        risks=[ReportRisk("SPOF", "HIGH", "Single point of failure", "Downtime")],
        recommendations=[ReportRecommendation("Add HA", "HIGH", "Deploy multiple", "Availability")],
        ai_model="gemini-2.0-flash",
        processing_time_seconds=5.0,
    )
    assert report.upload_id == "upload-id-1"
    assert report.summary == "Microservices architecture"
    assert len(report.components) == 1
    assert len(report.risks) == 1
    assert len(report.recommendations) == 1
    assert report.ai_model == "gemini-2.0-flash"
    assert report.processing_time_seconds == 5.0
    assert report.id is not None
    assert report.created_at is not None


def test_report_create_generates_unique_ids():
    r1 = Report.create("u1", "summary1", [], [], [], "model", 1.0)
    r2 = Report.create("u2", "summary2", [], [], [], "model", 2.0)
    assert r1.id != r2.id


def test_report_component_fields():
    comp = ReportComponent("DB", "Database", "Stores data", "PostgreSQL")
    assert comp.name == "DB"
    assert comp.type == "Database"
    assert comp.description == "Stores data"
    assert comp.technology == "PostgreSQL"


def test_report_risk_defaults():
    risk = ReportRisk("Timeout", "MEDIUM", "Service timeout", "Degraded UX")
    assert risk.affected_components == []
    assert risk.title == "Timeout"
    assert risk.severity == "MEDIUM"


def test_report_risk_with_components():
    risk = ReportRisk("SPOF", "HIGH", "desc", "impact", ["API GW", "DB"])
    assert len(risk.affected_components) == 2
    assert "API GW" in risk.affected_components


def test_report_recommendation_fields():
    rec = ReportRecommendation("Add HA", "HIGH", "Deploy multiple instances", "Better availability")
    assert rec.title == "Add HA"
    assert rec.priority == "HIGH"
    assert rec.description == "Deploy multiple instances"
    assert rec.rationale == "Better availability"


def test_report_create_empty_lists():
    report = Report.create(
        upload_id="upload-empty",
        summary="Simple architecture",
        components=[],
        risks=[],
        recommendations=[],
        ai_model="gemini-2.0-flash",
        processing_time_seconds=1.5,
    )
    assert report.components == []
    assert report.risks == []
    assert report.recommendations == []
