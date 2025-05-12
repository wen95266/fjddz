# telegram_doudizhu_bot/constants.py

# Card Ranks (ordered by value for sorting internally, not display order)
# Actual display value might be different (e.g. '10' vs 'T')
# Numerical values allow easy comparison.
RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8, RANK_9, RANK_10, RANK_J, RANK_Q, RANK_K, RANK_A, RANK_2, RANK_BLACK_JOKER, RANK_RED_JOKER = range(15)

RANK_ORDER_MAP_INTERNAL_TO_DISPLAY = {
    RANK_3: '3', RANK_4: '4', RANK_5: '5', RANK_6: '6', RANK_7: '7',
    RANK_8: '8', RANK_9: '9', RANK_10: '10', RANK_J: 'J', RANK_Q: 'Q',
    RANK_K: 'K', RANK_A: 'A', RANK_2: '2',
    RANK_BLACK_JOKER: 'BJ', RANK_RED_JOKER: 'RJ'
}
RANK_DISPLAY_TO_INTERNAL_MAP = {v: k for k, v in RANK_ORDER_MAP_INTERNAL_TO_DISPLAY.items()}

# Card Suits (mostly for uniqueness of 52 cards, less critical for DouDizhu logic)
SUIT_SPADES, SUIT_HEARTS, SUIT_CLUBS, SUIT_DIAMONDS, SUIT_JOKER = range(5)
SUIT_DISPLAY_MAP = {
    SUIT_SPADES: "♠", SUIT_HEARTS: "♥", SUIT_CLUBS: "♣", SUIT_DIAMONDS: "♦", SUIT_JOKER: ""
}
# Used for creating unique card IDs if needed, or parsing full card strings
SUIT_CHAR_TO_INTERNAL_MAP = {"S": SUIT_SPADES, "H": SUIT_HEARTS, "C": SUIT_CLUBS, "D": SUIT_DIAMONDS}


# Game Phases
PHASE_WAITING_FOR_PLAYERS = "waiting_players"
PHASE_BIDDING = "bidding"
PHASE_PLAYING = "playing"
PHASE_GAME_OVER = "game_over"

# Player Roles
ROLE_FARMER = "farmer"
ROLE_LANDLORD = "landlord"

# Callback Data Prefixes (to identify button actions)
CALLBACK_JOIN_GAME = "join"
CALLBACK_START_GAME_MANUALLY = "start_man" # If admin wants to start with <3 players + AI
CALLBACK_BID_PREFIX = "bid_" # e.g., bid_1, bid_2, bid_3, bid_pass
CALLBACK_SELECT_CARD_PREFIX = "selcard_" # e.g., selcard_RJ, selcard_H_3 (Suit_Rank)
CALLBACK_PLAY_SELECTED_CARDS = "playcards"
CALLBACK_PASS_TURN = "pass"
CALLBACK_RESET_SELECTION = "reset_sel"
CALLBACK_PLAY_AGAIN = "play_again"
CALLBACK_VIEW_RULES_PAGE_PREFIX = "rulespg_"
CALLBACK_CHANGE_LANG_PREFIX = "setlang_"
CALLBACK_CONFIRM_ACTION_PREFIX = "confirm_" # Generic confirm prefix

# Hand Types (ensure these match strings used in hand_rules.py)
TYPE_INVALID = "invalid"
TYPE_SINGLE = "single"
TYPE_PAIR = "pair"
TYPE_TRIO = "trio"
TYPE_TRIO_PLUS_ONE = "trio_plus_one"
TYPE_TRIO_PLUS_PAIR = "trio_plus_pair" # Full House
TYPE_STRAIGHT = "straight" # 5+ cards
TYPE_DOUBLE_STRAIGHT = "double_straight" # 3+ pairs, LianDui
TYPE_TRIPLE_STRAIGHT = "triple_straight" # aka airplane (body only), FeiJi
TYPE_TRIPLE_STRAIGHT_PLUS_SINGLES = "triple_straight_plus_singles" # airplane with small wings
TYPE_TRIPLE_STRAIGHT_PLUS_PAIRS = "triple_straight_plus_pairs" # airplane with large wings
TYPE_QUAD_PLUS_TWO_SINGLES = "quad_plus_two_singles" # SiDaiErDan
TYPE_QUAD_PLUS_TWO_PAIRS = "quad_plus_two_pairs" # SiDaiLiangDui
TYPE_BOMB = "bomb" # Four of a kind
TYPE_ROCKET = "rocket" # Black Joker + Red Joker

# Minimum lengths for sequences
MIN_STRAIGHT_LEN = 5
MIN_DOUBLE_STRAIGHT_LEN = 3 # e.g., 334455 (3 pairs)
MIN_TRIPLE_STRAIGHT_LEN = 2 # e.g., 333444 (2 trios)

# Job Queue Context Keys/Names for timeouts (must be unique)
JOB_TYPE_BID = "job_bid_timeout"
JOB_TYPE_PLAY = "job_play_timeout"
JOB_TYPE_JOIN = "job_join_timeout"

# Points/Score multipliers
SCORE_BASE = 1 # Base score for a win/loss
SCORE_MULTIPLIER_BOMB = 2
SCORE_MULTIPLIER_ROCKET = 2 # Or higher if desired
SCORE_MULTIPLIER_SPRING = 2 # Landlord plays all cards, farmers play none
SCORE_MULTIPLIER_ANTI_SPRING = 2 # Farmer plays all cards, landlord plays only one hand (or none after first)
