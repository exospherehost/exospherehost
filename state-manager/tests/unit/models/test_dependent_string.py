import pytest

# Attempt multiple import paths to accommodate common layouts
try:
    # e.g., src/state_manager/models/dependent_string.py
    from state_manager.models.dependent_string import DependentString, Dependent
except Exception:
    try:
        # e.g., state_manager/dependent_string.py
        from state_manager.dependent_string import DependentString, Dependent
    except Exception:
        try:
            # e.g., state-manager/state_manager/models/dependent_string.py accessible as package
            from models.dependent_string import DependentString, Dependent
        except Exception:
            # Fallback: relative import if tests live alongside source
            from dependent_string import DependentString, Dependent  # type: ignore


class TestCreateDependentString:
    def test_no_placeholders_returns_head_only_and_empty_dependents(self):
        s = "plain string without placeholders"
        ds = DependentString.create_dependent_string(s)
        assert isinstance(ds, DependentString)
        assert ds.head == s
        assert ds.dependents == {}
        # get_identifier_field should be empty for no dependents
        assert ds.get_identifier_field() == []

    def test_single_placeholder_happy_path(self):
        template = "Hello ${{ step.outputs.foo }} world"
        ds = DependentString.create_dependent_string(template)
        # Head is the prefix before the first placeholder
        assert ds.head == "Hello "
        # One dependent keyed by order 0
        assert list(ds.dependents.keys()) == [0]
        dep = ds.dependents[0]
        assert isinstance(dep, Dependent)
        assert dep.identifier == "step"
        assert dep.field == "foo"
        assert dep.tail == " world"
        # Not set yet -> generate_string should raise
        with pytest.raises(ValueError) as exc:
            ds.generate_string()
        assert "Dependent value is not set" in str(exc.value)
        # After setting, generation should succeed
        ds.set_value("step", "foo", "BAR")
        assert ds.generate_string() == "Hello BAR world"

    def test_placeholder_at_end_results_in_empty_tail(self):
        template = "Hi ${{ a.outputs.x }}"
        ds = DependentString.create_dependent_string(template)
        assert ds.dependents[0].tail == ""
        ds.set_value("a", "x", "V")
        assert ds.generate_string() == "Hi V"

    def test_multiple_placeholders_in_order(self):
        template = "Start ${{ a.outputs.x }} mid ${{ b.outputs.y }} end"
        ds = DependentString.create_dependent_string(template)
        # Keys should reflect insertion order (0, 1) when sorted
        assert sorted(ds.dependents.keys()) == [0, 1]
        assert ds.dependents[0].identifier == "a"
        assert ds.dependents[0].field == "x"
        assert ds.dependents[0].tail == " mid "
        assert ds.dependents[1].identifier == "b"
        assert ds.dependents[1].field == "y"
        assert ds.dependents[1].tail == " end"
        ds.set_value("a", "x", "AX")
        ds.set_value("b", "y", "BY")
        assert ds.generate_string() == "Start AX mid BY end"

    def test_unclosed_placeholder_raises_value_error(self):
        template = "Start ${{ a.outputs.x end"
        with pytest.raises(ValueError) as exc:
            DependentString.create_dependent_string(template)
        msg = str(exc.value)
        assert "Invalid syntax string placeholder" in msg
        assert "'${{'" in msg or "not closed" in msg

    def test_invalid_placeholder_wrong_parts_count_raises(self):
        # Missing the third part after outputs
        template = "Start ${{ a.outputs }} end"
        with pytest.raises(ValueError) as exc:
            DependentString.create_dependent_string(template)
        assert "Invalid syntax string placeholder" in str(exc.value)

    def test_invalid_placeholder_wrong_keyword_raises(self):
        template = "Start ${{ a.outputz.x }} end"
        with pytest.raises(ValueError) as exc:
            DependentString.create_dependent_string(template)
        assert "Invalid syntax string placeholder" in str(exc.value)

    def test_placeholder_with_extra_whitespace_is_parsed(self):
        template = "P ${{  step  .  outputs  .  foo  }} T"
        ds = DependentString.create_dependent_string(template)
        assert ds.dependents[0].identifier == "step"
        assert ds.dependents[0].field == "foo"
        ds.set_value("step", "foo", "VAL")
        assert ds.generate_string() == "P VAL T"


class TestMappingAndSetValue:
    def test_get_identifier_field_returns_unique_keys(self):
        template = "A ${{ a.outputs.x }} B ${{ a.outputs.x }} C ${{ b.outputs.y }}"
        ds = DependentString.create_dependent_string(template)
        # Should return two unique keys: ('a','x') and ('b','y'), order not guaranteed
        keys = ds.get_identifier_field()
        assert set(keys) == {("a", "x"), ("b", "y")}

    def test_set_value_updates_all_matching_dependents(self):
        template = "A ${{ a.outputs.x }} B ${{ a.outputs.x }}"
        ds = DependentString.create_dependent_string(template)
        ds.set_value("a", "x", "V")
        # Both dependents should get the same value and render twice
        assert ds.generate_string() == "A V B V"

    def test_set_value_with_unknown_mapping_raises_keyerror(self):
        template = "A ${{ a.outputs.x }}"
        ds = DependentString.create_dependent_string(template)
        with pytest.raises(KeyError):
            ds.set_value("unknown", "field", "V")

    def test_build_mapping_is_idempotent_and_cached(self):
        template = "A ${{ a.outputs.x }} B ${{ b.outputs.y }}"
        ds = DependentString.create_dependent_string(template)
        # First call builds mapping
        keys1 = set(ds.get_identifier_field())
        # Second call should not change
        keys2 = set(ds.get_identifier_field())
        assert keys1 == keys2 == {("a", "x"), ("b", "y")}
