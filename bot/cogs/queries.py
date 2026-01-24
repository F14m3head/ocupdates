# User facing commands
from discord.ext import commands
from discord import app_commands
import discord
import os


class QuerieCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Log channel ID
        self.log_channel_id = int(os.getenv("LOG_CHANNEL_ID", "0"))
        if self.log_channel_id == 0:
            raise RuntimeError("LOG_CHANNEL_ID is missing/invalid in .env")

    class AlertView(discord.ui.View):
        def __init__(self, alerts):
            super().__init__(timeout=300)
            self.alerts = alerts
            self.current_page = 0
            self.total_pages = self._count_entities(alerts.feed)
            self.update_buttons()

        def _count_entities(self, feed) -> int:
            if not feed:
                return 0
            # Try common attributes that may hold entities
            for attr in ("entries",):
                val = getattr(feed, attr, None)
                if val is not None:
                    try:
                        return int(len(val))
                    except Exception:
                        break
            # Fallback when count is unknown
            return 0


        def update_buttons(self):
            self.prev_button.disabled = (self.current_page == 0)
            self.next_button.disabled = (self.current_page == self.total_pages - 1)
            self.page_counter.label = f"Alert {self.current_page + 1}/{self.total_pages}"

        def create_embed(self):
            alert = self.alerts.feed.entries[self.current_page]

            embed = discord.Embed(
                title=alert.get("title", "No Title"),
                url=alert.get("link", "No Link"),
                description=alert.get("description", "No Description"),
                color=discord.Color.red()
            )
            embed.add_field(name="Published", value=alert.get("published", "No Published Date"), inline=False)
            embed.set_footer(text=f"Alert {self.current_page + 1} of {self.total_pages} • Source: OC Transpo")
            return embed

        @discord.ui.button(label="◀ Prev", style=discord.ButtonStyle.primary)
        async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

        @discord.ui.button(label="1/1", style=discord.ButtonStyle.secondary, disabled=True)
        async def page_counter(self, interaction: discord.Interaction, button: discord.ui.Button):
            pass

        @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
        async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

    # -- Helper to get the log channel --    
    async def get_log_channel(self) -> discord.TextChannel | None:
        ch = self.bot.get_channel(self.log_channel_id)
        if ch is None:
            try:
                ch = await self.bot.fetch_channel(self.log_channel_id)
            except Exception:
                return None
        return ch if isinstance(ch, discord.TextChannel) else None
    
    # -- Helper to log messages to the log channel --
    async def log(self, msg: str) -> None:
        ch = await self.get_log_channel()
        if ch:
            try:
                await ch.send(msg)
            except Exception:
                pass

    @app_commands.command(name="update", description="Check for status updates directly from OC Transpo")
    async def update(self, interaction: discord.Interaction, number: int = 5):
        await interaction.response.defer()

        # Pull the shard RSS store from the bot
        store = getattr(self.bot, "rss_store", None)
        if store is None:
            try:
                await interaction.followup.send("RSS store is not available.", ephemeral=True)
            except Exception as e:
                await self.log(f"Error sending RSS store not available message: {e}")
            return
        
        # Fetch snapshot
        try:
            snap = await store.get_snapshot()
        except Exception as e:
            try:
                await interaction.followup.send(f"Error fetching RSS snapshot: {e}", ephemeral=True)
            except Exception:
                await self.log(f"Error fetching RSS snapshot (notify failed): {e}")
            await self.log(f"Error fetching RSS snapshot: {e}")
            return
        
        if not snap.feed.entries:
            try:
                await interaction.followup.send("No updates found.", ephemeral=True)
            except Exception as e:
                await self.log(f"Error sending no updates found message: {e}")
            return
        
        view = self.AlertView(snap)
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view)
                    
async def setup(bot: commands.Bot):
    await bot.add_cog(QuerieCog(bot))