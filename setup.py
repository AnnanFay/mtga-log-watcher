from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='mtga-log-watcher',
    version='0',
    description='Auto-backup MTGA logs',
    long_description=readme(),
    keywords='logs mtga backup mtg magic arena',
    url='http://github.com/AnnanFay/mtga-log-watcher',
    author='Annan Fay Yearian',
    author_email='annanfay@gmail.com',
    license='MIT',
    packages=['mtga_log_watcher'],
    package_dir={
        'mtga_log_watcher': 'mtga_log_watcher'
    },
    package_data={
        'mtga_log_watcher': ['assets/*']
    },
    install_requires=[
        'pyside6',
        'plyer',
        'humanize',
        'psutil'
    ],
    entry_points={
        # 'console_scripts': ['mtga-log-watcher=mtga_log_watcher:run'],
    },
    include_package_data=True,
    zip_safe=True
)
