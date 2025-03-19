from dash.resources import Resources, ResourceConfig


def test_resources_eager():
    resource = Resources("js_test", ResourceConfig(False, True))

    filtered = resource._filter_resources(
        [
            {"async": "eager", "external_url": "a.js"},
            {"async": "lazy", "external_url": "b.js"},
            {"async": True, "external_url": "c.js"},
        ],
        False,
    )

    assert len(filtered) == 3
    assert filtered[0].get("external_url") == "a.js"
    assert filtered[0].get("dynamic") is False  # include (eager when eager)
    assert filtered[1].get("external_url") == "b.js"
    assert (
        filtered[1].get("dynamic") is True
    )  # exclude (lazy when eager -> closest to exclude)
    assert filtered[2].get("external_url") == "c.js"
    assert filtered[2].get("dynamic") is False  # include (always matches settings)


def test_resources_lazy():
    resource = Resources("js_test", ResourceConfig(False, False))

    filtered = resource._filter_resources(
        [
            {"async": "eager", "external_url": "a.js"},
            {"async": "lazy", "external_url": "b.js"},
            {"async": True, "external_url": "c.js"},
        ],
        False,
    )

    assert len(filtered) == 3
    assert filtered[0].get("external_url") == "a.js"
    assert filtered[0].get("dynamic") is True  # exclude (no eager when lazy)
    assert filtered[1].get("external_url") == "b.js"
    assert filtered[1].get("dynamic") is True  # exclude (lazy when lazy)
    assert filtered[2].get("external_url") == "c.js"
    assert filtered[2].get("dynamic") is True  # exclude (always matches settings)
