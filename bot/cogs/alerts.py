import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import CommandTree, describe
from bot.routes.alerts import get_alerts

class AlertsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tree: CommandTree = bot.tree

    @app_commands.command(
        name="alerts",
        description="Get current alerts from OC Transpo"
    )
    @describe(
        route="Route number to filter by",
        category="Alert category (e.g. detour, general message)",
    )
    async def alerts(
        self,
        interaction: discord.Interaction,
        route: str = None,
        category: str = None
    ):
        await interaction.response.defer() #Incase the fuck ass API is slow :)
        # Call to API
        try:
            alerts_data = get_alerts()
        except Exception as e:
            return await interaction.followup.send(f"Failed to fetch alerts: {e}", ephemeral=True)
        
        alerts_list = list(alerts_data.values())

        # Filter alerts based on route and/or category
        if route:
            route_lower = route.strip().lower()
            alerts_list = [
                a for a in alerts_list
                if any(route_lower == r.lower() for r in a.get("affected_routes", []))
            ]
        if category:
            category_lower = category.strip().lower()
            alerts_list = [
                a for a in alerts_list
                if any(category_lower in c.lower() for c in a.get("categories", []))
            ]
        if not alerts_list:
            return await interaction.followup.send("No alerts found.", ephemeral=True)

        embeds = []
        embed = discord.Embed(title="OC Transpo Alerts", color=discord.Color.blue())
        embed.add_field(
            name="Filtering by",
            value=(
                (f"`Route: {route}` " if route else "") +
                (f"`Category: {category}`" if category else "")
            )
        )
        char_limit = 6000  # Discord embed total character limit
        field_limit = 25   # Discord embed field limit
        current_chars = sum(len(f.name) + len(f.value) for f in embed.fields)
        current_fields = len(embed.fields)

        for idx, alert in enumerate(alerts_list):
            # Prepare field values
            title = alert["title"]
            value = (
            f"• **Routes:** {', '.join(alert['affected_routes'])}\n"
            f"• **Categories:** {', '.join(alert['categories'])}\n"
            f"• {alert['summary']}\n"
            f"[Read more]({alert['link']})"
            )
            # Truncate value to 900 characters if necessary
            if len(value) > 900:
                value = value[:900] + "…"
            # Check if adding this field would exceed limits
            if (current_chars + len(title) + len(value) > char_limit) or (current_fields + 1 > field_limit):
                embeds.append(embed)
                embed = discord.Embed(title="OC Transpo Alerts (cont.)", color=discord.Color.blue())
                current_chars = 0
                current_fields = 0
            embed.add_field(name=title, value=value, inline=False)
            current_chars += len(title) + len(value)
            current_fields += 1
            
        # Add the last embed if it has fields
        if embed.fields:
            if len(alerts_list) > 5 and len(embeds) == 0:
                embed.set_footer(text=f"...and {len(alerts_list) - 5} more alerts.")
            embeds.append(embed)

        for e in embeds:
            await interaction.followup.send(embed=e)

async def setup(bot: commands.Bot):
    await bot.add_cog(AlertsCog(bot))