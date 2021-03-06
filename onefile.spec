# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

data_files = [
         ( 'mtga_log_watcher/assets/*', 'mtga_log_watcher/assets/' ),
         ( 'README.md', '.' )
]

spec_root = os.path.abspath(SPECPATH)

a = Analysis(['cli.py'],
             pathex=[spec_root],
             binaries=[],
             datas=data_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='mtga-log-watcher',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
