#!/usr/bin/env python3
"""Make web-sized versions of post images and record their image-host URLs.

Post images are referenced by local paths (data/assets_mapping.json maps them to the
original uploads on the image host). Those originals are full-size phone photos, often
5-8 MB each, and most carry GPS coordinates. This script produces, per image:

  - an AVIF (with a small progressive preview layer, so Chrome can show it early), and
  - a progressive JPEG fallback (uploading it is optional; without it, browsers that
    cannot show AVIF get the original upload),

both at most MAX_WIDTH x MAX_HEIGHT, rotated upright, with all metadata except the ICC
color profile removed. layouts/_default/_markup/render-image.html serves them through
<picture> once their URLs are listed in data/assets_optimized.json.

Usage:
  optimize_images.py build [--force]   encode images that have no entry in
                                       data/assets_optimized.json into optimized-images/
  optimize_images.py link <urls.txt>   read uploaded URLs (one per line, any order; extra
                                       text is ignored), match them to optimized-images/
                                       by file name and update data/assets_optimized.json

Requires macOS sips plus avifenc (libavif), jpegtran (libjpeg-turbo) and exiftool.
"""

import argparse
import concurrent.futures
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAPPING = ROOT / "data" / "assets_mapping.json"
OPTIMIZED = ROOT / "data" / "assets_optimized.json"
OUT = ROOT / "optimized-images"
MANIFEST = OUT / "manifest.json"

MAX_WIDTH, MAX_HEIGHT = 1800, 2400
JPEG_QUALITY = 80
AVIF_QUALITY = 60

# EXIF orientation -> (sips rotate degrees clockwise, sips flip)
ORIENTATION = {2: (0, "horizontal"), 3: (180, None), 4: (0, "vertical"),
               5: (90, "horizontal"), 6: (90, None), 7: (270, "horizontal"), 8: (270, None)}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def run(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True) + "\n", encoding="utf-8")


def out_names(keys) -> dict:
    """/assets/local-assets/posts/<post>/<file>.jpeg -> <post>-<file>; keys that would share a
    name (same file with different extensions) get the extension appended, e.g. <post>-<file>-png."""
    def base(key: str) -> str:
        parts = Path(key).with_suffix("").parts
        return f"{parts[-2]}-{parts[-1]}" if len(parts) >= 2 else parts[-1]
    counts = {}
    for key in keys:
        counts[base(key)] = counts.get(base(key), 0) + 1
    return {key: base(key) if counts[base(key)] == 1 else f"{base(key)}-{Path(key).suffix.lstrip('.').lower()}"
            for key in keys}


def source_for(key: str, url: str, work: Path) -> Path:
    local = ROOT / key.lstrip("/")
    if local.is_file():
        return local
    target = work / Path(url).name
    # The image host's Cloudflare front rejects urllib's default User-Agent with 403.
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (optimize_images.py)"})
    with urllib.request.urlopen(request, timeout=120) as response, target.open("wb") as handle:
        shutil.copyfileobj(response, handle)
    return target


