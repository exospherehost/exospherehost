"""
Integration tests for trigger deduplication logic in create_crons.
These tests verify that duplicate triggers with identical expression and timezone
result in only one DatabaseTriggers row being created.
"""
import pytest

from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.node_template_model import NodeTemplate
from app.models.trigger_models import Trigger, TriggerTypeEnum
from app.models.db.trigger import DatabaseTriggers
from app.tasks.verify_graph import create_crons


@pytest.mark.asyncio(loop_scope="session")
async def test_create_crons_deduplicates_identical_triggers(app_started):
    """Test that create_crons deduplicates triggers with identical expression and timezone

    This integration test verifies the actual database behavior, not mocks.
    It creates a GraphTemplate with duplicate CRON triggers and verifies that only
    one DatabaseTriggers row exists per (expression, timezone) pair.
    """
    # Clean up any existing triggers for this test
    await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_dedup_graph",
        DatabaseTriggers.namespace == "test_namespace"
    ).delete_many()

    # Create a graph template with duplicate triggers
    graph_template = GraphTemplate(
        name="test_dedup_graph",
        namespace="test_namespace",
        nodes=[
            NodeTemplate(
                node_name="test_node",
                namespace="test_namespace",
                identifier="test_node",
                inputs={},
                next_nodes=None,
                unites=None
            )
        ],
        validation_status=GraphTemplateValidationStatus.PENDING,
        triggers=[
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 9 * * *", "timezone": "America/New_York"}),
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 9 * * *", "timezone": "America/New_York"}),
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 9 * * *", "timezone": "America/New_York"}),
        ]
    )

    # Call create_crons
    await create_crons(graph_template)

    # Query the database to verify only one trigger was created
    triggers = await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_dedup_graph",
        DatabaseTriggers.namespace == "test_namespace",
        DatabaseTriggers.expression == "0 9 * * *",
        DatabaseTriggers.timezone == "America/New_York"
    ).to_list()

    # Assert only one trigger exists (deduplication worked)
    assert len(triggers) == 1
    assert triggers[0].expression == "0 9 * * *"
    assert triggers[0].timezone == "America/New_York"

    # Clean up
    await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_dedup_graph",
        DatabaseTriggers.namespace == "test_namespace"
    ).delete_many()


@pytest.mark.asyncio(loop_scope="session")
async def test_create_crons_keeps_triggers_with_different_timezones(app_started):
    """Test that create_crons keeps triggers with same expression but different timezones

    This verifies that triggers are only deduplicated when BOTH expression AND timezone match.
    """
    # Clean up any existing triggers for this test
    await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_timezone_graph",
        DatabaseTriggers.namespace == "test_namespace"
    ).delete_many()

    # Create a graph template with same expression, different timezones
    graph_template = GraphTemplate(
        name="test_timezone_graph",
        namespace="test_namespace",
        nodes=[
            NodeTemplate(
                node_name="test_node",
                namespace="test_namespace",
                identifier="test_node",
                inputs={},
                next_nodes=None,
                unites=None
            )
        ],
        validation_status=GraphTemplateValidationStatus.PENDING,
        triggers=[
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 9 * * *", "timezone": "America/New_York"}),
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 9 * * *", "timezone": "Europe/London"}),
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 9 * * *", "timezone": "Asia/Tokyo"}),
        ]
    )

    # Call create_crons
    await create_crons(graph_template)

    # Query the database to verify all three triggers were created (different timezones)
    triggers = await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_timezone_graph",
        DatabaseTriggers.namespace == "test_namespace",
        DatabaseTriggers.expression == "0 9 * * *"
    ).to_list()

    # Assert three triggers exist (one for each timezone)
    assert len(triggers) == 3

    timezones = {t.timezone for t in triggers}
    assert timezones == {"America/New_York", "Europe/London", "Asia/Tokyo"}

    # Clean up
    await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_timezone_graph",
        DatabaseTriggers.namespace == "test_namespace"
    ).delete_many()


