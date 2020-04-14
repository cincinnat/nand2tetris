import os
import glob
import contextlib

from parser import Parser
from code_generator import CodeGenerator


class Translator:
    def __init__(self):
        self.__parser = None
        self.__generator = None


    @contextlib.contextmanager
    def __init_resorces(self):
        self.__parser = Parser()
        self.__generator = CodeGenerator()
        yield
        self.__parser = None
        self.__generator = None


    def translate(self, path, dry_run=False):
        with self.__init_resorces():
            blocks = self.__translate(path)

            if dry_run:
                for _ in blocks:
                    pass
            else:
                output = self.__make_output_name(path)
                with open(output, 'w') as f:
                    for block in blocks:
                        f.write(block)
                        f.write('\n')


    def __translate(self, path):
        if os.path.isdir(path):
            yield from self.__translate_project(path)
        else:
            yield from self.__translate_file(path)


    def __translate_project(self, path):
        yield self.__generator.gen_initializer()
        for fname in glob.iglob(os.path.join(path, '*.vm')):
            yield from self.__translate_file(fname)


    def __translate_file(self, path):
        filename = os.path.splitext(os.path.basename(path))[0]
        commands = self.__parser.parse_file(path)
        yield from self.__generator.itranslate(filename, commands)


    def __make_output_name(self, input_name):
        if os.path.isdir(input_name):
            dirname = os.path.basename(os.path.abspath(input_name))
            fname = os.path.join(input_name, dirname)
        else:
            fname, _ = os.path.splitext(input_name)
        return fname + '.asm'
