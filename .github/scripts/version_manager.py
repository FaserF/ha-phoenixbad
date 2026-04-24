"""Version manager for Phoenix-Bad."""
import argparse
import json
import os
import re
import subprocess
import glob


def find_manifest():
    """Find the manifest.json file."""
    matches = glob.glob("custom_components/*/manifest.json")
    return matches[0] if matches else None


def get_current_version(manifest_path):
    """Get the current version from git tags or manifest."""
    try:
        tags = (
            subprocess.check_output(["git", "tag"], stderr=subprocess.DEVNULL)
            .decode()
            .splitlines()
        )
        v_tags = []
        for tag in tags:
            tag = tag.strip()
            # Match Major.Minor.Patch (optional bX)
            match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:b(\d+))?$", tag)
            if match:
                maj, min_v, pat, b_n = match.groups()
                v_tags.append(
                    {
                        "tag": tag,
                        "key": (
                            int(maj),
                            int(min_v),
                            int(pat),
                            (int(b_n) if b_n else 999), # Stable is higher than beta
                        ),
                    }
                )
        if v_tags:
            return sorted(v_tags, key=lambda x: x["key"], reverse=True)[0]["tag"]
    except (subprocess.CalledProcessError, IndexError, ValueError):
        pass

    if manifest_path and os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f).get("version", "1.0.0")
    return "1.0.0"


def write_version(v, manifest_path):
    """Write the new version to manifest and VERSION file."""
    with open("VERSION", "w", encoding="utf-8") as f:
        f.write(v)
    if manifest_path and os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["version"] = v
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")


def calculate_version(bump_type, release_channel, curr):
    """Calculate the next version based on bump type and channel."""
    # Match Major.Minor.Patch (optional bX)
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:b(\d+))?$", curr)
    if not match:
        major, minor, patch, beta = 1, 0, 0, None
    else:
        major, minor, patch, beta = match.groups()
        major, minor, patch = int(major), int(minor), int(patch)
        beta = int(beta) if beta else None

    if release_channel == "stable":
        if beta is not None:
            # If we were in beta, stable release is just the base version
            return f"{major}.{minor}.{patch}"

        if bump_type == "major":
            return f"{major + 1}.0.0"
        if bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        return f"{major}.{minor}.{patch + 1}"

    if release_channel == "beta":
        if beta is not None:
            # Already in beta, just bump the beta number
            return f"{major}.{minor}.{patch}b{beta + 1}"

        # Starting a new beta. First bump the target segment
        if bump_type == "major":
            return f"{major + 1}.0.0b0"
        if bump_type == "minor":
            return f"{major}.{minor + 1}.0b0"
        return f"{major}.{minor}.{patch + 1}b0"

    raise ValueError(f"Unknown release channel: {release_channel}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["get", "bump"])
    parser.add_argument("--bump-type", choices=["major", "minor", "patch"], default="patch")
    parser.add_argument("--release-type", choices=["stable", "beta"], default="stable")
    parser.add_argument("--manifest", default=None)
    args = parser.parse_args()

    m_path = args.manifest or find_manifest()

    if args.action == "get":
        print(get_current_version(m_path))
    elif args.action == "bump":
        current = get_current_version(m_path)
        new_v = calculate_version(args.bump_type, args.release_type, current)
        write_version(new_v, m_path)
        print(new_v)
