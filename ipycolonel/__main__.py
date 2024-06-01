import os
import shutil
import sys
from typing import List, Sequence, Set, Tuple, Union

import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from pip._vendor import pkg_resources


class Err:
    def __init__(self, err: str):
        self.err = err


def get_dist(
    name: str,
) -> Union[Tuple["pkg_resources.Distribution", None], Tuple[None, Err]]:
    dists = sorted(
        pkg_resources.find_on_path(None, "./ipycolonel-environment"),
        key=lambda i: str(i),
    )
    for dist in dists:
        if dist.project_name == name or dist.egg_name == name:
            return dist, None

    return None, Err("cannot find package named {!r}".format(name))


def get_deps(name: str):
    """
    Retrieves the dependencies of a given package.

    Args:
        name (str): The name of the package.

    Returns:
        Union[List[pkg_resources.Requirement], Err]: A list of requirements if the package is found,
        otherwise an instance of the Err class.
    """

    # https://gist.github.com/jaymecd/d42fcb3207cb4c4f5c1ea971a22c310f
    dist, err = get_dist(name)

    if err:
        return err
    else:
        assert dist
        return dist.requires()


def install(packages_or_flags: List[str]) -> int:
    pkgs_shortened = (
        packages_or_flags[:3] + [f"+{len(packages_or_flags) - 3}"]
        if len(packages_or_flags) > 3
        else packages_or_flags
    )
    print(f"● Installing {', '.join(pkgs_shortened)} \n")

    return os.system(
        "pip install --target=ipycolonel-environment --upgrade "
        + "--platform=linux_x86_64 --no-deps --prefer-binary "
        + " ".join(packages_or_flags)
    )


def remove(name: str):
    dist, err = get_dist(name)

    if err:
        print("error: ipycolonel remove: %s" % err.err)
        return 1

    assert dist

    path = os.path.dirname(dist._get_metadata_path_for_display(dist.PKG_INFO))
    record_file = os.path.join(path, "RECORD")

    with open(record_file, "rb") as f:
        lines = f.readlines()

    print("🐣 our beloved chick is staring at the directories...", end="", flush=True)
    all_dirs: Set[str] = set()

    for line in lines:
        if not line:
            continue

        fn = b"".join(line.split(b",")[:1]).decode("utf-8")

        if fn.startswith("../../"):
            print("\x1b[2K→ ignored binary file %s" % fn, end="\r", flush=True)
            continue

        all_dirs.add(fn.split("/")[0])

        try:
            os.remove(os.path.join("ipycolonel-environment", fn))
        except FileNotFoundError:
            continue

        print("\x1b[2K→ removed %s" % fn, end="\r", flush=True)

    print(f"\n🐣 our beloved chick removed {len(lines)} files\n")

    baseline = f"→ Removing {len(all_dirs)} empty directories... "
    print(baseline, end="\r", flush=True)

    removed_dirs = set()

    for path in all_dirs:
        path = os.path.join("ipycolonel-environment", path)
        if path in removed_dirs:
            continue

        removed_dirs.add(path)
        print(baseline + "%s" % path, end="\r", flush=True)

        try:
            shutil.rmtree(path)
        except Exception as err:
            print(f"\n[failed] {err}", end="", flush=True)

    print("\n🐣 our beloved chick removed %s directories" % len(removed_dirs))

    print("\nRemoved {name}".format(name=name))

    return 0


def deep_remove(packages: List[str]):
    for name in packages:
        deps = get_deps(name)

        if isinstance(deps, Err):
            print("failed.")
            print("error: ipycolonel deep remove: %s" % deps.err)
            return 1

        all_deps = list(map(lambda item: f"{item.name}", deps))

        if not all_deps:
            print("okay.")
            print(f"  ✓ {name} is all clear!\n")
            continue

        deps_shortened = (
            all_deps if len(all_deps) < 3 else all_deps[:2] + [f"+{len(all_deps) - 2}"]
        )

        print("● Removing packages: %s\n" % ", ".join(deps_shortened))

        for dep in all_deps:
            deep_remove([dep])
            remove(dep)

        remove(name)  # remove self


