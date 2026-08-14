from agent.plugin_composition import SKILLS, Context
from agent.plugins import Plugin

api_version = 3
name = "huayue-skills"
version = "1.0.2"
inject = (SKILLS,)


async def apply(ctx: Context, config: object) -> None:
    """Register the plugin-owned Skill catalog in the composition Root."""

    _ = config
    skills = ctx.require(SKILLS)
    await skills.register(ctx, "skills")


class HuayueSkillsPlugin(Plugin):
    api_version = 2
    name = "huayue-skills"
    version = "1.0.2"
    desc = "Huayue personal skills bundle"

    @classmethod
    def skill_roots(cls) -> tuple[str, ...]:
        return ("skills",)
