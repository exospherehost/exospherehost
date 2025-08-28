# Notes

- Tests authored with pytest, matching repository conventions discovered via search.
- Models use Pydantic v2 (field_validator), so assertions expect pydantic.ValidationError wrapping ValueError messages from validators.
- No new dependencies introduced.