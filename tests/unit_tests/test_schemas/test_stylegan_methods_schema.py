from app.schemas.stylegan_methods import StyleGanMethod


def test_styleganmethod():
    """Unit test the __call__ method of the StyleGanMethod class."""
    new_method = StyleGanMethod(
        "method_name", "method_description", ("method_option1", "method_option2")
    )

    assert new_method() == {
        "name": "method_name",
        "description": "method_description",
        "method_options": ("method_option1", "method_option2"),
    }
