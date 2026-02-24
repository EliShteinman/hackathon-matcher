from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_TEMPLATE_DIR = Path(__file__).parent


class TemplateRenderer:
    def __init__(self) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(_TEMPLATE_DIR)),
            autoescape=True,
        )

    def render_match_request(
        self, initiator_name: str, initiator_branch: str, target_name: str, approve_url: str
    ) -> str:
        template = self._env.get_template("match_request.html")
        reject_url = approve_url.replace("/approve/", "/reject/")
        return template.render(
            initiator_name=initiator_name,
            initiator_branch=initiator_branch,
            target_name=target_name,
            approve_url=approve_url,
            reject_url=reject_url,
        )

    def render_match_approved(
        self, initiator_name: str, target_name: str, target_branch: str, target_email: str
    ) -> str:
        template = self._env.get_template("match_approved.html")
        return template.render(
            initiator_name=initiator_name,
            target_name=target_name,
            target_branch=target_branch,
            target_email=target_email,
        )

    def render_match_rejected(self, initiator_name: str, target_name: str) -> str:
        template = self._env.get_template("match_rejected.html")
        return template.render(initiator_name=initiator_name, target_name=target_name)

    def render_match_cancelled(self, initiator_name: str, target_name: str) -> str:
        template = self._env.get_template("match_cancelled.html")
        return template.render(initiator_name=initiator_name, target_name=target_name)
