# telegram_doudizhu_bot/utils/decorators.py
from functools import wraps
import time
from typing import Callable, Dict, List, Any, Coroutine

from telegram import Update
from telegram.ext import ContextTypes

from i18n.translator import _
from utils.helpers import get_user_lang, is_user_admin, check_group_membership_and_reply

# Store last call times for rate limiting (user_id -> list of timestamps)
# This should ideally be in context.bot_data for persistence across restarts if needed,
# or handled by a more robust rate-limiting library. For simplicity, module-level dict.
user_call_times: Dict[int, List[float]] = {}


def admin_command(func: Callable[..., Coroutine[Any, Any, Any]]):
    """Decorator to restrict a command handler to admins only."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        user_lang = get_user_lang(context, user.id if user else None)
        if not user or not is_user_admin(user.id, context):
            if update.message:
                await update.message.reply_text(_("⛔ Access denied. This command is for admins only.", user_lang))
            elif update.callback_query:
                await update.callback_query.answer(_("⛔ Access denied. Admin only.", user_lang), show_alert=True)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def group_member_command(func: Callable[..., Coroutine[Any, Any, Any]]):
    """Decorator to ensure user is member of REQUIRED_GROUP_ID for a command."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not await check_group_membership_and_reply(update, context):
            return # Reply is handled by the check function
        return await func(update, context, *args, **kwargs)
    return wrapper


def rate_limit_command(
    calls: int = None, # Max calls. Uses config if None.
    period: int = None # Per X seconds. Uses config if None.
):
    """
    Decorator to rate limit a command handler per user.
    Uses values from config.py if not specified in decorator args.
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = update.effective_user
            if not user: # Should not happen for most handlers
                return await func(update, context, *args, **kwargs)

            user_lang = get_user_lang(context, user.id)
            
            # Get rate limit settings from bot_data (config) or use decorator args
            _calls = calls if calls is not None else context.bot_data.get("config", {}).get("RATE_LIMIT_CALLS", 5)
            _period = period if period is not None else context.bot_data.get("config", {}).get("RATE_LIMIT_PERIOD", 10)

            current_time = time.time()
            if user.id not in user_call_times:
                user_call_times[user.id] = []

            # Remove timestamps older than the period
            user_call_times[user.id] = [t for t in user_call_times[user.id] if t > current_time - _period]

            if len(user_call_times[user.id]) >= _calls:
                # User has exceeded the rate limit
                if update.message:
                    await update.message.reply_text(
                        _("⏳ You are sending commands too quickly. Please wait a moment.", user_lang)
                    )
                elif update.callback_query:
                    await update.callback_query.answer(
                        _("⏳ Too many requests. Please wait.", user_lang), show_alert=True
                    )
                return

            user_call_times[user.id].append(current_time)
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def game_command( # A meta-decorator for commands that require an active game
    require_game_phase: Optional[List[str]] = None, # e.g. [PHASE_PLAYING]
    require_player_turn: bool = False,
    allow_spectators: bool = False # If true, non-players can use the command (e.g. /gamestatus)
):
    """
    Decorator for command handlers that operate on an active game.
    Checks for active game, optionally specific phase, and if it's player's turn.
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            chat_id = update.effective_chat.id
            user = update.effective_user
            user_id = user.id if user else None
            user_lang = get_user_lang(context, user_id)
            
            game_manager = context.bot_data.get("game_manager")
            if not game_manager:
                # This is a critical setup error
                print("CRITICAL: GameManager not found in context.bot_data")
                if update.message: await update.message.reply_text(_("Bot error: Game service unavailable.", user_lang))
                elif update.callback_query: await update.callback_query.answer(_("Bot error.", user_lang), show_alert=True)
                return

            game = game_manager.get_game(chat_id)
            if not game:
                if update.message: await update.message.reply_text(_("No active game in this chat. Start one with /newgame.", user_lang))
                elif update.callback_query: await update.callback_query.answer(_("No active game.", user_lang), show_alert=True)
                return

            player = game.get_player(user_id) if user_id else None
            if not player and not allow_spectators and require_game_phase: # If needs phase, usually needs player
                if update.message: await update.message.reply_text(_("You are not part of the current game.", user_lang))
                elif update.callback_query: await update.callback_query.answer(_("Not in game.", user_lang), show_alert=True)
                return
            
            if require_game_phase and game.phase not in require_game_phase:
                # Example: Trying to /play when game is in PHASE_BIDDING
                phases_str = ", ".join([_(p, user_lang) for p in require_game_phase])
                msg = _("This action is only allowed during game phase(s): {}.", user_lang).format(phases_str)
                if update.message: await update.message.reply_text(msg)
                elif update.callback_query: await update.callback_query.answer(msg, show_alert=True)
                return

            if require_player_turn:
                if not player: # Should have been caught above if not allow_spectators
                    if update.message: await update.message.reply_text(_("You are not part of this game.", user_lang))
                    elif update.callback_query: await update.callback_query.answer(_("Not in game.", user_lang), show_alert=True)
                    return
                
                current_player_in_game = game.get_current_player() if game.phase == "playing" else game.get_current_bidder()
                if not current_player_in_game or current_player_in_game.user_id != user_id:
                    msg = _("It's not your turn.", user_lang)
                    if update.message: await update.message.reply_text(msg)
                    elif update.callback_query: await update.callback_query.answer(msg, show_alert=True)
                    return
            
            # Pass game and player objects to the handler if needed
            kwargs['game'] = game
            kwargs['player'] = player
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator
