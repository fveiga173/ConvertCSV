# Teste de aquisição Z binária com FIFO — v4

Objetivo: testar aquisição nominal de 500 Hz com gravação leve, usando a mesma montagem. Mantidos ±4 g, DLPF_CFG=2 e relógio interno do sensor. Sem novos fios. Não é validação metrológica nem firmware liberado para campanha de dias.

1. Extraia o ZIP.
2. Abra MPU6050_Z_BIN/MPU6050_Z_BIN.ino na IDE Arduino, selecione sua placa e porta e compile. Envie o resumo de memória desta versão.
3. Carregue e abra o Monitor Serial a 115200 baud. Abrir o monitor pode reiniciar o UNO e criar outra coleta; envie o par correspondente ao resumo final.
4. Deixe o sensor parado. O TESTE PARA AUTOMATICAMENTE EM 60 SEGUNDOS. S permite parar antes.
5. Espere “Coleta encerrada” e o relatório completo antes de desligar. Copie BIN e TXT do mesmo número. Nenhum arquivo anterior é sobrescrito.
6. Envie o par e o resumo completo, mesmo em erro. O BIN não abre diretamente no aplicativo atual.

## Conversão no computador

Python 3.9 ou superior, sem instalar bibliotecas. Coloque os arquivos na pasta do conversor e execute, usando o nome real:

```
python converter_bin_csv.py TEST035.BIN
```

O conversor exige TEST035.TXT, fechamento OK, contagem/tamanho compatíveis e CRC32 correto. Cria TEST035.CSV compatível com o Streamlit. Não substitui CSV existente. Use --saida outro_nome.csv para escolher um novo nome. Em caso de falha, preserve os originais para diagnóstico.

## Diagnósticos

error_code: 0 nenhuma; 1 comunicação I2C; 2 FIFO cheio/overflow; 3 gravação/tamanho; 4 pacote residual após parada; 5 leitura de confirmação da configuração; 6 limite de arquivo/contador.

max_fifo_bytes é o maior valor observado; não é amostragem contínua da ocupação. O firmware também registra ocupação e INT_STATUS na falha e antes/depois da última escrita monitorada. max_flush_acquiring_us exclui sincronização final. Se o programa falhar antes de fechar, TXT permanece INCOMPLETE. Uma falha física de cartão também pode impedir salvar o relatório.

O buffer adicional continua em 256 bytes (128 valores Z). A biblioteca SD mantém seus próprios buffers. A margem de RAM precisa ser verificada novamente após compilar; 632 bytes livres da versão anterior não comprovam ausência nem presença de colisão de pilha/heap. Não aumentar buffer sem medir.

Formato BIN: amostras Z int16 signed little-endian, sem cabeçalho, 8192 contagens/g. Exatos 2 bytes/amostra: 1000 bytes/s a 500 Hz nominais. TXT registra configuração, número de amostras e CRC32 do conteúdo binário.

## Tempo e limites

O tempo do CSV é reconstruído como índice/500, com primeira amostra em zero. Não é instante real de leitura nem comprovação de ausência de jitter. FIFO preserva a ordem das amostras enquanto não transborda. O relógio interno do MPU e o do Arduino têm erros próprios. A taxa estimada por número de amostras/duração Arduino é uma conferência aproximada, não uma calibração. Os limites de banda do filtro de 94 Hz continuam aplicáveis.

O status OK significa ausência das falhas monitoradas, não valida precisão, fixação, calibração ou representatividade. O app atual ignora metadados: examine TXT e diagnóstico antes de interpretar PSD. Saturação é relatada, mesmo com status OK, e requer avaliação.

A duração usa millis e subtração sem sinal, suficiente para este teste e períodos inferiores a aproximadamente 49 dias; não há o antigo limite de 71 minutos. O firmware encerra antes do limite de 4 GiB. Parada automática está configurada em 60000 ms, intencionalmente para a bancada.

## Registro para o TCC

TEST019: gravação textual de três eixos, taxa média observada ~207,83 registros/s.
TEST033: Z textual com formatação inteira, ~462,82 registros/s; pausas correlacionadas à sincronização do SD.
TEST034: FIFO + CSV em blocos; interrompido com sinalização de overflow. Não atribuir causa definitiva à RAM ou ao cartão sem testes adicionais.
Esta versão: FIFO + Z binário; resultado de hardware ainda pendente.

## Verificações realizadas na entrega

Sintaxe C++11 verificada com g++ e interfaces simuladas das bibliotecas Arduino. Isso não é compilação AVR: não confirma tamanho de flash/RAM, comportamento das bibliotecas reais nem temporização.
Conversor testado com valores positivos, negativos e extremos; escala, ordem dos bytes e tempo nominal conferidos. Testadas rejeições por arquivo truncado, CRC divergente, encerramento incompleto e overflow. Algoritmo CRC do firmware conferido contra zlib.
A compilação para UNO, o consumo de memória e o teste de hardware continuam pendentes.