def encode(key: str, url: str, name: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        src = source_for(key, url, work)
        png = work / "upright.png"
        run("sips", "-s", "format", "png", str(src), "--out", str(png))
        # sips keeps the EXIF orientation tag instead of applying it; rotate the pixels so the
        # output, which drops all EXIF, still shows upright.
        orientation = run("exiftool", "-s3", "-n", "-Orientation", str(src)).strip()
        rotate, flip = ORIENTATION.get(int(orientation) if orientation.isdigit() else 1, (0, None))
        if rotate:
            run("sips", "-r", str(rotate), str(png))
        if flip:
            run("sips", "-f", flip, str(png))
        size = run("sips", "-g", "pixelWidth", "-g", "pixelHeight", str(png))
        width = int(re.search(r"pixelWidth: (\d+)", size).group(1))
        height = int(re.search(r"pixelHeight: (\d+)", size).group(1))
        scale = min(1.0, MAX_WIDTH / width, MAX_HEIGHT / height)
        if scale < 1.0:
            width, height = round(width * scale), round(height * scale)
            run("sips", "-z", str(height), str(width), str(png))

        baseline = work / "baseline.jpg"
        run("sips", "-s", "format", "jpeg", "-s", "formatOptions", str(JPEG_QUALITY), str(png), "--out", str(baseline))
        # -copy icc keeps the color profile (many photos are Display P3) and drops EXIF/GPS.
        run("jpegtran", "-copy", "icc", "-optimize", "-progressive", "-outfile", str(OUT / f"{name}.jpg"), str(baseline))
        # avifenc does not pick up the profile sips writes into the PNG, so pass it explicitly.
        icc = work / "profile.icc"
        icc.write_bytes(subprocess.run(["exiftool", "-b", "-ICC_Profile", str(png)], capture_output=True).stdout)
        icc_args = ["--icc", str(icc)] if icc.stat().st_size else []
        run("avifenc", "--progressive", "-q", str(AVIF_QUALITY), "-y", "420", "-s", "6", "-j", "2",
            "--ignore-exif", "--ignore-xmp", *icc_args, str(png), str(OUT / f"{name}.avif"))
    return {"avif": f"{name}.avif", "jpg": f"{name}.jpg", "width": width, "height": height}


def build(force: bool) -> None:
    for tool in ("sips", "avifenc", "jpegtran", "exiftool"):
        if not shutil.which(tool):
            fail(f"{tool} is required (brew install libavif jpeg-turbo exiftool)")
    mapping, optimized = load(MAPPING), load(OPTIMIZED)
    OUT.mkdir(exist_ok=True)
    manifest = load(MANIFEST)
    names = out_names(mapping)
    todo = {key: url for key, url in mapping.items()
            if force or (key not in optimized
                         and manifest.get(key, {}).get("avif") != f"{names[key]}.avif")}
    if not todo:
        print("Nothing to encode: every mapped image already has an optimized version.")
        return
    print(f"Encoding {len(todo)} image(s) into {OUT.relative_to(ROOT)}/ ...")
    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(encode, key, url, names[key]): key for key, url in todo.items()}
        for done, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            key = futures[future]
            try:
                manifest[key] = future.result()
                print(f"[{done}/{len(todo)}] {manifest[key]['avif']}")
            except Exception as error:  # keep going; report at the end
                failures += 1
                print(f"[{done}/{len(todo)}] failed {key}: {error}", file=sys.stderr)
            dump(MANIFEST, manifest)
    print(f"Done. Upload every .avif (and optionally .jpg) in {OUT.relative_to(ROOT)}/ to the image host, "
          f"save the returned URLs to a text file and run: {Path(__file__).name} link <file>")
    if failures:
        fail(f"{failures} image(s) failed")


def link(urls_file: Path) -> None:
    manifest, optimized = load(MANIFEST), load(OPTIMIZED)
    if not manifest:
        fail(f"{MANIFEST.relative_to(ROOT)} is empty; run `build` first")
    urls = re.findall(r"https?://[^\s\"'<>()\[\],]+", urls_file.read_text(encoding="utf-8"))
    # Image hosts usually prefix uploads with an id ("1757407356140_<name>"), so match on the end.
    by_name = {}
    for url in urls:
        tail = url.rsplit("/", 1)[-1]
        for candidate in (tail, tail.split("_", 1)[-1]):
            by_name.setdefault(candidate, url)
    linked, missing = 0, []
    for key, entry in manifest.items():
        avif, jpg = by_name.get(entry["avif"]), by_name.get(entry["jpg"])
        if avif:
            # The JPEG fallback is optional: without it, browsers lacking AVIF get the original.
            optimized[key] = {"avif": avif, "width": entry["width"], "height": entry["height"]}
            if jpg:
                optimized[key]["jpg"] = jpg
            linked += 1
        elif key not in optimized:
            missing.append(entry["avif"])
    dump(OPTIMIZED, optimized)
    print(f"Linked {linked} image(s) in {OPTIMIZED.relative_to(ROOT)}.")
    if missing:
        print(f"{len(missing)} image(s) have no uploaded URL yet, e.g. {', '.join(missing[:5])}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--force", action="store_true", help="re-encode images that already have entries")
    link_parser = sub.add_parser("link")
    link_parser.add_argument("urls", type=Path)
    args = parser.parse_args()
    if args.command == "build":
        build(args.force)
    else:
        link(args.urls)


if __name__ == "__main__":
    main()