@pytest.mark.asyncio(loop_scope="session")
async def test_create_crons_keeps_triggers_with_different_expressions(app_started):
    """Test that create_crons keeps triggers with different expressions

    This verifies basic functionality - triggers with different expressions should all be created.
    """
    # Clean up any existing triggers for this test
    await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_expr_graph",
        DatabaseTriggers.namespace == "test_namespace"
    ).delete_many()

    # Create a graph template with different expressions
    graph_template = GraphTemplate(
        name="test_expr_graph",
        namespace="test_namespace",
        nodes=[
            NodeTemplate(
                node_name="test_node",
                namespace="test_namespace",
                identifier="test_node",
                inputs={},
                next_nodes=None,
                unites=None
            )
        ],
        validation_status=GraphTemplateValidationStatus.PENDING,
        triggers=[
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 9 * * *", "timezone": "UTC"}),
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 12 * * *", "timezone": "UTC"}),
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "*/15 * * * *", "timezone": "UTC"}),
        ]
    )

    # Call create_crons
    await create_crons(graph_template)

    # Query the database to verify all three triggers were created
    triggers = await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_expr_graph",
        DatabaseTriggers.namespace == "test_namespace"
    ).to_list()

    # Assert three triggers exist (all different expressions)
    assert len(triggers) == 3

    expressions = {t.expression for t in triggers}
    assert expressions == {"0 9 * * *", "0 12 * * *", "*/15 * * * *"}

    # Clean up
    await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_expr_graph",
        DatabaseTriggers.namespace == "test_namespace"
    ).delete_many()


@pytest.mark.asyncio(loop_scope="session")
async def test_create_crons_complex_deduplication_scenario(app_started):
    """Test complex deduplication scenario with mix of duplicates and unique triggers

    This tests a realistic scenario where a graph template has:
    - Some duplicate triggers (same expression + timezone)
    - Some unique triggers
    - Triggers with same expression but different timezone
    """
    # Clean up any existing triggers for this test
    await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_complex_graph",
        DatabaseTriggers.namespace == "test_namespace"
    ).delete_many()

    # Create a graph template with a complex mix of triggers
    graph_template = GraphTemplate(
        name="test_complex_graph",
        namespace="test_namespace",
        nodes=[
            NodeTemplate(
                node_name="test_node",
                namespace="test_namespace",
                identifier="test_node",
                inputs={},
                next_nodes=None,
                unites=None
            )
        ],
        validation_status=GraphTemplateValidationStatus.PENDING,
        triggers=[
            # Three duplicates - should result in 1 DB row
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 9 * * *", "timezone": "America/New_York"}),
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 9 * * *", "timezone": "America/New_York"}),
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 9 * * *", "timezone": "America/New_York"}),

            # Same expression, different timezone - should result in 1 DB row
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 9 * * *", "timezone": "Europe/London"}),

            # Two duplicates of a different expression - should result in 1 DB row
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "*/15 * * * *", "timezone": "UTC"}),
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "*/15 * * * *", "timezone": "UTC"}),

            # Unique trigger - should result in 1 DB row
            Trigger(value={"type": TriggerTypeEnum.CRON, "expression": "0 0 1 * *", "timezone": "Asia/Tokyo"}),
        ]
    )

    # Call create_crons
    await create_crons(graph_template)

    # Query the database to verify correct number of triggers
    triggers = await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_complex_graph",
        DatabaseTriggers.namespace == "test_namespace"
    ).to_list()

    # Expected: 4 unique (expression, timezone) pairs
    # 1. (0 9 * * *, America/New_York)
    # 2. (0 9 * * *, Europe/London)
    # 3. (*/15 * * * *, UTC)
    # 4. (0 0 1 * *, Asia/Tokyo)
    assert len(triggers) == 4

    # Verify each unique pair exists
    trigger_pairs = {(t.expression, t.timezone) for t in triggers}
    assert trigger_pairs == {
        ("0 9 * * *", "America/New_York"),
        ("0 9 * * *", "Europe/London"),
        ("*/15 * * * *", "UTC"),
        ("0 0 1 * *", "Asia/Tokyo"),
    }

    # Clean up
    await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == "test_complex_graph",
        DatabaseTriggers.namespace == "test_namespace"
    ).delete_many()