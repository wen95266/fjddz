# telegram_doudizhu_bot/utils/helpers.py
from typing import List, Optional, Tuple

from telegram import Update
from telegram.ext import ContextTypes

try:
    from config import ADMIN_USER_IDS, REQUIRED_GROUP_ID, DEFAULT_LANG
except ImportError:
    print("CRITICAL: config.py not found in utils.helpers.py. Using fallback defaults.")
    ADMIN_USER_IDS = []
    REQUIRED_GROUP_ID = 0
    DEFAULT_LANG = "en"

from game_logic.card import Card # Assuming Card class is defined
from game_logic.player import Player # Assuming Player class
from game_logic.game_state import GameState # Assuming GameState class
# from game_manager import GameManager # Careful with circular imports if GameManager also imports this

def get_user_lang(context: ContextTypes.DEFAULT_TYPE, user_id: Optional[int] = None) -> str:
    """Gets the user's preferred language from context.user_data, fallback to DEFAULT_LANG."""
    if user_id and 'users_lang' in context.bot_data and user_id in context.bot_data['users_lang']:
        return context.bot_data['users_lang'][user_id]
    if 'lang' in context.user_data: # Check current user's context first
        return context.user_data['lang']
    return context.bot_data.get("config", {}).get("DEFAULT_LANG", DEFAULT_LANG)

def get_chat_lang(context: ContextTypes.DEFAULT_TYPE, chat_id: Optional[int] = None) -> str:
    """Gets the chat's preferred language from context.chat_data, fallback to DEFAULT_LANG."""
    if chat_id and 'chats_lang' in context.bot_data and chat_id in context.bot_data['chats_lang']:
        return context.bot_data['chats_lang'][chat_id]
    if 'lang' in context.chat_data: # Check current chat's context
        return context.chat_data['lang']
    return context.bot_data.get("config", {}).get("DEFAULT_LANG", DEFAULT_LANG)


def is_user_admin(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks if a user_id is in the admin list."""
    admin_list = context.bot_data.get("config", {}).get("ADMIN_USER_IDS", ADMIN_USER_IDS)
    return user_id in admin_list

async def check_group_membership_and_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Checks if the user is a member of the REQUIRED_GROUP_ID.
    Replies to the user if they are not a member.
    Returns True if member (or no group required, or admin), False otherwise.
    """
    user = update.effective_user
    if not user:
        return False # Should not happen

    user_lang = get_user_lang(context, user.id)
    
    # Get current REQUIRED_GROUP_ID, allowing for dynamic changes through bot_data
    current_required_group_id = context.bot_data.get("db_config", {}).get("REQUIRED_GROUP_ID")
    if current_required_group_id is None: # Fallback to hardcoded config if not in db_config
        current_required_group_id = context.bot_data.get("config", {}).get("REQUIRED_GROUP_ID", REQUIRED_GROUP_ID)

    if not current_required_group_id or current_required_group_id == 0:
        return True # No group requirement set

    if is_user_admin(user.id, context):
        return True # Admins bypass this check

    try:
        member = await context.bot.get_chat_member(chat_id=current_required_group_id, user_id=user.id)
        if member.status not in ['member', 'administrator', 'creator']:
            # User is not in the group or has left/been banned
            from i18n.translator import _ # Local import
            # Try to get group info for a more helpful message
            group_name_or_link = str(current_required_group_id)
            try:
                chat_info = await context.bot.get_chat(current_required_group_id)
                if chat_info.invite_link:
                    group_name_or_link = f"[{chat_info.title}]({chat_info.invite_link})"
                elif chat_info.title:
                    group_name_or_link = chat_info.title
            except Exception:
                pass # Stick with ID if fetching info fails

            await update.message.reply_text(
                _(("You must be a member of our designated group to use this command.\n"
                   "Please join: {}"), user_lang).format(group_name_or_link),
                parse_mode='Markdown'
            )
            return False
    except Exception as e: # Bot not in group, user not found, etc.
        from i18n.translator import _ # Local import
        print(f"Error checking group membership for user {user.id} in group {current_required_group_id}: {e}")
        await update.message.reply_text(
            _("Could not verify your group membership. The bot might not be in the required group, or an error occurred. Please contact an admin.", user_lang)
        )
        return False
    return True

def format_cards_for_display(cards: List[Card], separator: str = ", ") -> str:
    """Converts a list of Card objects to a displayable string."""
    if not cards:
        return ""
    return separator.join(str(card) for card in sorted(cards)) # DouDizhu hands usually sorted

def get_player_and_game(
    game_manager, # Pass Game Manager instance
    chat_id: int,
    user_id: int
) -> Tuple[Optional[Player], Optional[GameState]]:
    """Convenience function to get current player and game."""
    game = game_manager.get_game(chat_id)
    if not game:
        return None, None
    player = game.get_player(user_id)
    if not player:
        return None, game
    return player, game

def get_job_name(job_type: str, chat_id: int, user_id: Optional[int] = None) -> str:
    """Creates a unique job name for APScheduler based on type, chat, and optionally user."""
    if user_id:
        return f"{job_type}_{chat_id}_{user_id}"
    return f"{job_type}_{chat_id}"

def format_leaderboard_display(leaderboard_data: List[dict], lang: str, bot_username: str) -> str:
    from i18n.translator import _ # Local import
    if not leaderboard_data:
        return _("The leaderboard is empty right now!", lang)

    header = _("🏆 **Dou Dizhu Leaderboard** 🏆\n\n", lang)
    table_header = "| " + _("Rank", lang) + " | " + _("Player", lang) + \
                   " | " + _("Wins", lang) + " | " + _("Played", lang) + \
                   " | " + _("Score", lang) + " |\n"
    table_sep =    "|:----:|:-----------|:------:|:--------:|:-------:|\n"
    
    rows = []
    for i, entry in enumerate(leaderboard_data):
        player_name = entry.get('username', str(entry.get('user_id', 'Unknown')))
        # Make username clickable if it's not the bot itself and starts with @
        if not player_name.startswith('@') and player_name != bot_username :
            player_name_display = f"[{player_name}](tg://user?id={entry.get('user_id')})"
        else:
            player_name_display = player_name

        row_str = f"| {i+1:^4} | {player_name_display:<11} | {entry.get('games_won', 0):^6} | " \
                  f"{entry.get('games_played', 0):^8} | {entry.get('total_score', 0):^7} |"
        rows.append(row_str)

    return header + table_header + table_sep + "\n".join(rows)

def get_bot_username(context: ContextTypes.DEFAULT_TYPE) -> str:
    if "bot_username" not in context.bot_data:
        context.bot_data["bot_username"] = context.bot.username
    return context.bot_data["bot_username"]
