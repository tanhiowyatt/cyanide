from cyanide.vfs.profile_loader import invalidate, load


def test_msgpack_corruption_fallback(tmp_path):
    # Setup: Create a profile-like structure
    profile_dir = tmp_path / "profiles"
    ubuntu_dir = profile_dir / "ubuntu"
    ubuntu_dir.mkdir(parents=True)

    # Create valid YAML
    (ubuntu_dir / "static.yaml").write_text("static: {'/test.txt': {'content': 'OK'}}")
    (ubuntu_dir / "base.yaml").write_text("metadata: {os_id: ubuntu}")

    # Pre-compile
    load("ubuntu", profile_dir)
    msgpack_file = ubuntu_dir / ".compiled.msgpack"
    assert msgpack_file.exists()

    # 1. Corrupt the msgpack file
    msgpack_file.write_text("NOT_A_MSGPACK_FILE")

    # 2. Try to load again
    invalidate()
    data = load("ubuntu", profile_dir)

    # 3. Verify it fell back to YAML and regenerated
    assert data["static"]["/test.txt"]["content"] == "OK"
    assert msgpack_file.stat().st_size > 20  # Should be valid msgpack now
