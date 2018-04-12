import os
import shutil


DOMAIN = 'catalogmanager'
LOCALE_DIR = '../locale'
LOCALE_TMP_DIR = '../locale_tmp'

POT_FILE = '{}.pot'.format(DOMAIN)
APP_DIR = '../.'
LOCALES = ['en', 'es', 'pt', 'es_ES', 'pt_PT', ]

LANG_FOLDERS = [item for item in os.listdir(LOCALE_TMP_DIR) if '_' not in item]
COUNTRY_FOLDERS = [item for item in os.listdir(LOCALE_TMP_DIR) if '_' in item]


def po_file_path(locale, locale_dir=LOCALE_TMP_DIR):
    return os.path.join(locale_dir, locale, 'LC_MESSAGES', DOMAIN+'.po')


PO_FILES = {locale: po_file_path(locale) for locale in LOCALES}


def cmd_extract(file=POT_FILE):
    return 'pybabel extract -o {} {}'.format(file, APP_DIR)


def cmd_init(pot_file, locale='es'):
    return 'pybabel init -D {} -i {} -d {} -l {}'.format(
            DOMAIN,
            pot_file,
            LOCALE_TMP_DIR,
            locale
        )


def cmd_update(pot_file, locale='es'):
    return 'pybabel update -i {} -d {} -D {} -l {} --previous --ignore-obsolete'.format(
        POT_FILE,
        LOCALE_TMP_DIR,
        DOMAIN,
        locale
    )


def cmd_compile(po_file, locale):
    cmd = 'pybabel compile -D {} -d {} -i {} -l {} -f --statistics'.format(
            DOMAIN,
            LOCALE_TMP_DIR,
            po_file,
            locale
        )
    return cmd


def missing_translation(po_file):
    return open(po_file).read().count('msgstr ""')-1


def load(po_file):
    content = {}
    for item in open(po_file).readlines():
        item = item.strip()
        if item.startswith('msgid '):
            k = item
        elif item.startswith('msgstr '):
            content[k] = item
    return content


def merge(po_file1, po_file2, fixer):
    bkpfile = po_file2+'.bkp'
    shutil.copyfile(po_file2, bkpfile)
    origin = load(po_file1)
    dest = load(po_file2)
    for k, v in dest.items():
        if v == '':
            dest[k] = origin.get(k, '')

    new = []
    for item in open(po_file2).readlines():
        item = item.strip()
        if item.startswith('msgid '):
            k = item
            new.append(item)
        elif item.startswith('msgstr '):
            text = origin.get(k, '')
            if text == item:
                text = k.replace('msgid ', 'msgstr ')
            text = fix(text, fixer)
            new.append(text)
        else:
            new.append(item)

    open(po_file2, 'w').write('\n'.join(new))
    os.system(
        'diff -rup {} {} > {}.diff.txt'.format(
            bkpfile, po_file2, os.path.basename(po_file2)))


def init(pot_file=POT_FILE):
    for locale in LOCALES:
        cmd = cmd_init(pot_file, locale)
        if cmd is not None:
            os.system(cmd)


def update(pot_file=POT_FILE):
    q = 0
    for locale in LOCALES:
        os.system(cmd_update(pot_file, locale))

    auto = [
        ('en', 'pt', fixer_en_pt()),
        ('pt', 'pt_PT', fixer_pt_pt_PT()),
        ('pt_PT', 'es', fixer_pt_es()),
        ('es', 'es_ES', fixer_es_es_ES()),
    ]

    for locale1, locale2, fixer in auto:
        c1 = missing_translation(PO_FILES[locale1])
        if locale1 == 'en':
            c1 = 0
        c2 = missing_translation(PO_FILES[locale2])
        q = c1 + c2
        if c1 > 0:
            print('Revise {}'.format(PO_FILES[locale1]))
            print('Depois execute novamente a atualizacao')
            print('Faltam {} termos'.format(c1))
        elif c2 > 0:
            merge(PO_FILES[locale1], PO_FILES[locale2], fixer)
            print('Revise {}'.format(PO_FILES[locale2]))
            print('Depois execute novamente a atualizacao')
            print('Faltam {} termos'.format(c2))
        if q > 0:
            break
    if q == 0:
        print('Sem pendencias. Executar opcao C. ')
        return True


def fixer_es_es_ES():
    return [
        ('archivo', 'fichero'),
    ]


def fixer_pt_pt_PT():
    return [
        ('arquivo', 'ficheiro'),
    ]


def fixer_pt_es():
    return [
        ('ficheiro', 'archivo'),
        ('arquivo', 'archivo'),
        ('artigo', 'artículo'),
        ('Não', 'No'),
        ('não', 'no'),
        ('encontrado', 'se encontró'),
        (' o ', ' el '),
        (' os ', ' los '),
        ('ativo', 'activo'),
        (' do ', ' del '),
        ('O ', 'El '),
    ]


def fixer_en_pt():
    return [
        ('asset file', 'ativo digital'),
        ('file', 'arquivo'),
        ('Not found', 'Não encontrado'),
        ('article', 'artigo'),
        ('of the', 'do'),
        (' the ', ' o '),
        ('The ', 'O '),
        ('is not ', 'não está '),
        ('registered', 'registrado'),
    ]


def fix(text, fixer):
    for a, b in fixer:
        text = text.replace(a, b)
    return text


def compile():
    for locale in os.listdir(LOCALE_TMP_DIR):
        if os.path.isdir(os.path.join(LOCALE_TMP_DIR, locale)):
            po_file = po_file_path(locale)
            print('')
            os.system(cmd_compile(po_file, locale))
            mo_file = po_file.replace('.po', '.mo')
            mo_file2 = mo_file.replace(LOCALE_TMP_DIR, LOCALE_DIR)
            path = os.path.dirname(mo_file2)
            if not os.path.isdir(path):
                os.makedirs(path)
            shutil.copyfile(
                mo_file, mo_file2)
            print('Gerado {}'.format(mo_file2))
            print('')


reset = not os.path.isfile(POT_FILE)
os.system(cmd_extract(POT_FILE))
if reset:
    init()
r = update()
if r is True:
    compile()
