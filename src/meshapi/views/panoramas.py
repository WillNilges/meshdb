import os
from pathlib import Path
import requests
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import status
from meshapi.models import Building, Install

from meshapi.util.django_pglocks import advisory_lock

# Raised if we get total nonsense as a panorama title
class BadPanoramaTitle(Exception):
    pass

# View called to make MeshDB refresh the panoramas.
# We want a cache to be able to diff which panos we've already ingested. Maybe
# we could store it in postgres :P
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
# @advisory_lock() # TODO: Wanna lock the table when we update the panoramas?
def update_panoramas_from_github(request):
    # TODO: Make env variables
    owner = os.environ.get("PANO_REPO_OWNER")
    repo = os.environ.get("PANO_REPO")
    branch = os.environ.get("PANO_BRANCH")
    directory = os.environ.get("PANO_DIR")
    host_url = os.environ.get("PANO_HOST")

    if not owner or not repo or not branch or not directory or not host_url:
        return Response({"detail": "Did not find environment variables"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    head_tree_sha = get_head_tree_sha(owner, repo, branch)

    panorama_files = list_files_in_directory(owner, repo, directory, head_tree_sha)
    if not panorama_files:
        return Response({"detail": "Could not list files"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    print(panorama_files)

    panos = build_pano_dict(panorama_files)

    panoramas_saved = 0
    warnings = []

    for install_number, filenames in panos.items():
        try:
            install: Install = Install.objects.get(install_number=int(install_number))
            install.building.panoramas = []
            if not install:
                print(
                    f"Warning: Could not add panorama to building (Install #{install_number}). Install does not exist."
                )
                warnings.append(install_number)
                continue
            for filename in filenames:
                file_url = f"{host_url}{filename}"
                install.building.panoramas.append(file_url)
            install.building.save()
            panoramas_saved += len(filenames)
        except Exception as e:
            print(f"Warning: Could not add panorama to building (Install #{install_number}): {e}")
            warnings.append(install_number)

    return Response(
        {
            "detail": f"Saved {panoramas_saved} panoramas. Got {len(warnings)} warnings.",
            "saved": panoramas_saved,
            "warnings": len(warnings),
            "warn_install_nums": warnings,
        },
        status=status.HTTP_200_OK,
    )


def build_pano_dict(files: list[str]):
    panos = {}
    for f in files:
        try:
            number, label = parse_pano_title(Path(f).stem)
        except BadPanoramaTitle as e:
            print(e)
            continue
        if number not in panos:
            panos[number] = [f]
        else:
            panos[number].append(f)
    return panos

# This is awful. Maybe there are easy ways to generalize some cases like stripping
# spaces, but for now I would rather explicitly handle these cases until I have
# better tests.
def parse_pano_title(title: str):
    if len(title) <= 0:
        raise BadPanoramaTitle("Got title of length 0")

    # Get that file extension outta here
    stem = Path(title).stem

    # Handle dumb edge case
    if len(stem) > 4 and stem[0:4] == "IMG_":
        return (stem[4:], "")

    # Some of the files have spaces but are otherwise fine
    if stem[0] == " ":
        stem = stem[1:]

    # Handle any other dumb edge cases by bailing
    if not stem[0].isdigit():
        raise BadPanoramaTitle(f"First character not a digit: {title}")

    number = ""
    label = ""
    for i in range(0, len(stem)):
        if stem[i].isdigit():
            number += stem[i]
        elif i == 0:
            # There are some files in here that have a space or something in the
            # first letter, so we handle that edge case by ignoring it.
            continue
        else:
            label = stem[i:]
            break
    return (number, label)


# Gets the tree-sha, which we need to use the trees API (allows us to list up to
# 100k/7MB of data)
def get_head_tree_sha(owner, repo, branch):
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    master = requests.get(url)
    master = master.json()
    return master["commit"]["commit"]["tree"]["sha"]


# Returns all the filenames, stripped of extensions and everything
def list_files_in_directory(owner: str, repo: str, directory: str, tree):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{tree}?recursive=1"
    response = requests.get(url)

    if response.status_code == 200:
        files = []
        tree = response.json()
        for item in tree["tree"]:
            if item["type"] == "blob" and directory in item["path"]:
                files.append(os.path.basename(item["path"]))
        return files
    else:
        print(f"Error: Failed to fetch directory contents. Status code: {response.status_code}")
        return None
