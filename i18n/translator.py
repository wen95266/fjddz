# telegram_doudizhu_bot/i18n/translator.py
import gettext
import os
from typing import Dict, Optional

# Assuming config.py is in the parent directory of i18n
# Correct path to config.py and locales directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    from config import DEFAULT_LANG
except ImportError:
    print("CRITICAL: config.py not found or DEFAULT_LANG not set. Falling back to 'en'.")
    DEFAULT_LANG = "en"


LOCALE_DIR = os.path.join(PROJECT_ROOT, 'i18n', 'locales')

loaded_translations: Dict[str, gettext.GNUTranslations] = {}

def get_translator(lang_code: Optional[str] = None) -> gettext.GNUTranslations:
    """
    Returns a gettext translation object for the given language code.
    Falls back to DEFAULT_LANG if the specified language is not found or if lang_code is None.
    """
    effective_lang_code = lang_code if lang_code else DEFAULT_LANG

    if effective_lang_code not in loaded_translations:
        try:
            # Ensure the domain 'bot' matches your .mo file names (e.g., bot.mo)
            translation = gettext.translation('bot', localedir=LOCALE_DIR, languages=[effective_lang_code], fallback=True)
            loaded_translations[effective_lang_code] = translation
        except FileNotFoundError:
            # This fallback might not be strictly necessary if gettext.translation handles it with fallback=True
            if effective_lang_code != DEFAULT_LANG:
                print(f"Warning: Language '{effective_lang_code}' .mo file not found. Falling back to '{DEFAULT_LANG}'.")
                return get_translator(DEFAULT_LANG) # Recursive call with default
            else:
                # If default language itself is not found, use NullTranslations
                print(f"Error: Default language '{DEFAULT_LANG}' .mo file not found. Using NullTranslations.")
                return gettext.NullTranslations() # No translations will occur
    return loaded_translations[effective_lang_code]

def _(text: str, lang_code: Optional[str] = None) -> str:
    """
    Translate the given text using the translator for the specified or default language.
    This is the primary function to be used for localization.
    Example: message = _("Hello, world!", user_specific_lang_code)
    """
    translator = get_translator(lang_code)
    return translator.gettext(text)

# You would need to generate .po and .mo files.
# Example .po file content (e.g., locales/zh_CN/LC_MESSAGES/bot.po):
#
# msgid ""
# msgstr ""
# "Project-Id-Version: DouDizhuBot 1.0\n"
# "Report-Msgid-Bugs-To: \n"
# "POT-Creation-Date: 2023-01-01 12:00+0000\n"
# "PO-Revision-Date: 2023-01-01 12:00+0000\n"
# "Last-Translator: Your Name <your.email@example.com>\n"
# "Language-Team: Chinese <language@example.com>\n"
# "Language: zh_CN\n"
# "MIME-Version: 1.0\n"
# "Content-Type: text/plain; charset=UTF-8\n"
# "Content-Transfer-Encoding: 8bit\n"
# "Plural-Forms: nplurals=1; plural=0;\n"
#
# msgid "Welcome to Dou Dizhu Bot! Use /newgame to start a game."
# msgstr "欢迎来到斗地主机器人！使用 /newgame 开始一个新游戏。"
#
# msgid "Your hand: {}"
# msgstr "你的手牌: {}"
#
# To compile .po to .mo:
# pybabel compile -d locales -D bot
# (Assumes you have 'bot.po' files and Babel installed)
