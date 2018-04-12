import os
import shutil


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))


class PO_File:

    def __init__(self, po_file):
        self.po_file = po_file
        self.load()

    def count(self):
        if '/en/' in self.po_file:
            return 0
        return open(self.po_file).read().count('msgstr ""')-1

    def load(self):
        self.terms = {}
        for item in open(self.po_file).readlines():
            item = item.strip()
            if item.startswith('msgid '):
                k = item
            elif item.startswith('msgstr '):
                self.terms[k] = item

    def merge(self, origin, fixer):
        bkpfile = self.po_file+'.bkp'
        shutil.copyfile(self.po_file, bkpfile)

        new = []
        for item in open(self.po_file).readlines():
            item = item.strip()
            if item.startswith('msgid '):
                k = item
                new.append(item)
            elif item.startswith('msgstr '):
                text = self.items.get(k, '')
                if text == item:
                    text = k.replace('msgid ', 'msgstr ')
                text = fix(text, fixer)
                new.append(text)
            else:
                new.append(item)

        open(self.po_file, 'w').write('\n'.join(new))
        os.system(
            'diff -rup {} {} > {}.diff.txt'.format(
                bkpfile, _dest_file, os.path.basename(_dest_file)))


class LocaleCreator:

    def __init__(self, domain, app_dir, app_locale_dir):
        self.LOCALES = ['en', 'es', 'pt', 'es_ES', 'pt_PT', ]
        self.domain = domain
        self.app_dir = app_dir
        self.app_locale_dir = app_locale_dir

        self.pot_file = os.path.join(
            CURRENT_PATH, 'tmp', domain, domain+'.pot')
        self.locale_dir = os.path.join(
            CURRENT_PATH, 'tmp', domain, 'locale')

        self.po_file_paths = {
            locale: self.po_file_path(locale)
            for locale in self.LOCALES
        }
        self.PO_FILES = {
            locale: PO_File(f)
            for locale, f in self.po_file_paths.items()
        }

    def po_file_path(self, locale):
        return os.path.join(
            self.locale_dir,
            locale,
            'LC_MESSAGES',
            self.domain+'.po'
        )

    def extract(self):
        os.system(
            'pybabel extract -o {} {}'.format(self.pot_file, self.app_dir))

    def init(self):
        for locale in self.LOCALES:
            cmd = 'pybabel init -D {} -i {} -d {} -l {}'.format(
                self.domain,
                self.pot_file,
                self.locale_dir,
                locale
            )
            os.system(cmd)

    def update_locale(self, locale):
        cmd = 'pybabel update -i {} -d {} -D {} -l {} --previous --ignore-obsolete'.format(
            self.pot_file,
            self.locale_dir,
            self.domain,
            locale
        )
        os.system(cmd)

    def compile_locale(self, locale):
        cmd = 'pybabel compile -D {} -d {} -i {} -l {} -f --statistics'.format(
                self.domain,
                self.locale_dir,
                self.po_file_paths.get(locale),
                locale
            )
        os.system(cmd)

    def compile(self):
        for locale in self.LOCALES:
            po_file = self.po_file_paths.get(locale)
            print('\n=====\n')
            self.compile_locale(locale)
            mo_file = po_file.replace('.po', '.mo')
            path = os.path.dirname(mo_file)
            if not os.path.isdir(path):
                os.makedirs(path)
            print('  Gerado {}'.format(mo_file))
            print('\n=====\n')




def update(pot_file=self.pot_file):
    q = 0
    for locale in self.LOCALES:
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




reset = not os.path.isfile(self.pot_file)
os.system(cmd_extract(self.pot_file))
if reset:
    init()
r = update()
if r is True:
    compile()
