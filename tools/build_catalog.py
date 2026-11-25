#!/usr/bin/env python3
"""Rebuilds catalog.json from the zips in zips/.

Each zip must hold one folder named blank-<name>, with blank-<name>/blank-<name>.php inside,
whose header gives at least "Plugin Name" and "Version" (x.y.z). Optional headers:
"Description" and "Requires Plugins" (comma-separated slugs, e.g. "blank-core, woocommerce").

A zip with another name is renamed to zips/<slug>-<version>.zip. A version already published
is never replaced: if the same name exists with other content, the run stops and nothing changes.
For each extension the catalog lists the highest version.

Usage: python3 tools/build_catalog.py   (from the repository root)
Exit code 1 with a French message when a zip is refused.
"""
import hashlib
import json
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIPS = os.path.join(ROOT, "zips")
CATALOG = os.path.join(ROOT, "catalog.json")
SLUG = re.compile(r"^blank-[a-z0-9-]{1,40}$")
VERSION = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}$")
MAX = 20 * 1024 * 1024


def fail(message):
    print("REFUSÉ : " + message)
    sys.exit(1)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def header(text, field):
    found = re.search(r"^[ \t/*#@]*" + re.escape(field) + r":\s*(.+?)\s*$", text, re.M | re.I)
    return found.group(1).strip() if found else ""


JUNK = re.compile(r"(^__MACOSX/|(^|/)\.DS_Store$|(^|/)Thumbs\.db$)")


def clean_zip(path):
    """Removes Mac/Windows hidden files (__MACOSX, .DS_Store, Thumbs.db) from a zip, in place."""
    try:
        with zipfile.ZipFile(path) as zf:
            junk = [n for n in zf.namelist() if JUNK.search(n)]
            if not junk:
                return False
            keep = [(i, zf.read(i)) for i in zf.infolist() if not JUNK.search(i.filename)]
    except zipfile.BadZipFile:
        return False
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for info, data in keep:
            out.writestr(info, data)
    os.replace(tmp, path)
    return True


def read_zip(path):
    name = os.path.basename(path)
    if clean_zip(path):
        print("nettoyé (fichiers cachés Mac/Windows retirés) : " + name)
    if os.path.getsize(path) > MAX:
        fail("%s dépasse 20 Mo." % name)
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        fail("%s n'est pas un zip valide." % name)
    names = zf.namelist()
    tops = {n.split("/", 1)[0] for n in names}
    if len(tops) != 1:
        fail("%s doit contenir un seul dossier (trouvé : %s)." % (name, ", ".join(sorted(tops))))
    slug = tops.pop()
    if not SLUG.match(slug):
        fail("%s : le dossier « %s » doit s'appeler blank-quelquechose (minuscules, chiffres, tirets)." % (name, slug))
    for n in names:
        if ".." in n or "\\" in n or n.startswith("/"):
            fail("%s contient un chemin interdit : %s" % (name, n))
    main = slug + "/" + slug + ".php"
    if main not in names:
        fail("%s : le fichier principal %s est absent." % (name, main))
    text = zf.read(main)[:8192].decode("utf-8", "replace")
    plugin_name = header(text, "Plugin Name")
    version = header(text, "Version")
    if not plugin_name:
        fail("%s : l'en-tête « Plugin Name » manque dans %s." % (name, main))
    if not VERSION.match(version):
        fail("%s : la version « %s » doit avoir la forme 1.2.3." % (name, version))
    requires = [r.strip() for r in header(text, "Requires Plugins").split(",") if r.strip()]
    for r in requires:
        if r != "woocommerce" and not SLUG.match(r):
            fail("%s : dépendance non gérée « %s » (seulement woocommerce ou blank-…)." % (name, r))
    return {
        "slug": slug,
        "name": plugin_name[:80],
        "description": header(text, "Description")[:300],
        "version": version,
        "requires": requires,
    }


def vkey(v):
    return tuple(int(x) for x in v.split("."))


def main():
    os.makedirs(ZIPS, exist_ok=True)
    renames = []
    best = {}
    for fname in sorted(os.listdir(ZIPS)):
        if not fname.lower().endswith(".zip"):
            continue
        path = os.path.join(ZIPS, fname)
        info = read_zip(path)
        canonical = "%s-%s.zip" % (info["slug"], info["version"])
        if fname != canonical:
            target = os.path.join(ZIPS, canonical)
            if os.path.exists(target):
                if sha256(target) != sha256(path):
                    fail("la version %s de %s est déjà publiée avec un autre contenu. Change le numéro de version." % (info["version"], info["slug"]))
                os.remove(path)
            else:
                os.rename(path, target)
            renames.append("%s -> %s" % (fname, canonical))
            path = target
        info["zip"] = "zips/" + canonical
        info["sha256"] = sha256(path)
        current = best.get(info["slug"])
        if current is None or vkey(info["version"]) > vkey(current["version"]):
            best[info["slug"]] = info

    catalog = {"plugins": [best[s] for s in sorted(best)]}
    with open(CATALOG, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    for r in renames:
        print("renommé : " + r)
    for item in catalog["plugins"]:
        print("catalogue : %s %s" % (item["slug"], item["version"]))


if __name__ == "__main__":
    main()
