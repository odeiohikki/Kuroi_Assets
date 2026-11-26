from pathlib import Path
import zipfile
import re

allowed = {
    **{name: {'attack','defense','special'} for name in ['anya','barou','bayonetta','columbina','dazai','ichigo','jolyne','kirara','robin']},
    'dante': {'defense','devil_trigger','gunslinger','royalguard','swordmaster','trickster'},
    'itachi': {'attack','defense','totsuka_sword','yata_mirror'},
    'magna': {'attack','defense','special_1','special_2'},
    'rider': {'attack_enhanced','attack_normal','defense_enhanced','defense_normal','special_normal','special_petrification'},
    'saber': {'attack_hidden','attack_revealed','defense','special'},
}
expected = {f'gifs/{name}/{action}.gif' for name, actions in allowed.items() for action in actions}
assert len(expected) == 51
archives = sorted(Path('incoming').glob('Kuroi_upload_*.zip'))
pending = {}
for archive in archives:
    if not re.fullmatch(r'Kuroi_upload_0[1-6]\.zip', archive.name):
        raise ValueError(f'Nome inesperado: {archive}')
    if archive.stat().st_size > 25_000_000:
        raise ValueError('ZIP muito grande')
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            name = item.filename
            if name not in expected or name in pending or item.file_size > 15_000_000:
                raise ValueError(f'Entrada inválida: {name}')
            data = z.read(item)
            if data[:6] not in (b'GIF87a', b'GIF89a'):
                raise ValueError(f'GIF inválido: {name}')
            pending[name] = data
if set(pending) != expected:
    print(f'Aguardando pacotes: {len(pending)}/51 GIFs recebidos.')
    raise SystemExit(0)
for name, data in pending.items():
    target = Path(name)
    if target.is_symlink() or any(parent.is_symlink() for parent in target.parents):
        raise ValueError(f'Link simbólico inesperado: {name}')
    if target.exists() and target.read_bytes() != data:
        raise ValueError(f'Arquivo existente diferente: {name}')
for name, data in pending.items():
    target = Path(name)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
print('51 GIFs importados sem alterar retratos.')
