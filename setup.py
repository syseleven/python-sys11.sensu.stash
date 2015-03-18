from setuptools import setup

setup(
        name='sys11.sensu.stash',
        version='0.1',
        author='Christoph Glaubitz',
        author_email='c.glaubitz@syseleven.de',
        description=('handle stashes from sensu'),
        license='Apache License 2.0',
        url='http://github.com/chrigl/python-sys11.sensu.stash',
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
                'stashnotifier = sys11.sensu.stash.listener:listen',
                ],
            'sys11.sensu.stash.notifiers': [
                'mailnotifier = sys11.sensu.stash.notifier:MailNotifier',
                ],
            }
        )
