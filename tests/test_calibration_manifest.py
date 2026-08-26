from pathlib import Path

from dbl_farmer.calibration.manifest import missing_templates, template_specs
from dbl_farmer.input.executor import default_action_targets
from dbl_farmer.vision.states import default_state_definitions


def test_manifest_covers_every_state_detection_template():
    paths = {spec.path for spec in template_specs()}
    expected = {
        cue.template_path.removeprefix("assets/templates/")
        for definition in default_state_definitions("assets/templates")
        for cue in definition.cues
    }

    assert expected <= paths


def test_manifest_covers_every_action_template():
    paths = {spec.path for spec in template_specs()}
    expected = {
        template
        for target in default_action_targets().values()
        for template in target.templates
    }

    assert expected <= paths


def test_missing_templates_only_returns_absent_files(tmp_path: Path):
    first = template_specs()[0]
    captured = tmp_path / first.path
    captured.parent.mkdir(parents=True)
    captured.write_bytes(b"x")

    missing = missing_templates(tmp_path)

    assert first.path not in {spec.path for spec in missing}
    assert len(missing) == len(template_specs()) - 1
