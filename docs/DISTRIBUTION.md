# Distribution and release procedure

## Recommended formats

Publish the source on https://github.com/lunagoat/tty-terminal and submit the
small native package recipe to the AUR. The AUR hosts `PKGBUILD` and `.SRCINFO`,
not the built package or an AppImage. It downloads a versioned source release,
builds the font locally, and depends on the distribution's Kitty package.

Keep AppImage as an optional second format. The existing local AppImage bundles
CachyOS libraries requiring x86-64-v3 and Linux 6.1+. It is not a universal Linux
build. Before a public AppImage release:

1. Build on an older supported baseline with the minimum intended CPU target.
2. Pin downloads and verify checksums, rather than relying on changing continuous builds.
3. Supply the exact corresponding sources and notices for bundled third-party code.
4. Test Wayland and X11, graphics drivers, image rendering, and clean machines
   without system Kitty/Python installations.
5. Keep portable config empty or use the example; never publish personal settings.

The local AppImage build script is retained for development. Git ignores its
generated binaries, runtimes, and AppDir. The public release workflow publishes
only this project's source archive and checksums.

## First GitHub upload

Create an **empty** GitHub repository named `lunagoat/tty-terminal` (do not add a
separate README or license), then from this directory:

```sh
git status
# Set your preferred commit name/email if Git asks; use a GitHub noreply address if desired.
git add .
git commit -m "Prepare tty-terminal 0.1.0"
git push -u origin main
```

The local repository already has the intended origin URL. Authentication and
creating the remote repository remain account-owner actions. No credentials
are stored in the project.

## Validate and create a release

```sh
make check
python3 scripts/prepare_release.py
cp dist/0.1.0/tty-terminal-0.1.0.tar.gz dist/0.1.0/aur/
(cd dist/0.1.0/aur && makepkg)
```

Review the resulting `*.pkg.tar.zst`, and preferably test it in a clean Arch
chroot with devtools (`extra-x86_64-build`). The GitHub CI also builds it in an
Arch container. A successful local build is not a clean-chroot certification.
To install a reviewed local package, use `sudo pacman -U path/to/package.pkg.tar.zst`.

The release script uses **Git-tracked paths** and their current on-disk contents.
Stage newly added files first. Commit all release changes before tagging.
It writes a deterministic `.tar.gz`, SHA256SUMS, and a ready-to-submit AUR directory.
Run it without a custom SOURCE_DATE_EPOCH to match the release workflow's default
timestamp. Do not change a published archive: bump VERSION for a new release.

```sh
git tag -a v0.1.0 -m "tty-terminal 0.1.0"
git push origin v0.1.0
```

The tag workflow creates a **draft** GitHub release. Review its notes and assets,
then publish it. The uploaded asset must be named `tty-terminal-0.1.0.tar.gz`:
the AUR recipe intentionally uses this release asset, not GitHub's automatic
source archive. Verify its SHA256 matches the generated PKGBUILD.

## AUR submission

The name `tty-terminal` was unclaimed when checked during preparation; recheck
before submission. Create/sign in to an AUR account and register your SSH public
key there. GitHub and AUR authentication are separate.

After the GitHub release is public:

```sh
git -c init.defaultBranch=master clone ssh://aur@aur.archlinux.org/tty-terminal.git ../tty-terminal-aur
cp dist/0.1.0/aur/PKGBUILD dist/0.1.0/aur/.SRCINFO dist/0.1.0/aur/LICENSE ../tty-terminal-aur/
cd ../tty-terminal-aur
makepkg --verifysource
makepkg --printsrcinfo > .SRCINFO
git add PKGBUILD .SRCINFO LICENSE
git commit -m "Initial tty-terminal package"
git push
```

Do not commit `src/`, `pkg/`, tarballs, or built packages to the AUR repository.
For a later release, update VERSION and CHANGELOG, regenerate release artifacts,
publish the new GitHub release, and update PKGBUILD and .SRCINFO in the AUR repo.

## Existing development installs

The user install at `~/.local/bin/tty-terminal` can take precedence over
`/usr/bin/tty-terminal`, and a user desktop entry can override the packaged one.
After installing the native package, either launch `/usr/bin/tty-terminal`
explicitly or remove those two old user launcher files. Keep
`~/.config/tty-terminal/config.toml`; package installation does not overwrite it.

## References

- https://wiki.archlinux.org/title/AUR_submission_guidelines
- https://wiki.archlinux.org/title/Creating_packages
- https://docs.appimage.org/reference/best-practices.html
