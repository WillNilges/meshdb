import os
from pathlib import Path

import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import status

from meshapi.models import Install
from meshapi.permissions import HasPanoramaUpdatePermission
from meshapi.util.constants import DEFAULT_EXTERNAL_API_TIMEOUT_SECONDS
from meshapi.util.django_pglocks import advisory_lock
from meshdb.celery import app as celery_app

# Config for gathering/generating panorama links
PANO_REPO_OWNER = "nycmeshnet"
PANO_REPO = "node-db"
PANO_BRANCH = "master"
PANO_DIR = "data/panoramas"
PANO_HOST = "https://node-db.netlify.app/panoramas/"


# Raised if we get total nonsense as a panorama title
class BadPanoramaTitle(Exception):
    pass


class GitHubError(Exception):
    pass


# View called to make MeshDB refresh the panoramas.
@api_view(["POST"])
@permission_classes([HasPanoramaUpdatePermission])
def update_panoramas(request):
    try:
        panoramas_saved, warnings = sync_github_panoramas()
        return Response(
            {
                "detail": f"Saved {panoramas_saved} panoramas. Got {len(warnings)} warnings.",
                "saved": panoramas_saved,
                "warnings": len(warnings),
                "warn_install_nums": warnings,
            },
            status=status.HTTP_200_OK,
        )
    except (ValueError, GitHubError) as e:
        print(e)
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@advisory_lock("update_panoramas_lock")
def sync_github_panoramas() -> tuple[int, list[str]]:
    # Check that we have all the environment variables we need
    owner = PANO_REPO_OWNER
    repo = PANO_REPO
    branch = PANO_BRANCH
    directory = PANO_DIR

    token = os.environ.get("PANO_GITHUB_TOKEN")
    if token is None:
        raise ValueError("Environment variable PANO_GITHUB_TOKEN not found")

    head_tree_sha = get_head_tree_sha(owner, repo, branch, token)
    if not head_tree_sha:
        raise GitHubError("Could not get head tree SHA from GitHub")

    panorama_files = list_files_in_git_directory(owner, repo, directory, head_tree_sha, token)
    if not panorama_files:
        raise GitHubError("Could not get file list from GitHub")

    panos = build_pano_dict(panorama_files)
    return set_panoramas(panos)


def set_panoramas(panos: dict[str, list[str]]) -> tuple[int, list[str]]:
    panoramas_saved = 0
    warnings = []

    host_url = PANO_HOST

    for install_number, filenames in panos.items():
        try:
            install: Install = Install.objects.get(install_number=int(install_number))
            panoramas = []
            if not install:
                print(
                    f"Warning: Could not add panorama to building (Install #{install_number}). Install does not exist."
                )
                warnings.append(install_number)
                continue
            for filename in filenames:
                file_url = f"{host_url}{filename}"
                panoramas.append(file_url)
            if install.building.panoramas == panoramas:
                continue
            for p in panoramas:
                if p not in install.building.panoramas:
                    install.building.panoramas.append(p)
            install.building.save()
            panoramas_saved += len(filenames)
        except Exception as e:
            print(f"Warning: Could not add panorama to building (Install #{install_number}): {e}")
            warnings.append(install_number)
    return panoramas_saved, warnings


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
def get_head_tree_sha(owner, repo, branch, token: str = ""):
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    master = requests.get(
        url, headers={"Authorization": f"Bearer {token}"}, timeout=DEFAULT_EXTERNAL_API_TIMEOUT_SECONDS
    )
    if master.status_code != 200:
        print(f"Error: Got status {master.status_code} from GitHub trying to get SHA.")
        return None
    master = master.json()
    return master["commit"]["commit"]["tree"]["sha"]


# Returns all the filenames, stripped of extensions and everything
def list_files_in_git_directory(owner: str, repo: str, directory: str, tree, token: str = ""):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{tree}?recursive=1"
    response = requests.get(
        url, headers={"Authorization": f"Bearer {token}"}, timeout=DEFAULT_EXTERNAL_API_TIMEOUT_SECONDS
    )
    if response.status_code != 200:
        print(f"Error: Failed to fetch GitHub directory contents. Status code: {response.status_code}")
        return None
    files = []
    tree = response.json()
    for item in tree["tree"]:
        if item["type"] == "blob" and directory in item["path"]:
            files.append(os.path.basename(item["path"]))
    return files
