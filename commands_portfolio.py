"""Portfolio analytics and visualization."""
import discord
from discord import app_commands
from discord.ext import commands
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import database
import market
import utils
import config
import team_detection


class PortfolioCommands(commands.Cog):
    """Commands for portfolio analytics."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="portfolio", description="View your portfolio with analytics")
    async def portfolio(self, interaction: discord.Interaction):
        """Detailed portfolio analysis with graphs."""
        await interaction.response.defer()
        
        try:
            # Get portfolio
            portfolio = await database.get_portfolio(interaction.user.id)
            balance = await database.get_balance(interaction.user.id)
            
            if not portfolio:
                await interaction.followup.send("📊 Your portfolio is empty", ephemeral=True)
                return
            
            # Calculate values
            total_invested = 0
            current_value = 0
            holdings_data = []
            
            for holding in portfolio:
                symbol = holding['symbol']
                shares = holding['shares']
                avg_cost = holding['avg_cost']
                
                current_price = await market.market.get_price(symbol)
                if not current_price:
                    continue
                
                invested = avg_cost * shares
                value = current_price * shares
                pl = value - invested
                pl_pct = (pl / invested * 100) if invested > 0 else 0
                
                total_invested += invested
                current_value += value
                
                holdings_data.append({
                    'symbol': symbol,
                    'shares': shares,
                    'avg_cost': avg_cost,
                    'current_price': current_price,
                    'invested': invested,
                    'value': value,
                    'pl': pl,
                    'pl_pct': pl_pct
                })
            
            # Total P/L
            total_pl = current_value - total_invested
            total_pl_pct = (total_pl / total_invested * 100) if total_invested > 0 else 0
            total_value_with_cash = current_value + balance
            
            # Generate pie chart
            chart_path = await self._generate_portfolio_chart(holdings_data, balance)
            
            # Create embed
            embed = discord.Embed(
                title=f"📊 {interaction.user.display_name}'s Portfolio",
                color=discord.Color.green() if total_pl >= 0 else discord.Color.red()
            )
            
            # Summary
            pl_emoji = "📈" if total_pl >= 0 else "📉"
            pl_sign = "+" if total_pl >= 0 else ""
            
            summary = f"**Total Value:** {utils.spurs_to_cogs_display(total_value_with_cash)}\n"
            summary += f"**Stocks:** {utils.spurs_to_cogs_display(current_value)}\n"
            summary += f"**Cash:** {utils.spurs_to_cogs_display(balance)}\n"
            summary += f"**Invested:** {utils.spurs_to_cogs_display(total_invested)}\n"
            summary += f"{pl_emoji} **P/L:** {pl_sign}{utils.spurs_to_cogs_display(total_pl)} ({pl_sign}{total_pl_pct:.1f}%)"
            
            embed.add_field(name="Summary", value=summary, inline=False)
            
            # Top 3 holdings
            holdings_data.sort(key=lambda x: x['value'], reverse=True)
            holdings_text = ""
            for h in holdings_data[:3]:
                team_name = team_detection.get_team_name(h['symbol'])
                pl_emoji = "🟢" if h['pl'] >= 0 else "🔴"
                pl_sign = "+" if h['pl'] >= 0 else ""
                holdings_text += f"{pl_emoji} **{h['symbol']}** - {team_name}\n"
                holdings_text += f"  {h['shares']:,} × {utils.spurs_to_cogs_display(h['current_price'])} = {utils.spurs_to_cogs_display(h['value'])}\n"
                holdings_text += f"  P/L: {pl_sign}{utils.spurs_to_cogs_display(h['pl'])} ({pl_sign}{h['pl_pct']:.1f}%)\n\n"
            
            embed.add_field(name="Top Holdings", value=holdings_text or "None", inline=False)
            
            # Set chart
            embed.set_image(url=f'attachment://portfolio_chart.png')
            embed.set_footer(text="Use /history to view trade history")
            
            # Send
            file = discord.File(chart_path, filename='portfolio_chart.png')
            await interaction.followup.send(embed=embed, file=file)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    async def _generate_portfolio_chart(self, holdings_data, balance):
        """Generate portfolio distribution pie chart."""
        os.makedirs(config.GRAPH_DIR, exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
        fig.patch.set_facecolor('#0B0E11')
        ax.set_facecolor('#131722')
        
        # Data
        labels = []
        sizes = []
        colors = ['#26A69A', '#EF5350', '#5865F2', '#FEE75C', '#57F287', '#EB459E']
        
        for i, h in enumerate(holdings_data[:5]):  # Top 5
            team_name = team_detection.get_team_name(h['symbol'])
            labels.append(f"{h['symbol']}\n{utils.spurs_to_cogs_display(h['value'])}")
            sizes.append(h['value'])
        
        if balance > 0:
            labels.append(f"Cash\n{utils.spurs_to_cogs_display(balance)}")
            sizes.append(balance)
        
        # Plot
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors[:len(sizes)],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'color': '#C9D1D9', 'fontsize': 10}
        )
        
        for autotext in autotexts:
            autotext.set_color('#0B0E11')
            autotext.set_fontweight('bold')
        
        ax.set_title('Portfolio Distribution', color='#C9D1D9', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        output_path = os.path.join(config.GRAPH_DIR, 'portfolio_chart.png')
        plt.savefig(output_path, dpi=100, bbox_inches='tight', facecolor='#0B0E11')
        plt.close(fig)
        
        return output_path


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(PortfolioCommands(bot))
