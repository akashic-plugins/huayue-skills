from agent.plugin_composition import Context

api_version = 3
name = "huayue-skills"
version = "1.0.2"
skill_roots = ("skills",)


async def apply(ctx: Context, config: object) -> None:
    """保留纯 v3 generation 入口；Skill roots 由模块静态声明。"""

    _ = (ctx, config)
