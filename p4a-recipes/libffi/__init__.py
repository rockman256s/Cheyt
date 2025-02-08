"""Custom recipe for libffi to work around build issues"""
from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import shprint, current_directory
from os.path import exists, join
from multiprocessing import cpu_count
import sh

class LibffiRecipe(Recipe):
    version = '3.4.4'
    url = 'https://github.com/libffi/libffi/releases/download/v{version}/libffi-{version}.tar.gz'
    depends = []
    patches = []
    built_libraries = {'libffi.so': '.libs'}

    def should_build(self, arch):
        return not exists(join(self.ctx.get_libs_dir(arch.arch), 'libffi.so'))

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            shprint(sh.Command('./configure'),
                    '--host=' + arch.command_prefix,
                    '--prefix=' + self.ctx.get_python_install_dir(),
                    '--disable-static',
                    '--enable-shared',
                    '--disable-multi-os-directory',
                    '--disable-docs',
                    _env=env)
            shprint(sh.make, '-j', str(cpu_count()), _env=env)
            shprint(sh.make, 'install', _env=env)
            shprint(sh.cp, '-L', '.libs/libffi.so', self.ctx.get_libs_dir(arch.arch))

recipe = LibffiRecipe()