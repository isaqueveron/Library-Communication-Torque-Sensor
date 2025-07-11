-----

# Biblioteca de Comunicação do Transdutor de Torque Rotativo (`LCTSfunctions`)

[](https://www.python.org/)
[](https://opensource.org/licenses/MIT)
[](https://www.google.com/search?q=https://github.com/isaque-verona/LCTSfunctions/commits/main)

-----

## Visão Geral

A biblioteca `LCTSfunctions` é um conjunto de módulos Python desenvolvido para facilitar a comunicação serial com transdutores de torque rotativos, especificamente o modelo T25 da Interface Inc. Esta biblioteca de alto nível abstrai as complexidades do protocolo de comunicação proprietário do fabricante, permitindo que pesquisadores e engenheiros interajam com o dispositivo de forma eficiente para aquisição e controle de dados.

-----

## Contexto de Utilização no Projeto "Bancada de Emulação de Turbina Eólica Integrada em Microrrede"

No âmbito do projeto de pesquisa "BANCADA DE EMULAÇÃO DE TURBINA EÓLICA INTEGRADA EM MICRORREDE", a **biblioteca `LCTSfunctions`** desempenha um papel crucial na interface com o transdutor de torque T25, um componente essencial do emulador eólico. Desenvolvida em Python e aderindo ao protocolo de comunicação serial proprietário do fabricante, esta biblioteca permite a **leitura precisa e em tempo real dos valores de torque e RPM** gerados pelo sistema motor-gerador. Ao abstrair a complexidade da comunicação por telegramas de bytes, a `LCTSfunctions` viabiliza a **coleta contínua de dados**, fundamental para o sistema de controle que ajusta o motor emulador eólico, garantindo que ele reproduza fielmente o comportamento de uma turbina real sob diversas condições de vento. Em última análise, a confiabilidade e agilidade proporcionadas por esta biblioteca são pilares para o desenvolvimento do gêmeo digital da microrrede e para a validação de algoritmos avançados de controle e gestão de energia em um ambiente de laboratório multiusuário.

-----

## Fluxograma de Alto Nível do Processo de Comunicação

O processo de comunicação com o torquímetro através desta biblioteca segue o seguinte fluxo:

1.  **Inicialização do Torquímetro**: Criação de uma instância da classe `Torquimeter`.
2.  **Chamada de Método**: Invocação de um método do `Torquimeter` (e.g., `ReadRaw`).
3.  **Envio de Telegrama**: O comando é convertido em um telegrama de bytes e enviado via serial.
4.  **Aguardando Resposta**: A biblioteca entra em um loop, aguardando dados da porta serial.
5.  **Leitura e Processamento**: Os dados recebidos são lidos, limpos e a integridade é verificada (checksums).
6.  **Extração de Dados**: Em caso de sucesso, os parâmetros são extraídos e transformados.
7.  **Atualização de Atributos**: Os atributos do objeto `Torquimeter` são atualizados com os novos valores.
8.  **Retorno**: O método retorna os dados processados ou `None` em caso de falha.

-----

## Formato do Telegrama

Os telegramas de comunicação seguem um formato de bytes padrão:

  * **`STX` (0x02)**: Byte de início de texto (repetido duas vezes).
  * **Command byte**: Define a operação a ser realizada.
  * **Receiver (RX) address**: Endereço do dispositivo de destino.
  * **Transmitter (TX) address**: Endereço do dispositivo de origem.
  * **Number of parameter bytes**: Quantidade de bytes nos parâmetros.
  * **Parameters (optional)**: Dados específicos do comando.
  * **Checksum**: Soma de verificação simples.
  * **Weighted checksum**: Soma de verificação ponderada.

-----

## Comandos Disponíveis

A biblioteca implementa os seguintes comandos, representados por constantes hexadecimais:

  * `STX = 0x02`
  * `SCMD_ACK = 0x06`
  * `SCMD_NACK = 0x15`
  * `SCMD_Hello = 0x40`
  * `SCMD_ReadRaw = 0x41`
  * `SCMD_ReadStatus = 0x42`
  * `SCMD_ReadStatusShort = 0x43`
  * `SCMD_ReadConfig = 0x44`
  * `SCMD_WriteFullStroke = 0x45`
  * `SCMD_WriteConfig = 0x46`
  * `SCMD_RestartDevice = 0x4B`
  * `SCMD_GotoSpecialMode = 0x5a`

-----

## Instalação

Para utilizar esta biblioteca, você precisará ter o Python instalado e a biblioteca `pyserial`.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/LCTSfunctions.git
    cd LCTSfunctions
    ```
2.  **Instale as dependências:**
    ```bash
    pip install pyserial
    ```

-----

## Como Usar

### `Torquimeter` Classe

Esta classe gerencia a conexão serial e as operações de alto nível com o transdutor.

#### `__init__(self, Port:str, Tm_max:float, Rpm_max:float, Baudrate = 230400, Timeout = 0.003, byte_resolution = 25000)`

Inicializa a comunicação com o torquímetro.

  * `Port` (string): Nome da porta serial (ex: 'COM1' no Windows, '/dev/ttyUSB0' no Linux).
  * `Tm_max` (float): Torque máximo que o dispositivo pode medir (para calibração).
  * `Rpm_max` (float): RPM máximo que o dispositivo pode medir (para calibração).
  * `Baudrate` (int, opcional): Taxa de transmissão. Padrão: `230400`.
  * `Timeout` (float, opcional): Tempo limite para leitura serial em segundos. Padrão: `0.003`.
  * `byte_resolution` (int, opcional): Valor máximo em bytes que representa a resolução do sensor. Padrão: `25000`.

#### Métodos de Leitura e Escrita

  * **`ReadRaw()`**: Obtém os valores de medição brutos e calibrados (torque e RPM).
      * Retorna: `list` (MesurementChannel\_0, MesurementChannel\_1, Torque\_calibrated, RPM\_calibrated, FullstrokeFlag, Overloadflag) ou `None`.
  * **`Hello()`**: Envia um comando "Hello" e recebe a resposta do sensor.
      * Retorna: `list` com os dados de resposta ou `None`.
  * **`ReadStatus()`**: Solicita um relatório de status detalhado.
      * Retorna: `list` com os dados do status ou `None`.
  * **`ReadStatusShort()`**: Solicita um relatório de status resumido.
      * Retorna: `list` com os dados do status curto ou `None`.
  * **`ReadConfig(parameter: int)`**: Lê um bloco de configuração específico.
      * `parameter` (int): Número do bloco de configuração.
      * Retorna: `list` com os dados do bloco ou `None`.
  * **`WriteConfig(parameters: list[int])`**: Escreve um bloco de configuração.
      * `parameters` (list[int]): Lista com o número do bloco e 32 bytes de dados.
      * Retorna: `list` com a resposta do sensor ou `None`.
  * **`WriteFullStroke(parameter: bool)`**: Ativa/desativa o modo de sinal de fundo de escala.
      * `parameter` (bool): `True` (On) ou `False` (Off).
      * Retorna: `list` com a resposta do sensor ou `None`.
  * **`RestartDevice()`**: Reinicia o dispositivo.
      * Retorna: `list` com a resposta do sensor ou `None`.

### Exemplo de Uso (Básico)

```python
import serial
from LCTSfunctions import Torquimeter, Methods, BytearrayCommands

# Configurações da porta serial e do torquímetro
PORTA_SERIAL = 'COM3' # Altere para a porta correta do seu sistema
TORQUE_MAX = 100.0 # N.m (Exemplo: 100 N.m para o T25)
RPM_MAX = 3000.0   # RPM (Exemplo: 3000 RPM)

try:
    # Inicializa o objeto Torquimeter
    torquimetro = Torquimeter(Port=PORTA_SERIAL, Tm_max=TORQUE_MAX, Rpm_max=RPM_MAX)
    print(f"Torquímetro conectado na porta {PORTA_SERIAL}.")

    # Exemplo: Ler dados brutos
    print("Tentando ler dados brutos...")
    dados_brutos = torquimetro.ReadRaw()

    if dados_brutos:
        print("\nDados Brutos Recebidos:")
        print(f"  Canal 0 (Não Calibrado): {dados_brutos[0]}")
        print(f"  Canal 1 (Não Calibrado): {dados_brutos[1]}")
        print(f"  Torque Calibrado (N.m): {dados_brutos[2]:.2f}")
        print(f"  RPM Calibrado: {dados_brutos[3]:.2f}")
        print(f"  Fullstroke Flag: {dados_brutos[4]}")
        print(f"  Overload Flag: {dados_brutos[5]}")
    else:
        print("Falha ao ler dados brutos ou sem dados disponíveis.")

    # Exemplo: Enviar comando Hello
    print("\nEnviando comando 'Hello'...")
    resposta_hello = torquimetro.Hello()
    if resposta_hello:
        print(f"Resposta 'Hello' recebida: {resposta_hello}")
    else:
        print("Nenhuma resposta ao comando 'Hello'.")

except serial.SerialException as e:
    print(f"Erro de comunicação serial: {e}. Verifique se a porta está correta e disponível.")
except Exception as e:
    print(f"Ocorreu um erro: {e}")
finally:
    # Sempre feche a porta serial ao finalizar
    if 'torquimetro' in locals() and torquimetro.serialport.is_open:
        torquimetro.serialport.close()
        print("\nPorta serial fechada.")

```

-----

## Contribuições

Contribuições são bem-vindas\! Se você encontrar bugs, tiver sugestões de melhorias ou quiser adicionar novas funcionalidades, sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

-----

## Licença

Este projeto está licenciado sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.

-----

## Contato

  * **Isaque Verona** - [GitHub Profile](https://www.google.com/search?q=https://github.com/isaqueveron)

-----

## Referencias

 - https://github.com/Duckle29/LorenzTelegram/tree/main
 - http://www.shintron.com.tw/proimages/a3-2/Protocol.pdf
 - https://www.mb-naklo.si/files/catalogs/avtomatizacija/lorenz-messtechnik/senzorji-momenta-in-sile-lorenz.pdf
 - https://www.sensor.com.tw/upload/files/lorenz/operation%20manual/090302i_DR_3000_VS.pdf
 - https://www.sensor.com.tw/upload/files/lorenz/operation%20manual/090231e_DR-2112_2212_2412_2512.pdf
 - https://forum.dewesoft.com/software-discussions/dewesoft-software/reading-torque-data-from-lorenz-dr-3000-in-dewesoft-using-serial-com-plugin

Key-words: Lorenz, communication, serial, pyserial, torque sensor, Interface, transducer.

Updates:
 - update 0 24/set/24: early code, it lacks of testing, when I get a sucessifull try, i'll write it here.
 - update 1 26/set/24: it workedddddd! I send the command and it respond some of the commands.
 - update 2 o3/out/24: now the communication are really fast, and we got the readigns already in N.m probably.
 - update 3 11/jul/25: damn time flies, the code looks professional now, object oriented, all documented, works good in production, my masterpiece until now in this engenniering course.

 ______________________________________________________________________
