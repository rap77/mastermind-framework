"""End-to-end pipeline for selecting and validating multi-harness bundles."""

from __future__ import annotations

from dataclasses import dataclass

from .file_system_catalog import FileSystemHarnessCatalog
from .models import MultiHarnessPipelineResult, ObjectiveProfile
from .multi_harness_selector import MultiHarnessSelector
from .run_bundle_composer import RunBundleComposer
from .run_bundle_validator import RunBundleValidator


@dataclass(frozen=True, slots=True)
class MultiHarnessPipeline:
    """Build a validated RunBundle from an objective profile."""

    catalog: FileSystemHarnessCatalog
    composer: RunBundleComposer
    validator: RunBundleValidator = RunBundleValidator()

    def build(self, profile: ObjectiveProfile) -> MultiHarnessPipelineResult:
        """Select, compose, and validate a run bundle for the profile."""
        plan = MultiHarnessSelector(self.catalog).select(profile)
        bundle = self.composer.compose(plan)
        validated_bundle = self.validator.validate(bundle)
        return MultiHarnessPipelineResult(plan=plan, bundle=validated_bundle)
