from agent.plugins import Plugin


class HuayueSkillsPlugin(Plugin):
    api_version = 2
    name = "huayue-skills"
    version = "1.0.2"
    desc = "Huayue personal skills bundle"

    @classmethod
    def skill_roots(cls) -> tuple[str, ...]:
        return ("skills",)
