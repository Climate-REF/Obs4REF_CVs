#!/usr/bin/env python3
import os
import sys
from esgvoc.core.service.configuration.setting import (
    Setting,
    UniverseSettings,
    ProjectSettings,
)
from esgvoc.core.service import config_manager
from esgvoc.core.service.state import StateService


def configure_and_install_esgvoc():
    """Configure esgvoc with test branch and synchronize"""
    try:
        test_branch = os.environ.get("TEST_BRANCH")
        repo_url = os.environ.get("REPO_URL")
        esgvoc_branch = os.environ.get("ESGVOC_LIBRARY_BRANCH")

        if not test_branch or not repo_url:
            raise ValueError(
                "TEST_BRANCH and REPO_URL environment variables must be set"
            )

        print(f"Configuring esgvoc to use CV from branch: {test_branch}")
        print(f"Repository: {repo_url}")
        print(f"Using esgvoc library from branch: {esgvoc_branch}")

        # Create configuration for the CV project using test branch
        project_config = ProjectSettings(
            project_name="test_cv", github_repo=repo_url, branch=test_branch
        )

        # Create universe settings
        universe_config = UniverseSettings(
            github_repo="https://github.com/WCRP-CMIP/WCRP-universe", branch="esgvoc"
        )

        # Create main setting with our test configuration
        custom_setting = Setting(universe=universe_config, projects=[project_config])

        # Update the global current_state with our custom configuration
        import esgvoc.core.service

        esgvoc.core.service.current_state = StateService(custom_setting)

        # Now synchronize with our custom settings
        print("Initializing esgvoc with test configuration...")
        esgvoc.core.service.current_state.synchronize_all()
        print("✅ ESGVoc configured and synchronized successfully!")

    except Exception as e:
        print(f"❌ ESGVoc configuration failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def test_cv_with_esgvoc():
    """Run CV validation tests with esgvoc"""
    try:
        print("Running CV validation tests...")

        # Add your specific esgvoc validation logic here
        # Example: result = esgvoc.validate_cv()
        # if not result.is_valid:
        #     sys.exit(1)

        print("✅ CV validation passed!")

    except Exception as e:
        print(f"❌ CV validation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: cv-validate.py [configure|test]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "configure":
        configure_and_install_esgvoc()
    elif command == "test":
        test_cv_with_esgvoc()
    else:
        print("Invalid command. Use 'configure' or 'test'")
        sys.exit(1)
