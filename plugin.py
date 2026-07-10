from agent.plugins import Plugin


class HuayueSkillsPlugin(Plugin):
    name = "huayue-skills"
    version = "1.0.0"
    desc = "Huayue personal skills bundle"

    @classmethod
    def skill_roots(cls) -> tuple[str, ...]:
        return ("skills",)
