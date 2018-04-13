# coding=utf-8

import os
import shutil


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))


def short_path(f):
    return f.replace(CURRENT_PATH, '.')


def print_path(f):
    print(short_path(f))


class PO_File:

    def __init__(self, po_file):
        self.po_file = po_file
        self.load()

    @property
    def count(self):
        if '/en/' in self.po_file:
            return 0
        if os.path.isfile(self.po_file):
            c = open(self.po_file).read().count('msgstr ""')-1
            return c
        return 0

    def load(self):
        self.terms = {}
        if os.path.isfile(self.po_file):
            for item in open(self.po_file).readlines():
                item = item.strip()
                if item.startswith('msgid '):
                    MSGID = item
                elif item.startswith('msgstr '):
                    self.terms[MSGID] = item
                    if '/en/' in self.po_file:
                        self.terms[MSGID] = MSGID.replace('msgid ', 'msgstr ')

    def merge(self, origin, fixer):
        # bkpfile = self.po_file+'.bkp'
        # shutil.copyfile(self.po_file, bkpfile)

        new = []
        for item in open(self.po_file).readlines():
            item = item.strip()
            if item.startswith('msgid '):
                k = item
                new.append(item)
            elif item.startswith('msgstr '):
                translation = origin.terms.get(k)
                if translation is None:
                    print('Not found transl:' + k)
                else:
                    item = translation
                    for a, b in fixer:
                        item = item.replace(a, b)
                new.append(item)
            else:
                new.append(item)

        open(self.po_file, 'w').write('\n'.join(new))


class LocaleCreator:

    def __init__(self, app_locale_dir):
        self.LOCALES = ['en', 'es', 'pt', 'es_ES', 'pt_PT', ]
        self.app_locale_dir = app_locale_dir
        self.app_dir = os.path.dirname(app_locale_dir)
        self.domain = os.path.basename(self.app_dir)

        self.pot_file = os.path.join(
            CURRENT_PATH, 'tmp', self.domain, self.domain+'.pot')
        self.tmp_locale_dir = os.path.join(
            CURRENT_PATH, 'tmp', self.domain, 'locale')

        self.po_file_paths = {
            locale: self.po_file_path(locale)
            for locale in self.LOCALES
        }
        self.PO_FILES = {
            locale: PO_File(f)
            for locale, f in self.po_file_paths.items()
        }

    @property
    def app_locale_files(self):
        files = []
        if os.path.isdir(self.app_locale_dir):
            for (dirpath, dirnames, filenames) in os.walk(self.app_locale_dir):
                for file in filenames:
                    files.append(os.path.join(dirpath, file))
        return files

    def copy_locale_dir(self):
        for f in self.app_locale_files:
            new = f.replace(self.app_locale_dir, self.tmp_locale_dir)
            dirname = os.path.dirname(new)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            shutil.copyfile(f, new)

    def po_file_path(self, locale):
        return os.path.join(
            self.tmp_locale_dir,
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
                self.tmp_locale_dir,
                locale
            )
            os.system(cmd)

    def update_locale(self, locale):
        cmd = 'pybabel update -i {} -d {} -D {} -l {} --previous --ignore-obsolete'.format(
            self.pot_file,
            self.tmp_locale_dir,
            self.domain,
            locale
        )
        os.system(cmd)

    def update(self):
        q = 0
        for locale in self.LOCALES:
            self.update_locale(locale)

        auto = [
            ('en', 'pt'),
            ('pt', 'pt_PT'),
            ('pt_PT', 'es'),
            ('es', 'es_ES'),
        ]

        for locale_origin, locale_dest in auto:
            print('---')
            origin = self.PO_FILES.get(locale_origin)
            dest = self.PO_FILES.get(locale_dest)

            print('')
            print(locale_origin, locale_dest)
            print_path(origin.po_file)
            print_path(dest.po_file)

            fixer_file = '_'.join(
                [
                    locale_origin.replace('_', ''),
                    locale_dest.replace('_', '')
                ])+'.tsv'
            fixer_file = os.path.join(CURRENT_PATH, 'transltabs', fixer_file)
            print_path(fixer_file)

            fixer = []
            if os.path.isfile(fixer_file):
                fixer = [
                    item.replace('\n', '').replace('\r', '').split('\t')
                    for item in open(fixer_file).readlines()
                ]

            q = origin.count + dest.count
            if origin.count > 0:
                print('\n=====\n')
                print('  Revise \n    {}    '.format(short_path(origin.po_file)))
                print('\n=====\n')
            elif dest.count > 0:
                dest.merge(origin, fixer)
                print('\n=====\n')
                print('  Revise \n    {}    '.format(short_path(dest.po_file)))
                print('\n=====\n')
            if q > 0:
                break
        return q == 0

    def compile_locale(self, locale):
        cmd = 'pybabel compile -D {} -d {} -i {} -l {} -f --statistics'.format(
                self.domain,
                self.tmp_locale_dir,
                self.po_file_paths.get(locale),
                locale
            )
        os.system(cmd)

    def compile(self):
        done = []
        for locale in self.LOCALES:
            po_file = self.po_file_paths.get(locale)
            self.compile_locale(locale)
            mo_file = po_file.replace('.po', '.mo')
            path = os.path.dirname(mo_file)
            if not os.path.isdir(path):
                os.makedirs(path)

            done.append(short_path(mo_file))
        print('\n=====\n')
        print('  Gerados\n')
        for item in done:
            print('    * {}'.format(item))
        print('\n=====\n')

    def create(self):
        self.copy_locale_dir()
        self.extract()
        self.init()

        finished = False
        while not finished:
            finished = self.update()
            if not finished:
                cont = input(
                    'Se arquivo foi revisado. Continuar (S/N)?\n> ')
                if cont.upper() != 'S':
                    break
        if finished:
            self.compile()
            self.diff()

    def diff(self):
        os.system(
            'diff -rup {} {} > diff.txt'.format(
                self.app_locale_dir,
                self.tmp_locale_dir
            )
        )
        print('\n"locale" gerado: {}\n'.format(self.tmp_locale_dir))
        print('\nVerifique diff.txt\n')
        print('\nSe estiver correto, copie {} para {} \n'.format(
                self.tmp_locale_dir, self.app_locale_dir
            )
        )


if __name__ == '__main__':
    print(os.getcwd())

    app_locale_dir = input(
        'Entre o caminho completo da PASTA "locale" da aplicação:\n> ')
    if not app_locale_dir.endswith('/locale'):
        print(
            'Caminho {} deve conter a pasta "locale". '.format(app_locale_dir))
    elif not os.path.isdir(app_locale_dir):
        print('{} não existe. Crie o caminho. '.format(app_locale_dir))
    else:
        op = input(
            'Serão gerados os arquivos de {}. Continuar (S/N)?\n> '.format(
                app_locale_dir
            )
        )
        if op.upper() == 'S':
            lc = LocaleCreator(app_locale_dir)
            lc.create()
        else:
            print('Você cancelou a operação. ')
