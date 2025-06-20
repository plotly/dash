"""
Test suite for Dash packaging and build system.

Tests verify:
1. sdist and wheel builds contain the same essential content
2. Built components (dcc, html, dash_table) are present and complete
3. Package sizes are within expected ranges
4. Build artifacts are properly excluded
"""

import tarfile
import zipfile
import subprocess
import pytest


class TestPackaging:
    """Test Dash packaging system including sdist, wheel, and build hooks."""

    @pytest.fixture(scope="class")
    def build_artifacts(self, tmp_path_factory):
        """Build both sdist and wheel for testing."""
        # Create a temporary directory for build artifacts
        build_dir = tmp_path_factory.mktemp("build_test")

        # Build both sdist and wheel
        subprocess.run(
            ["uv", "build", "--sdist", "--out-dir", str(build_dir)],
            capture_output=True,
            text=True,
            check=True,
        )

        subprocess.run(
            ["uv", "build", "--wheel", "--out-dir", str(build_dir)],
            capture_output=True,
            text=True,
            check=True,
        )

        # Find the built files
        sdist_files = list(build_dir.glob("*.tar.gz"))
        wheel_files = list(build_dir.glob("*.whl"))

        assert len(sdist_files) == 1, f"Expected 1 sdist, found {len(sdist_files)}"
        assert len(wheel_files) == 1, f"Expected 1 wheel, found {len(wheel_files)}"

        return {
            "sdist_path": sdist_files[0],
            "wheel_path": wheel_files[0],
            "build_dir": build_dir,
        }

    @pytest.fixture
    def extracted_sdist(self, build_artifacts, tmp_path):
        """Extract sdist contents for testing."""
        extract_dir = tmp_path / "sdist_extracted"
        extract_dir.mkdir()

        with tarfile.open(build_artifacts["sdist_path"], "r:gz") as tar:
            tar.extractall(extract_dir)

        # Find the main dash directory (should be dash-X.Y.Z/)
        dash_dirs = [
            d
            for d in extract_dir.iterdir()
            if d.is_dir() and d.name.startswith("dash-")
        ]
        assert len(dash_dirs) == 1, f"Expected 1 dash directory, found {len(dash_dirs)}"

        return dash_dirs[0]

    @pytest.fixture
    def extracted_wheel(self, build_artifacts, tmp_path):
        """Extract wheel contents for testing."""
        extract_dir = tmp_path / "wheel_extracted"
        extract_dir.mkdir()

        with zipfile.ZipFile(build_artifacts["wheel_path"], "r") as zip_file:
            zip_file.extractall(extract_dir)

        return extract_dir

    def test_build_succeeds(self, build_artifacts):
        """Test that both sdist and wheel builds complete successfully."""
        assert build_artifacts["sdist_path"].exists()
        assert build_artifacts["wheel_path"].exists()
        assert build_artifacts["sdist_path"].stat().st_size > 1000000  # > 1MB
        assert build_artifacts["wheel_path"].stat().st_size > 1000000  # > 1MB

    def test_package_sizes_reasonable(self, build_artifacts):
        """Test that package sizes are within reasonable bounds."""
        sdist_size = build_artifacts["sdist_path"].stat().st_size
        wheel_size = build_artifacts["wheel_path"].stat().st_size

        # Sizes should be between 3MB and 15MB (reasonable bounds)
        assert (
            3_000_000 < sdist_size < 15_000_000
        ), f"sdist size {sdist_size} outside expected range"
        assert (
            3_000_000 < wheel_size < 15_000_000
        ), f"wheel size {wheel_size} outside expected range"

        # wheel should be roughly similar size to sdist (within 50% difference)
        size_ratio = max(sdist_size, wheel_size) / min(sdist_size, wheel_size)
        assert (
            size_ratio < 1.5
        ), f"Size difference too large: sdist={sdist_size}, wheel={wheel_size}"

    def test_core_python_modules_present(self, extracted_sdist, extracted_wheel):
        """Test that core Python modules are present in both packages."""
        # Core modules that should be present
        core_modules = [
            "dash/__init__.py",
            "dash/dash.py",
            "dash/_callback.py",
            "dash/_configs.py",
            "dash/dependencies.py",
            "dash/version.py",
        ]

        for module in core_modules:
            # Check in sdist
            sdist_path = extracted_sdist / module
            assert sdist_path.exists(), f"Missing {module} in sdist"

            # Check in wheel
            wheel_path = extracted_wheel / module
            assert wheel_path.exists(), f"Missing {module} in wheel"

    def test_built_components_present(self, extracted_sdist, extracted_wheel):
        """Test that built components (dcc, html, dash_table) are present and complete."""
        # Component directories that should exist
        component_dirs = ["dash/dcc", "dash/html", "dash/dash_table"]

        for comp_dir in component_dirs:
            # Check sdist
            sdist_dir = extracted_sdist / comp_dir
            assert (
                sdist_dir.exists() and sdist_dir.is_dir()
            ), f"Missing {comp_dir} in sdist"

            # Check wheel
            wheel_dir = extracted_wheel / comp_dir
            assert (
                wheel_dir.exists() and wheel_dir.is_dir()
            ), f"Missing {comp_dir} in wheel"

    def test_dcc_components_complete(self, extracted_sdist, extracted_wheel):
        """Test that DCC components are properly built and included."""
        # Key DCC files that should exist
        dcc_files = [
            "dash/dcc/__init__.py",
            "dash/dcc/Graph.py",
            "dash/dcc/Dropdown.py",
            "dash/dcc/Input.py",
            "dash/dcc/dash_core_components.js",
            "dash/dcc/dash_core_components-shared.js",
        ]

        for dcc_file in dcc_files:
            # Check in both packages
            assert (extracted_sdist / dcc_file).exists(), f"Missing {dcc_file} in sdist"
            assert (extracted_wheel / dcc_file).exists(), f"Missing {dcc_file} in wheel"

        # Check for async component files
        async_files = [
            "dash/dcc/async-graph.js",
            "dash/dcc/async-dropdown.js",
            "dash/dcc/async-upload.js",
        ]

        for async_file in async_files:
            assert (
                extracted_sdist / async_file
            ).exists(), f"Missing {async_file} in sdist"
            assert (
                extracted_wheel / async_file
            ).exists(), f"Missing {async_file} in wheel"

    def test_html_components_complete(self, extracted_sdist, extracted_wheel):
        """Test that HTML components are properly built and included."""
        html_files = [
            "dash/html/__init__.py",
            "dash/html/Div.py",
            "dash/html/H1.py",
            "dash/html/Button.py",
            "dash/html/dash_html_components.min.js",
        ]

        for html_file in html_files:
            assert (
                extracted_sdist / html_file
            ).exists(), f"Missing {html_file} in sdist"
            assert (
                extracted_wheel / html_file
            ).exists(), f"Missing {html_file} in wheel"

    def test_dash_table_components_complete(self, extracted_sdist, extracted_wheel):
        """Test that Dash Table components are properly built and included."""
        table_files = [
            "dash/dash_table/__init__.py",
            "dash/dash_table/DataTable.py",
            "dash/dash_table/bundle.js",
            "dash/dash_table/async-table.js",
        ]

        for table_file in table_files:
            assert (
                extracted_sdist / table_file
            ).exists(), f"Missing {table_file} in sdist"
            assert (
                extracted_wheel / table_file
            ).exists(), f"Missing {table_file} in wheel"

    def test_key_js_files_functional(self, extracted_sdist, extracted_wheel):
        """Test that key JavaScript files are present and appear functional."""
        key_js_files = [
            "dash/dcc/dash_core_components.js",
            "dash/dcc/dash_core_components-shared.js",
            "dash/dash_table/bundle.js",
            "dash/html/dash_html_components.min.js",
        ]

        for js_file in key_js_files:
            # Check in both packages
            sdist_file = extracted_sdist / js_file
            wheel_file = extracted_wheel / js_file

            assert sdist_file.exists(), f"Missing {js_file} in sdist"
            assert wheel_file.exists(), f"Missing {js_file} in wheel"

            # Basic functional checks
            sdist_content = sdist_file.read_text(encoding="utf-8")
            wheel_content = wheel_file.read_text(encoding="utf-8")

            # Should contain some JavaScript patterns
            assert len(sdist_content) > 1000, f"{js_file} in sdist seems too small"
            assert len(wheel_content) > 1000, f"{js_file} in wheel seems too small"

            # Should not contain obvious build artifacts
            assert (
                "TODO" not in sdist_content.upper()
            ), f"{js_file} in sdist contains TODO"
            assert (
                "TODO" not in wheel_content.upper()
            ), f"{js_file} in wheel contains TODO"

            # Content should be the same between sdist and wheel
            assert (
                sdist_content == wheel_content
            ), f"{js_file} differs between sdist and wheel"

    def test_unwanted_files_excluded(self, extracted_sdist, extracted_wheel):
        """Test that unwanted files are excluded from packages."""
        # Files/directories that should NOT be in the package
        unwanted_patterns = [
            "node_modules/",
            "tests/",
            "components/",
            ".git/",
            "*.pyc",
            "__pycache__/",
            ".pytest_cache/",
            "build/",
            "dist/",
            ".venv/",
            "venv/",
        ]

        def check_unwanted(directory, package_type):
            """Check that unwanted files are not present."""
            for pattern in unwanted_patterns:
                if pattern.endswith("/"):
                    # Directory pattern
                    matches = list(directory.rglob(pattern.rstrip("/")))
                    # Filter out dash-renderer/build which is needed at runtime
                    if pattern == "build/":
                        matches = [m for m in matches if "dash-renderer" not in str(m)]
                    # Filter out labextension/dist which is needed for JupyterLab integration
                    if pattern == "dist/":
                        matches = [m for m in matches if "labextension" not in str(m)]
                    assert (
                        len(matches) == 0
                    ), f"Found unwanted directory {pattern} in {package_type}: {matches}"
                else:
                    # File pattern
                    matches = list(directory.rglob(pattern))
                    if matches:
                        # Allow some exceptions like metadata files
                        filtered_matches = [
                            m
                            for m in matches
                            if not any(
                                part in str(m)
                                for part in ["metadata", "PKG-INFO", "SOURCES.txt"]
                            )
                        ]
                        assert (
                            len(filtered_matches) == 0
                        ), f"Found unwanted files {pattern} in {package_type}: {filtered_matches}"

        check_unwanted(extracted_sdist, "sdist")
        check_unwanted(extracted_wheel, "wheel")

    def test_metadata_files_present(self, extracted_sdist, extracted_wheel):
        """Test that required metadata files are present."""
        # Files that should be in sdist
        sdist_metadata = [
            "PKG-INFO",
            "pyproject.toml",
            "README.md",
            "LICENSE",
        ]

        for metadata_file in sdist_metadata:
            assert (
                extracted_sdist / metadata_file
            ).exists(), f"Missing {metadata_file} in sdist"

        # Check wheel metadata
        wheel_metadata_dirs = list(extracted_wheel.glob("*.dist-info"))
        assert (
            len(wheel_metadata_dirs) == 1
        ), f"Expected 1 .dist-info dir, found {len(wheel_metadata_dirs)}"

        wheel_metadata_files = [
            "METADATA",
            "WHEEL",
        ]

        # Optional files that might be present
        optional_metadata_files = [
            "top_level.txt",
            "RECORD",
        ]

        metadata_dir = wheel_metadata_dirs[0]
        for metadata_file in wheel_metadata_files:
            assert (
                metadata_dir / metadata_file
            ).exists(), f"Missing {metadata_file} in wheel metadata"

        # Check that at least some optional files are present
        optional_present = any(
            (metadata_dir / f).exists() for f in optional_metadata_files
        )
        assert (
            optional_present
        ), f"None of the optional metadata files found: {optional_metadata_files}"

    def test_sdist_wheel_content_equivalence(self, extracted_sdist, extracted_wheel):
        """Test that sdist and wheel contain equivalent Python content."""
        # Key Python files that should be identical
        python_files_to_compare = [
            "dash/__init__.py",
            "dash/dash.py",
            "dash/dependencies.py",
            "dash/version.py",
            "dash/dcc/__init__.py",
            "dash/html/__init__.py",
            "dash/dash_table/__init__.py",
        ]

        for py_file in python_files_to_compare:
            sdist_file = extracted_sdist / py_file
            wheel_file = extracted_wheel / py_file

            if sdist_file.exists() and wheel_file.exists():
                sdist_content = sdist_file.read_text(encoding="utf-8")
                wheel_content = wheel_file.read_text(encoding="utf-8")
                assert (
                    sdist_content == wheel_content
                ), f"{py_file} differs between sdist and wheel"
