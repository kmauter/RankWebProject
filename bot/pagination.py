"""Pagination utilities for Discord embeds.

Provides a View with Previous/Next buttons for navigating through
multiple embed pages. Used when results or comments exceed Discord's
embed character limits.
"""

from __future__ import annotations

import discord


class PaginatedView(discord.ui.View):
    """A view with Previous/Next buttons for paginating embeds.

    Args:
        pages: List of discord.Embed objects to paginate through.
        author_id: The user ID who triggered the command (only they can navigate).
        timeout: How long the buttons stay active (seconds). Default 120.
    """

    def __init__(
        self,
        pages: list[discord.Embed],
        author_id: int,
        timeout: float = 120.0,
    ) -> None:
        super().__init__(timeout=timeout)
        self.pages = pages
        self.author_id = author_id
        self.current_page = 0
        self._update_buttons()

    def _update_buttons(self) -> None:
        """Enable/disable buttons based on current page position."""
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= len(self.pages) - 1

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Go to the previous page."""
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the person who ran this command can navigate.",
                ephemeral=True,
            )
            return

        self.current_page -= 1
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.pages[self.current_page], view=self
        )

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        """Go to the next page."""
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the person who ran this command can navigate.",
                ephemeral=True,
            )
            return

        self.current_page += 1
        self._update_buttons()
        await interaction.response.edit_message(
            embed=self.pages[self.current_page], view=self
        )

    async def on_timeout(self) -> None:
        """Disable all buttons when the view times out."""
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True


def paginate_embed_fields(
    base_embed: discord.Embed,
    items: list[tuple[str, str]],
    per_page: int = 10,
) -> list[discord.Embed]:
    """Split items into multiple embed pages.

    Args:
        base_embed: The base embed to clone for each page (title, color, etc.)
        items: List of (field_name, field_value) tuples to distribute across pages.
        per_page: Maximum number of fields per page.

    Returns:
        List of embed pages. If items fit in one page, returns a single embed.
    """
    if not items:
        return [base_embed]

    pages: list[discord.Embed] = []
    total_pages = (len(items) + per_page - 1) // per_page

    for page_num in range(total_pages):
        start = page_num * per_page
        end = start + per_page
        page_items = items[start:end]

        embed = discord.Embed(
            title=base_embed.title,
            description=base_embed.description,
            color=base_embed.color,
        )

        for name, value in page_items:
            embed.add_field(name=name, value=value, inline=False)

        if total_pages > 1:
            embed.set_footer(text=f"Page {page_num + 1}/{total_pages}")

        pages.append(embed)

    return pages
