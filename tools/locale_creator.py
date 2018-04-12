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
                if '/en/' in self.po_file:
                    self.terms[k] = item.replace('msgstr ', 'msgid ')

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
                text = origin.terms.get(k)
                for a, b in fixer:
                    text = text.replace(a, b)
                new.append(text)
            else:
                new.append(item)

        open(self.po_file, 'w').write('\n'.join(new))
        os.system(
            'diff -rup {} {} > {}.diff.txt'.format(
                bkpfile, self.po_file, os.path.basename(self.po_file)))


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
            new = f.replace(self.app_locale_dir, self.locale_dir)
            dirname = os.path.dirname(new)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            shutil.copyfile(f, new)

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
            origin = self.PO_FILES.get(locale_origin)
            dest = self.PO_FILES.get(locale_dest)

            fixer_file = '_'.join(
                [locale_origin, locale_dest.replace('_', '')])+'.tsv'
            fixer_file = os.path.join(CURRENT_PATH, 'transltabs', fixer_file)

            fixer = []
            if os.path.isfile(fixer_file):
                fixer = [
                    item.split('\t')
                    for item in open(fixer_file).readlines()
                ]

            q = origin.count + dest.count
            if origin.count > 0:
                print('\n=====\n')
                print('  Revise {}'.format(origin.po_file))
                print('  Depois execute novamente a atualizacao')
                print('  Faltam {} termos'.format(origin.count))
                print('\n=====\n')
            elif dest.count > 0:
                dest.merge(origin.po_file, fixer)
                print('\n=====\n')
                print('  Revise {}'.format(dest.po_file))
                print('  Depois execute novamente a atualizacao')
                print('  Faltam {} termos'.format(dest.count))
                print('\n=====\n')
            if q > 0:
                break
        return q == 0

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

    def create(self):
        reset = not os.path.isfile(self.pot_file)
        self.extract()
        if reset:
            self.init()
        if self.update():
            self.compile()
