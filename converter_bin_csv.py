"""Converte BIN v4 + TXT para CSV, sem dependências externas. Python 3.9+."""
import argparse
import csv
from pathlib import Path
import struct
import zlib

def validate(binary, report):
    meta={}
    for line in report.read_text(encoding='ascii').splitlines():
        if '=' in line:
            k,v=line.split('=',1);meta[k.strip()]=v.strip()
    if meta.get('status')!='OK':
        raise ValueError('Relatório não termina com status=OK. Coleta incompleta ou com falha; não converter para ensaio.')
    if meta.get('format')!='MPUZ_RAW_LE_V1' or meta.get('time_basis')!='sample_index_nominal':
        raise ValueError('Formato ou base temporal desconhecidos.')
    if int(meta['error_code']) or int(meta['fifo_overflows']):
        raise ValueError('Falha de aquisição registrada.')
    n=int(meta['samples']);fs=int(meta['sample_rate_nominal_hz']);scale=int(meta['lsb_per_g'])
    if n<=0 or fs!=500 or scale!=8192 or int(meta['dlpf_cfg'])!=2:
        raise ValueError('Quantidade ou configuração incompatível com esta versão.')
    if binary.stat().st_size!=n*2:
        raise ValueError('Tamanho do BIN não corresponde à contagem de amostras.')
    crc=0
    with binary.open('rb') as f:
        for block in iter(lambda:f.read(65536),b''):crc=zlib.crc32(block,crc)
    if crc!=int(meta['crc32']):raise ValueError('CRC32 divergente: dados e relatório não correspondem ou houve alteração.')
    return meta,n,fs,scale

def convert(binary,report,output):
    meta,n,fs,scale=validate(binary,report)
    # Exclusivo: não sobrescreve um CSV já existente.
    with binary.open('rb') as src, output.open('x',encoding='utf-8',newline='') as dst:
        writer=csv.writer(dst);writer.writerow(['time_s','accel_z_g'])
        i=0
        while True:
            block=src.read(65536)
            if not block:break
            for (z,) in struct.iter_unpack('<h',block):
                seconds=i//fs;microseconds=(i%fs)*2000
                writer.writerow([f'{seconds}.{microseconds:06d}',f'{z/scale:.8f}']);i+=1
        for k,v in meta.items():dst.write(f'# {k}={v}\n')
        dst.write('# acquisition_metrologically_validated=false\n')
    return n

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('binario',type=Path);p.add_argument('--relatorio',type=Path)
    p.add_argument('--saida',type=Path)
    a=p.parse_args();report=a.relatorio or a.binario.with_suffix('.TXT');output=a.saida or a.binario.with_suffix('.CSV')
    try:n=convert(a.binario,report,output)
    except (ValueError,KeyError,OSError) as exc:p.exit(1,f'ERRO: {exc}\n')
    print(f'{n} amostras convertidas: {output}')
    print('Tempo nominal = indice / 500. O CSV regular nao mede jitter do sensor.')
    print('Conferir duracao, taxa estimada, saturacao e diagnostico antes da PSD.')
if __name__=='__main__':main()
