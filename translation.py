import gettext
import locale
import os


DEFAULT = 'en'


def get_current_locale(locale_path):
    current_locale, encoding = locale.getdefaultlocale()
    folder = current_locale
    folders = os.listdir(locale_path)
    if current_locale not in folders:
        r = [f for f in folders if folder.startswith(current_locale)]
        folder = r[0] if len(r) > 0 else DEFAULT
    return folder


def gettext_translation(
        domain, current_language=None, localedir='./locale'):
    LOCALE_DIR = localedir or './locale'
    CURRENT_LOCALE = current_language or get_current_locale(LOCALE_DIR)
    t = gettext.translation(
        domain,
        localedir=LOCALE_DIR,
        languages=[CURRENT_LOCALE]
    )
    return t.gettext