def install_deps(packages: Sequence[str], *, deep_install: bool = False) -> int:
    for name in packages:
        print(f"\nGetting deps of {name}... ", end="", flush=True)

        deps = get_deps(name)
        if isinstance(deps, Err):
            if "cannot find package named" in deps.err:
                print("package not installed yet")
                install([name])
                return install_deps([name])

            print("failed.")
            print("error: ipycolonel deps install: %s" % deps.err)
            return 1

        all_deps = list(map(lambda item: str(item), deps))

        if not all_deps:
            print("okay.")
            print(f"  ✓ {name} is all clear!\n")
            continue

        deps_shortened = (
            all_deps if len(all_deps) < 3 else all_deps[:2] + [f"+{len(all_deps) - 2}"]
        )
        print(f"done. ({', '.join(deps_shortened)})")

        print(f"  ● Installing {len(all_deps)} packages...\n")
        install(all_deps)

        print()

        if deep_install:
            for dep in deps:
                print(f"🧪 (EXPR1) Deep install ({name}): {dep}\n")
                install_deps([dep.name], deep_install=True)
                print()

    return 0


def main(args: List[str] = sys.argv[1:]) -> int:
    if len(args) == 0:
        print("Usage: ipycolonel <command> [args...]")
        return 1

    command = args[0]

    if command == "install":
        packages_or_flags = args[1:]

        if not packages_or_flags:
            print("Usage: ipycolonel install <packages> [flags...]")
            return 1

        return install(packages_or_flags)

    elif command == "deps":
        sub = args[1] if len(args) > 1 else None

        if not sub:
            print("Usage: ipycolonel deps <subcommand>")
            print("Subcommands:")
            print("  of <packages>")
            print("  install <packages>")
            print("  deep install <packages>")
            return 1

        if sub == "of":
            packages = args[2:]

            for name in packages:
                deps = get_deps(name)
                if isinstance(deps, Err):
                    print("error: ipycolonel deps of: %s" % deps.err)
                    return 1

                all_deps = list(map(lambda item: f"{item.name}", deps))
                print(f"{name} relies on: {', '.join(all_deps) or 'itself!'}")

            return 0

        elif sub == "install" or (sub == "deep" and args[2] == "install"):
            deep_install = sub == "deep"
            packages = args[2:] if not deep_install else args[3:]

            if deep_install:
                print("🧪 (EXPR1) Using deep install... \n")

            install_deps(packages, deep_install=deep_install)

            return 0

        else:
            command = "deps " + sub

    elif command in {"remove", "uninstall"}:
        packages = args[1:]

        if packages:
            ans = input("You sure? [Yn] ")
            if ans.strip().lower() in {"y", "yes"}:
                for name in packages:
                    # print(f"Removing {name}... ", end="", flush=True)
                    remove(name)
            else:
                print("Cancelled.")

        return 0

    elif command == "deep":
        sub = args[1] if len(args) > 1 else None

        if not sub:
            print("Usage: ipycolonel deep <subcommand>")

        if sub == "install":
            packages_or_flags = args[2:]
            print("🧪 (EXPR1) Using deep install... \n")

            for name in packages_or_flags:
                if name.startswith("--") or name.startswith("-"):
                    continue

                install([name])
                install_deps(packages_or_flags, deep_install=True)

            return 0

        elif sub in {"remove", "uninstall"}:
            packages = args[2:]

            if packages:
                ans = input("You sure? [Yn] ")
                print("🧪 (EXPR1) Using deep remove... \n")
                if ans.strip().lower() in {"y", "yes"}:
                    deep_remove(packages)
                else:
                    print("Cancelled.")

            return 0

        print("Unknown subcommand: %s" % sub)
        return 1

    print("Unknown command: %s" % command)
    return 1


if __name__ == "__main__":
    sys.exit(main())
