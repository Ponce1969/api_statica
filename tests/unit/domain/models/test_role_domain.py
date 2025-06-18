# tests/unit/domain/models/test_role_domain.py
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.models.role import Role


def test_create_role_minimal_data() -> None:
    """Test creating a Role instance with minimal valid data."""
    role_name = "Test Role"
    role = Role(name=role_name)

    assert isinstance(role.id, UUID)
    assert role.name == role_name
    assert role.description is None
    assert isinstance(role.created_at, datetime)
    # Check if created_at is recent (e.g., within the last few seconds)
    assert (datetime.now(UTC) - role.created_at).total_seconds() < 5


def test_create_role_all_fields() -> None:
    """Test creating a Role instance with all fields provided."""
    role_id = uuid4()
    role_name = "Admin Role"
    role_description = "Administrator role with full permissions"
    created_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)

    role = Role(
        entity_id=role_id,
        name=role_name,
        description=role_description,
        created_at=created_time,
    )

    assert role.id == role_id
    assert role.name == role_name
    assert role.description == role_description
    assert role.created_at == created_time


def test_role_created_at_defaults_to_now_utc() -> None:
    """Test that created_at defaults to datetime.now(UTC) if not provided."""
    role = Role(name="Default Time Role")
    assert isinstance(role.created_at, datetime)
    assert role.created_at.tzinfo == UTC
    # Check if created_at is very recent
    assert (datetime.now(UTC) - role.created_at).total_seconds() < 2


def test_update_role_description() -> None:
    """Test updating the description of a Role."""
    role = Role(name="Original Name")
    assert role.description is None

    new_description = "This is an updated description."
    role.update_description(new_description)
    assert role.description == new_description

    empty_description = ""
    role.update_description(empty_description)
    assert role.description == empty_description


def test_role_str_representation() -> None:
    """Test the __str__ method of the Role entity."""
    role_id = uuid4()
    role_name = "Viewer"
    role = Role(name=role_name, entity_id=role_id)
    expected_str = f"Role(id={role_id}, name={role_name})"
    assert str(role) == expected_str
