import os


def test_flash(labgrid_session):
    t = labgrid_session
    
    probe_name = os.environ.get("PROBE_NAME") or "no-probe"

    d = t.get_driver("ProbeRsDriver", name=probe_name)

    binary = os.environ.get("BINARY") or "no-binary"

    fw_version = os.environ.get("FW_VERSION") or "no-version"
    fw_hash = os.environ.get("FW_HASH") or "no-hash"

    print(f"flashing {binary} with firmware {fw_version}")
    # flash binary
    d.flash(binary)
    print("finished flashing {binary}")
    print("verifying version")

    # attach with reset and read logs line-by-line from the test
    stream = d.attach_with_reset(binary, timeout=30.0)

    try:
        it = stream.iter_lines()

        try:
            first_line = next(it)
        except StopIteration:
            raise AssertionError("no output received from probe-rs")

        assert f"Launching: FW version={fw_version} hash={fw_hash}" in first_line, f"unexpected first line: {first_line}"

    finally:
        # Always stop the subprocess, even on assertion failure
        stream.close()
