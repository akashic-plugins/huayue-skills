"""Huayue Skill 包：把自带 skills 目录登记为当前组合的只读资产。"""
from agent.plugin_composition import Context
from agent.plugin_composition.assets import INSTALLED_ASSETS

api_version = 3
name = "huayue-skills"
version = "2.0.0"
inject = (INSTALLED_ASSETS,)


async def apply(ctx: Context) -> None:
    """登记插件自带 skills 目录；生命周期随当前 Root 的 Effect。"""

    _ = await ctx.require(INSTALLED_ASSETS).register(ctx, "skills", "skills")
