# telegram_doudizhu_bot/config.py
BOT_TOKEN = "YOUR_ACTUAL_TELEGRAM_BOT_TOKEN"
ADMIN_USER_IDS = [123456789, 987654321]  # Your Telegram User IDs
REQUIRED_GROUP_ID = 0      # Example: -1001234567890 (Must be integer, 0 or None means no requirement)
DATABASE_NAME = "doudizhu_bot.db"
DEFAULT_LANG = "zh_CN" # Default language: "en" or "zh_CN"

# Timeout settings (seconds)
BID_TIMEOUT_SECONDS = 60
PLAY_TIMEOUT_SECONDS = 75
JOIN_GAME_TIMEOUT_SECONDS = 300 # Game creation waiting for players

# Rate limiting settings
RATE_LIMIT_CALLS = 5
RATE_LIMIT_PERIOD = 10 # seconds

# Custom room settings defaults (can be overridden per game if implemented)
DEFAULT_ALLOW_THREE_ONE_PLANE = True
DEFAULT_ALLOW_FOUR_TWO_SINGLE = True
DEFAULT_ALLOW_FOUR_TWO_PAIR = True

# Logging
LOG_LEVEL = "INFO" # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "bot.log" # Optional: set to None to log only to console

# AI Player settings
AI_PLAYER_COUNT_TO_START_GAME = 1 # Min human players to start a game and fill with AI (if < 3)
# Max AI players: 3 - AI_PLAYER_COUNT_TO_START_GAME

# Number of top players in leaderboard
LEADERBOARD_TOP_N = 10
