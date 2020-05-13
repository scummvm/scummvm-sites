import logging

from buildbot.util import httpclientservice
from buildbot.www.hooks.github import GitHubEventHandler
from dateutil.parser import parse as dateparse
from twisted.internet import defer
from twisted.python import log


class PRGithubEventHandler(GitHubEventHandler):
    """GithubEventHandler that handles files in PRs"""

    @defer.inlineCallbacks
    def _get_pr_files(self, repo, number):
        """
        Get Files that belong to the Pull Request
        :param repo: the repo full name, ``{owner}/{project}``.
            e.g. ``buildbot/buildbot``
        """
        headers = {"User-Agent": "Buildbot"}
        if self._token:
            headers["Authorization"] = "token " + self._token

        url = "/repos/{}/pulls/{}/files".format(repo, number)
        http = yield httpclientservice.HTTPClientService.getService(
            self.master,
            self.github_api_endpoint,
            headers=headers,
            debug=self.debug,
            verify=self.verify,
        )
        res = yield http.get(url)
        data = yield res.json()
        return [f["filename"] for f in data]

    @defer.inlineCallbacks
    def handle_pull_request(self, payload, event):
        changes = []
        number = payload["number"]
        refname = "refs/pull/{}/{}".format(number, self.pullrequest_ref)
        basename = payload["pull_request"]["base"]["ref"]
        commits = payload["pull_request"]["commits"]
        title = payload["pull_request"]["title"]
        comments = payload["pull_request"]["body"]
        repo_full_name = payload["repository"]["full_name"]
        head_sha = payload["pull_request"]["head"]["sha"]

        log.msg("Processing GitHub PR #{}".format(number), logLevel=logging.DEBUG)

        head_msg = yield self._get_commit_msg(repo_full_name, head_sha)
        if self._has_skip(head_msg):
            log.msg(
                "GitHub PR #{}, Ignoring: "
                "head commit message contains skip pattern".format(number)
            )
            return ([], "git")

        action = payload.get("action")
        if action not in ("opened", "reopened", "synchronize"):
            log.msg("GitHub PR #{} {}, ignoring".format(number, action))
            return (changes, "git")

        files = yield self._get_pr_files(repo_full_name, number)

        properties = self.extractProperties(payload["pull_request"])
        properties.update({"event": event})
        properties.update({"basename": basename})
        change = {
            "revision": payload["pull_request"]["head"]["sha"],
            "when_timestamp": dateparse(payload["pull_request"]["created_at"]),
            "branch": refname,
            "revlink": payload["pull_request"]["_links"]["html"]["href"],
            "repository": payload["repository"]["html_url"],
            "project": payload["pull_request"]["base"]["repo"]["full_name"],
            "category": "pull",
            # TODO: Get author name based on login id using txgithub module
            "author": payload["sender"]["login"],
            "comments": "GitHub Pull Request #{0} ({1} commit{2})\n{3}\n{4}".format(
                number, commits, "s" if commits != 1 else "", title, comments
            ),
            "properties": properties,
            "files": files,
        }

        if callable(self._codebase):
            change["codebase"] = self._codebase(payload)
        elif self._codebase is not None:
            change["codebase"] = self._codebase

        changes.append(change)

        log.msg("Received {} changes from GitHub PR #{}".format(len(changes), number))
        return (changes, "git")
