from setuptools import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        exit(errno)

setup(
        name='sys11.sensu.stash',
        version='0.1',
        author='Christoph Glaubitz',
        author_email='c.glaubitz@syseleven.de',
        description=('handle stashes from sensu'),
        license='Apache License 2.0',
        url='http://github.com/chrigl/python-sys11.sensu.stash',
        tests_require=['pytest'],
        cmdclass={'test': PyTest},
        zip_safe=False,
        install_requires=[
            'six',
            'redis',
            'Jinja2',
            'markupsafe',
            ],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Topic :: System :: Monitoring",
            ],
        packages=['sys11.sensu.stash'],
        entry_points={
            'console_scripts': [
                'stashnotifier = sys11.sensu.stash.listener:main',
                ],
            'sys11.sensu.stash.notifiers': [
                'mailnotifier = sys11.sensu.stash.notifier:MailNotifier',
                'noopnotifier = sys11.sensu.stash.notifier:NoopNotifier',
                ],
            }
        )
