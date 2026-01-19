# Create auto command send to private channel incase of errors at parsing level
# Either call to test on each parse request or by use call. > verify RSS feed is getting correct status and data
# If fails, auto send to admin channel the error for review 
# AND send "Error on our end, please try again later" to user.

import discord
from discord import app_commands
from discord.ext import commands

class Queries(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rt_counts", description="Show how many RT entities are cached.")
    async def rt_counts(self, interaction: discord.Interaction):
        store = getattr(self.bot, "rt_store", None)
        if store is None:
            await interaction.response.send_message("❌ rt_store not found (rt_poller not loaded).", ephemeral=True)
            return

        snap = await store.get_snapshot()
        tu = snap.trip_updates
        vp = snap.vehicle_positions

        tu_n = len(tu.entities) if tu and store.is_fresh(tu) and tu.entities else 0
        vp_n = len(vp.entities) if vp and store.is_fresh(vp) and vp.entities else 0

        def _preview_entities(entities, n=3):
            if not entities:
                return []
            try:
                # dict-like (mapping)
                if isinstance(entities, dict):
                    return list(entities.values())[:n]
                # sequence types
                if isinstance(entities, (list, tuple)):
                    return entities[:n]
                # generic iterable
                it = iter(entities)
                res = []
                for _ in range(n):
                    res.append(next(it))
                return res
            except Exception:
                try:
                    return list(entities)[:n]
                except Exception:
                    return []

        tu_preview = _preview_entities(getattr(tu, 'entities', None), 3) if tu else []
        vp_preview = _preview_entities(getattr(vp, 'entities', None), 3) if vp else []

        await interaction.response.send_message(
            f"TripUpdates: {tu_n} (fresh={store.is_fresh(tu) if tu else False})\n"
            f"VehiclePositions: {vp_n} (fresh={store.is_fresh(vp) if vp else False})\n"
            f"First up to 3 TripUpdates: {tu_preview}\n"
            f"First up to 3 VehiclePositions: {vp_preview}",
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Queries(bot))
