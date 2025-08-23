from exospherehost._version import version


def test_version_import():
    """Test that version can be imported and is a string."""
    assert isinstance(version, str)
    assert len(version) > 0


def test_version_format():
    """Test that version follows a reasonable format."""
    # Version should be a string that could be a semantic version
    assert version is not None
    # Should not be empty
    assert version.strip() != ""
    # Should not contain only whitespace
    assert not version.isspace()


def test_version_consistency():
    """Test that version is consistent across imports."""
    from exospherehost._version import version as version1
    from exospherehost._version import version as version2
    
    assert version1 == version2
    assert version1 is version2


def test_version_in_package_init():
    """Test that version is properly exposed in package __init__."""
    from exospherehost import VERSION
    
    assert VERSION == version
    assert isinstance(VERSION, str) 