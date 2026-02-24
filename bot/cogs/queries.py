# User facing commands
from discord.ext import commands
from discord import app_commands
import discord
import os

from bot.util.filter_rss import filter_alerts

from bot.util.discord_helpers import log_to_channel


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_dir = os.path.join(root_dir, "data")

class QuerieCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    class AlertView(discord.ui.View):
        def __init__(self, alerts):
            super().__init__(timeout=300)
            self.alerts = alerts
            self.current_page = 0
            self.total_pages = len(alerts)
            self.update_buttons()
            

        def update_buttons(self):
            self.prev_button.disabled = (self.current_page == 0)
            self.next_button.disabled = (self.current_page == self.total_pages - 1)
            self.page_counter.label = f"Alert {self.current_page + 1}/{self.total_pages}"

        def create_embed(self):
            try:
                alert = self.alerts[self.current_page]

                # ADD NEW FIELDS AS NEEDED
                # VIEW UPDATE COMMAND IN THIS COG FOR MORE INFO
                embed = discord.Embed(
                    title=alert.get("title", "No Title"),
                    url=alert.get("link", "No Link"),
                    description=alert.get("description", "No Description") + "\n\n" +
                                f"Routes: {', '.join(alert.get('routes', set()))}\n" +
                                f"Stops: {', '.join(alert.get('stops', set()))}\n" +
                                f"Categories: {', '.join(alert.get('categories', set()))}",
                    color=discord.Color.red()
                )
                embed.add_field(name="Published", value=alert.get("published", "No Published Date"), inline=False)
                embed.set_footer(text=f"Alert {self.current_page + 1} of {self.total_pages} • Source: OC Transpo")
                return embed
            except IndexError:
                self.prev_button.disabled = True
                self.next_button.disabled = True
                self.page_counter.label = "No Alerts"
                return discord.Embed(
                    title="No Alert",
                    description="No alert information is available.",
                    color=discord.Color.red()
                )

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

    # -- Helper to log messages to the log channel --
    async def log(self, msg: str) -> None:
        await log_to_channel(self.bot, msg)

    @app_commands.command(name="update", description="Check for status updates directly from OC Transpo")
    @app_commands.describe(
        category="Alert category (Detours, Service Updates, etc.)",
        route="Route number (e.g. 90)",
        stop="Stop name or ID (e.g. Rideau or 3025)",
        since_hours="How many hours back",
        limit="Max alerts needed",)
    async def update(
        self,  
        interaction: discord.Interaction,
        category: str | None = None,
        route: str | None = None,
        stop: str | None = None,
        since_hours: int | None = None,
        limit: int | None = None,):
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


        # NEW VERSION OF THE ALERT DISPLAY USING THE VIEW
        # ADD TO EMBED CONFIG
            #    title = entry.get("title", "No Title")
            #    link = entry.get("link", "No Link")
            #    description = entry.get("description", "No Description")
            #    published = entry.get("published", "No Published Date")
            #    routes = entry.get("routes", set())
            #    stops = entry.get("stops", set())
            #    categories = entry.get("categories", set())
            #    updates.append(f"**{title}**\nPublished: {published}\nDescription: {description}\nLink: {link}\nRoutes: {', '.join(routes)}\nStops: {', '.join(stops)}\nCategories: {', '.join(categories)}\n")

        # Call filter_alerts(snap.feed.entries, category=category, route=route, stop=stop, since=since, limit=limit) to filter/sort the entries
        # Returns a list of entries
        filtered_entries = filter_alerts(snap.feed.entries, category=category, route=route, stop=stop, since=since_hours, limit=limit)
        
        
        view = self.AlertView(filtered_entries)
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(QuerieCog(bot))