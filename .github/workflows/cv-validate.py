#!/usr/bin/env python3
import os
from pathlib import Path
import sys
from esgvoc.core.service.configuration.setting import (
    ServiceSettings,
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
        custom_setting = ServiceSettings(
            universe=universe_config,
            projects={
                project_config.project_name: project_config,
            },
        )

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
        test_can_read_all_term()
        test_repo()
        # test_can_read_all_term()
        print("✅ CV validation passed!")

    except Exception as e:
        print(f"❌ CV validation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def test_can_read_all_term():
    """Test that all collections and elements are queryable via esgvoc API"""
    import esgvoc.api as ev
    import json

    print("🔍 Testing esgvoc API access for all repository collections and elements...")

    project_name = "obs4REF"  # fallback if file not found

    print(f"Testing project: {project_name}")

    errors = []

    # Test 1: Verify project exists in esgvoc
    try:
        projects = ev.get_all_projects()
        if project_name not in projects:
            errors.append(
                f"❌ Project '{project_name}' not found in esgvoc. Available projects: {projects}"
            )
            return  # Can't continue without valid project
        else:
            print(f"✅ Project '{project_name}' found in esgvoc")
    except Exception as e:
        errors.append(f"❌ Failed to get projects from esgvoc: {e}")
        return

    # Test 2: Get collections from esgvoc and compare with repository
    try:
        esgvoc_collections = ev.get_all_collections_in_project(project_name)
        print(
            f"Found {len(esgvoc_collections)} collections in esgvoc for project {project_name}"
        )
    except Exception as e:
        errors.append(f"❌ Failed to get collections from esgvoc: {e}")
        return

    # Get collections from repository (directories with .jsonld files)
    repo_collections = []
    all_directories = [p for p in Path(".").iterdir() if p.is_dir()]

    for directory in all_directories:
        files_in_dir = list(directory.iterdir())
        jsonld_files = [f for f in files_in_dir if f.name.endswith(".jsonld")]
        if len(jsonld_files) > 0:
            repo_collections.append(directory.name)

    print(f"Found {len(repo_collections)} collections in repository")

    # Test 3: Verify each repository collection is queryable in esgvoc
    missing_in_esgvoc = []
    for collection_name in repo_collections:
        if collection_name not in esgvoc_collections:
            missing_in_esgvoc.append(collection_name)
        else:
            print(f"✅ Collection '{collection_name}' found in esgvoc")

    if missing_in_esgvoc:
        errors.append(
            f"❌ Collections found in repository but not in esgvoc: {missing_in_esgvoc}"
        )

    # Test 4: For each collection, verify all elements are queryable
    for collection_name in repo_collections:
        if collection_name in esgvoc_collections:
            print(f"\n📂 Testing elements in collection: {collection_name}")

            # Get elements from repository
            collection_dir = Path(".") / collection_name
            files_in_dir = list(collection_dir.iterdir())
            json_element_files = [
                f
                for f in files_in_dir
                if f.name.endswith(".json") and not f.name.endswith(".jsonld")
            ]

            repo_elements = []
            for json_file in json_element_files:
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        content = json.load(f)
                    element_id = content.get(
                        "id", json_file.stem
                    )  # fallback to filename
                    repo_elements.append(element_id)
                except:
                    repo_elements.append(
                        json_file.stem
                    )  # fallback to filename if can't parse

            # Get elements from esgvoc
            try:
                esgvoc_terms = ev.get_all_terms_in_collection(
                    project_name, collection_name
                )
                esgvoc_element_ids = [term.id for term in esgvoc_terms]

                print(f"   Repository elements: {len(repo_elements)}")
                print(f"   ESGVoc elements: {len(esgvoc_element_ids)}")

                # Check each repository element exists in esgvoc
                missing_elements = []
                for element_id in repo_elements:
                    if element_id not in esgvoc_element_ids:
                        missing_elements.append(element_id)
                    else:
                        print(f"   ✅ Element '{element_id}' found in esgvoc")

                if missing_elements:
                    errors.append(
                        f"❌ Collection '{collection_name}': Elements in repository but not in esgvoc: {missing_elements}"
                    )
                else:
                    print(
                        f"   ✅ All elements in collection '{collection_name}' are queryable via esgvoc"
                    )

            except Exception as e:
                errors.append(
                    f"❌ Failed to get terms from collection '{collection_name}': {e}"
                )

    # Test 5: Test general API functions
    try:
        all_terms = ev.get_all_terms_in_all_projects()
        print(
            f"\n📊 ESGVoc API successfully returned {len(all_terms)} total terms across all projects"
        )
    except Exception as e:
        errors.append(f"❌ Failed to get all terms from esgvoc: {e}")

    # Summary
    print(f"\n📊 ESGVoc API Validation Summary:")
    if errors:
        print(f"❌ Found {len(errors)} errors:")
        for error in errors:
            print(f"   {error}")
        raise Exception(f"ESGVoc API validation failed with {len(errors)} errors")
    else:
        print("✅ All collections and elements are properly queryable via esgvoc API!")
        print(f"✅ Validated {len(repo_collections)} collections")
        print("✅ All repository elements are accessible through esgvoc")


def test_repo():
    """Test repository structure and file requirements - generic for any CV"""
    import json

    print("🧪 Testing repository structure...")

    # Get all directories
    all_directories = [p for p in Path(".").iterdir() if p.is_dir()]

    # Identify collection directories by presence of .jsonld files
    collection_directories = []
    directories_with_json_but_no_jsonld = []

    for directory in all_directories:
        files_in_dir = list(directory.iterdir())
        jsonld_files = [f for f in files_in_dir if f.name.endswith(".jsonld")]
        json_files = [
            f
            for f in files_in_dir
            if f.name.endswith(".json") and not f.name.endswith(".jsonld")
        ]

        if len(jsonld_files) > 0:
            collection_directories.append(directory)
        elif len(json_files) > 0:
            # Directory has JSON files but no JSONLD context file
            directories_with_json_but_no_jsonld.append(directory)

    print(
        f"Found {len(collection_directories)} collection directories (with .jsonld files)"
    )
    print(
        f"Found {len(directories_with_json_but_no_jsonld)} directories with JSON but no context"
    )

    errors = []
    warnings = []

    # Warn about directories that might be missing context files
    for directory in directories_with_json_but_no_jsonld:
        warnings.append(
            f"⚠️  DID YOU FORGET CONTEXT for directory '{directory.name}'? (has .json files but no .jsonld context)"
        )

    # Test each collection directory
    for directory in collection_directories:
        print(f"\n📁 Testing collection directory: {directory.name}")

        collection_errors = []

        # Test 1: Check directory structure (at least one jsonld + one other element)
        files_in_dir = list(directory.iterdir())
        jsonld_files = [f for f in files_in_dir if f.name.endswith(".jsonld")]
        other_files = [f for f in files_in_dir if not f.name.endswith(".jsonld")]

        if len(jsonld_files) == 0:
            collection_errors.append(
                f"❌ {directory.name}: No .jsonld context file found"
            )
        elif len(jsonld_files) > 1:
            warnings.append(
                f"⚠️  {directory.name}: Multiple .jsonld files found: {[f.name for f in jsonld_files]}"
            )

        if len(other_files) == 0:
            collection_errors.append(
                f"❌ {directory.name}: No element files found (directory only contains context)"
            )

        # Test 2: Validate JSONLD context structure
        for jsonld_file in jsonld_files:
            try:
                with open(jsonld_file, "r", encoding="utf-8") as f:
                    jsonld_content = json.load(f)

                if "@context" not in jsonld_content:
                    collection_errors.append(
                        f"❌   {jsonld_file.name}: Missing '@context' field"
                    )
                    continue

                context = jsonld_content["@context"]
                if not isinstance(context, dict):
                    collection_errors.append(
                        f"❌   {jsonld_file.name}: '@context' must be a dictionary"
                    )
                    continue

                # Check for required fields in context
                required_context_fields = ["id", "type", "@base"]
                missing_fields = [
                    field for field in required_context_fields if field not in context
                ]

                if missing_fields:
                    collection_errors.append(
                        f"❌   {jsonld_file.name}: Missing required fields in @context: {missing_fields}"
                    )

            except json.JSONDecodeError as e:
                collection_errors.append(
                    f"❌   {jsonld_file.name}: Invalid JSON syntax - {e}"
                )
            except Exception as e:
                collection_errors.append(
                    f"❌   {jsonld_file.name}: Error reading file - {e}"
                )

        # Test 3: Validate element files structure
        json_element_files = [f for f in other_files if f.name.endswith(".json")]

        for element_file in json_element_files:
            try:
                with open(element_file, "r", encoding="utf-8") as f:
                    element_content = json.load(f)

                # Check for required fields in element
                required_element_fields = ["id", "type", "@context"]
                missing_fields = [
                    field
                    for field in required_element_fields
                    if field not in element_content
                ]

                if missing_fields:
                    collection_errors.append(
                        f"❌   {element_file.name}: Missing required fields: {missing_fields}"
                    )

            except json.JSONDecodeError as e:
                collection_errors.append(
                    f"❌   {element_file.name}: Invalid JSON syntax - {e}"
                )
            except Exception as e:
                collection_errors.append(
                    f"❌   {element_file.name}: Error reading file - {e}"
                )

        # Print collection result
        if collection_errors:
            print(f"❌ {directory.name}: Failed validation")
            for error in collection_errors:
                print(f"   {error}")
            errors.extend(collection_errors)
        else:
            print(f"✅ {directory.name}: Passed validation")

    # Test 4: Validate project_specs.json source_collection references
    print(f"\n📄 Testing project_specs.json references...")
    try:
        with open("project_specs.json", "r", encoding="utf-8") as f:
            project_specs = json.load(f)

        # Extract all source_collection references
        source_collections = set()

        # Check drs_specs collections
        if "drs_specs" in project_specs:
            for drs_spec in project_specs["drs_specs"]:
                if "parts" in drs_spec:
                    for part in drs_spec["parts"]:
                        if "collection_id" in part:
                            source_collections.add(part["collection_id"])

        # Check global_attributes_specs collections
        if (
            "global_attributes_specs" in project_specs
            and "specs" in project_specs["global_attributes_specs"]
        ):
            for attr_name, attr_spec in project_specs["global_attributes_specs"][
                "specs"
            ].items():
                if "source_collection" in attr_spec:
                    source_collections.add(attr_spec["source_collection"])

        print(
            f"Found {len(source_collections)} unique source_collection references in project_specs.json"
        )

        # Check if each referenced collection directory exists
        existing_directories = {d.name for d in Path(".").iterdir() if d.is_dir()}

        for collection in source_collections:
            if collection not in existing_directories:
                errors.append(
                    f"❌ project_specs.json references non-existent collection: '{collection}'"
                )
            else:
                print(f"   ✅ {collection}: Referenced directory exists")

    except FileNotFoundError:
        warnings.append(
            "⚠️  project_specs.json not found - skipping source_collection validation"
        )
    except Exception as e:
        errors.append(f"❌ Error reading project_specs.json: {e}")

    # Display warnings
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"   {warning}")

    # Summary
    print(f"\n📊 Validation Summary:")
    if errors:
        print(f"❌ Found {len(errors)} errors:")
        for error in errors:
            print(f"   {error}")
        raise Exception(f"Repository validation failed with {len(errors)} errors")
    else:
        print("✅ All repository structure tests passed!")
        print(f"✅ Validated {len(collection_directories)} collection directories")
        print("✅ All required files have proper structure")
        if "project_specs.json" in [f.name for f in Path(".").iterdir()]:
            print("✅ All project_specs.json references are valid")


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
