Code for communicating with a torque sensor from LORENZ MESSTECHNIK GmbH

this model: DR-3000

For reading data: 
 - Configure the port in "Config.py" Mac or Linux, (its just like that for my personal use)
 - Then u run reading and it'll print the transformed data maybe in N.m

References:
 - https://github.com/Duckle29/LorenzTelegram/tree/main
 - http://www.shintron.com.tw/proimages/a3-2/Protocol.pdf
 - https://www.mb-naklo.si/files/catalogs/avtomatizacija/lorenz-messtechnik/senzorji-momenta-in-sile-lorenz.pdf
 - https://www.sensor.com.tw/upload/files/lorenz/operation%20manual/090302i_DR_3000_VS.pdf
 - https://www.sensor.com.tw/upload/files/lorenz/operation%20manual/090231e_DR-2112_2212_2412_2512.pdf
 - https://forum.dewesoft.com/software-discussions/dewesoft-software/reading-torque-data-from-lorenz-dr-3000-in-dewesoft-using-serial-com-plugin

Kw: lorenz, communication, serial port, pyserial, torque sensor, software

Updates:
 - update 0 24/set/24: early code, it lacks of testing, when I get a sucessifull try, i'll write it here.
 - update 1 26/set/24: it workedddddd! I send the command and it respond some of the commands.
 - update 2 o3/out/24: now the communication are really fast, and we got the readigns already in N.m probably.

 ______________________________________________________________________

Documentação da Biblioteca de Comunicação do Transdutor de Torque Rotativo (LCTSfunctions)
Esta documentação detalha a biblioteca Python LCTSfunctions, desenvolvida para facilitar a comunicação com transdutores de torque rotativos através de uma interface serial. A biblioteca abstrai a complexidade do protocolo de comunicação, permitindo que os usuários interajam com o dispositivo de forma mais intuitiva.

Autor, Data e Versão
Autor: Isaque Verona
Data: 2025
Versão: v.1

Contexto de Utilização da Biblioteca LCTSfunctions
No âmbito do projeto de pesquisa "BANCADA DE EMULAÇÃO DE TURBINA EÓLICA INTEGRADA EM MICRORREDE", a biblioteca LCTSfunctions desempenha um papel crucial na interface com o transdutor de torque T25, um componente essencial do emulador eólico. Desenvolvida em Python e aderindo ao protocolo de comunicação serial proprietário do fabricante, esta biblioteca permite a leitura precisa e em tempo real dos valores de torque e RPM gerados pelo sistema motor-gerador. Ao abstrair a complexidade da comunicação por telegramas de bytes, a LCTSfunctions viabiliza a coleta contínua de dados, fundamental para o sistema de controle que ajusta o motor emulador eólico, garantindo que ele reproduza fielmente o comportamento de uma turbina real sob diversas condições de vento. Em última análise, a confiabilidade e agilidade proporcionadas por esta biblioteca são pilares para o desenvolvimento do gêmeo digital da microrrede e para a validação de algoritmos avançados de controle e gestão de energia em um ambiente de laboratório multiusuário.

Fluxograma de Alto Nível do Processo de Comunicação com o Torquímetro
Este fluxograma descreve a sequência de eventos para a comunicação com o torquímetro, desde a inicialização até o processamento dos dados recebidos.
A --> B{Inicializar Torquímetro}: O processo começa com a inicialização do objeto Torquimeter, configurando a porta serial e os parâmetros básicos.
B --> C{Chamar um método do Torquímetro (ex: ReadRaw)}: Um método específico do torquímetro é invocado para realizar uma operação (por exemplo, ler dados brutos).
C --> D[Enviar Telegram (Methods.SendTelegram)]: Um telegrama de comando é montado e enviado para o torquímetro através da porta serial.
D --> E{Definir isReceiving como True}: A flag isReceiving é ativada para indicar que o sistema está aguardando uma resposta.
E --> F{Loop enquanto isReceiving}: O sistema entra em um loop para monitorar a porta serial até que uma resposta seja recebida ou a flag isReceiving seja desativada.
F --> G{Ler da Porta Serial (Methods.ReadFrom)}: Tenta ler dados da porta serial.
G --> H{code_received é None?}: Verifica se algum dado foi efetivamente lido.
H -- Sim --> I{Definir isReceiving como False}: Se nenhum dado foi recebido (code_received é None), a flag é desativada.
I --> J{Retornar None}: Retorna None indicando que nenhuma resposta válida foi obtida.
H -- Não --> K{Tentar Processar Telegrama Recebido (Methods.ReceiveTg)}: Se dados foram recebidos, tenta processar o telegrama.
K -- Sucesso --> L{Extrair e Processar Dados}: Se o processamento do telegrama for bem-sucedido, os dados relevantes são extraídos e transformados.
L --> M{Atualizar atributos do Torquímetro}: Os atributos internos do objeto Torquimeter são atualizados com os dados recebidos.
M --> N{Definir isReceiving como False}: A flag isReceiving é desativada.
N --> J: O fluxo segue para retornar os dados processados.
K -- Falha --> O{Definir isReceiving como False}: Se o processamento do telegrama falhar (ex: checksum inválido), a flag é desativada.
O --> J: O fluxo segue para retornar None (ou o estado de erro, dependendo da implementação).
J --> P[Fim]: O processo de comunicação é finalizado.

Formato do Telegrama
O telegrama de comunicação com o transdutor de torque segue um formato estruturado de bytes:
STX: Byte de início de texto (Start of Text), usado para sinalizar o começo de um telegrama.
STX: Repetição do byte STX para confirmação.
Command byte: Um byte que especifica o comando a ser executado pelo transdutor (ex: ler dados, configurar, etc.).
Receiver (RX) address: O endereço do dispositivo receptor.
Transmitter (TX) address: O endereço do dispositivo transmissor.
Number of parameter bytes: O número de bytes que seguem como parâmetros para o comando.
Parameters (optional): Bytes de dados adicionais que são específicos para o comando.
Checksum: Uma soma de verificação simples para garantir a integridade dos dados.
Weighted checksum: Uma soma de verificação ponderada, adicionando uma camada extra de verificação de integridade.

Constantes de Comandos (BytearrayCommands Bytes)
Estas são as constantes hexadecimais que representam diferentes comandos utilizados na comunicação:
STX = 0x02: Start of Text (Início de Texto).
SCMD_ACK = 0x06: Acknowledge (Reconhecimento).
SCMD_NACK = 0x15: Negative Acknowledge (Reconhecimento Negativo).
SCMD_Hello = 0x40: Comando "Olá".
SCMD_ReadRaw = 0x41: Comando para Ler Dados Brutos.
SCMD_ReadStatus = 0x42: Comando para Ler Status Detalhado.
SCMD_ReadStatusShort = 0x43: Comando para Ler Status Curto.
SCMD_ReadConfig = 0x44: Comando para Ler Configuração.
SCMD_WriteFullStroke = 0x45: Comando para Escrever Sinal de Fundo de Escala.
SCMD_WriteConfig = 0x46: Comando para Escrever Configuração.
SCMD_RestartDevice = 0x4B: Comando para Reiniciar Dispositivo.
SCMD_GotoSpecialMode = 0x5a: Comando para Entrar em Modo Especial.

Classe Torquimeter
A classe Torquimeter gerencia a conexão serial e as operações de alto nível com o transdutor de torque.
__init__(self, Port:str, Tm_max:float, Rpm_max:float, Baudrate = 230400, Timeout = 0.003, byte_resolution = 25000)
Inicializa uma nova instância da classe Torquimeter.
Parâmetros:
Port (str): A porta serial à qual o torquímetro está conectado (ex: 'COM1', '/dev/ttyUSB0').
Tm_max (float): O valor máximo de torque que o dispositivo pode ler.
Rpm_max (float): O valor máximo de RPM que o dispositivo pode ler.
Baudrate (int, opcional): A taxa de transmissão da comunicação serial. Padrão: 230400.
Timeout (float, opcional): O tempo limite em segundos para as operações de leitura serial. Padrão: 0.003.
byte_resolution (int, opcional): O valor máximo em bytes que representa a resolução do sensor. Padrão: 25000.
Atributos Inicializados:
self.serialport: Um objeto serial.Serial configurado para a comunicação.
self.isReceiving: Um booleano que indica se o sistema está aguardando uma resposta.
self.Overloadflag: Um booleano que indica se houve sobrecarga na medição.
self.Tm_max: Torque máximo configurado.
self.Rpm_max: RPM máximo configurado.
self.byte_resolution: Resolução máxima em bytes.
self.data: Armazena a última lista de dados brutos lidos.
self.MesurementChannel_0: Valor da medição do canal 0 (não calibrado).
self.MesurementChannel_1: Valor da medição do canal 1 (não calibrado).
self.CalibratedValCha_0: Valor de torque calibrado.
self.CalibratedValCha_1: Valor de RPM calibrado.
self.FullstrokeFlag: Flag que indica o status de fundo de escala.
ReadRaw(self) -> list | None
Envia um comando para o sensor para obter os valores de medição mais recentes (calibrados e não calibrados). É usado para calibração ou medição em modo normal. Sensores com apenas um canal terão os mesmos valores para ambos os canais.
Parâmetros: Nenhum.
Retorna:
list: Uma lista contendo: [MesurementChannel_0, MesurementChannel_1, Torque_calibrated, RPM_calibrated, FullstrokeFlag, Overloadflag].
None: Se a comunicação falhar ou nenhum dado válido for recebido.
Hello(self) -> list | None
Configura o sensor para enviar uma mensagem após ligar. Esta função é útil para depuração, especialmente em aplicações ponto a ponto.
Parâmetros: Nenhum.
Retorna:
list: Uma lista com os dados de resposta do comando Hello.
None: Se a comunicação falhar ou nenhum dado válido for recebido.
ReadStatus(self) -> list | None
Envia um comando para obter um relatório de status detalhado do sensor, incluindo informações internas sobre sua saúde. O número de parâmetros pode variar dependendo do dispositivo.
Parâmetros: Nenhum.
Retorna:
list: Uma lista com os dados do relatório de status.
None: Se a comunicação falhar ou nenhum dado válido for recebido.
ReadStatusShort(self) -> list | None
Envia um comando para obter uma versão resumida do relatório de status do sensor.
Parâmetros: Nenhum.
Retorna:
list: Uma lista com os dados do relatório de status curto.
None: Se a comunicação falhar ou nenhum dado válido for recebido.
ReadConfig(self, parameter: int) -> list | None
Lê um bloco de configuração específico do sensor. Existem vários blocos, cada um contendo diferentes tipos de dados de configuração.
Parâmetros:
parameter (int): O número do bloco de configuração a ser lido.
Retorna:
list: Uma lista com os dados do bloco de configuração.
None: Se a comunicação falhar ou nenhum dado válido for recebido.
WriteConfig(self, parameter: list[int]) -> list | None
Escreve um bloco de configuração no sensor. Blocos como 0, 1, 128 e 129 só podem ser escritos uma única vez durante a produção do sensor.
Parâmetros:
parameters (list[int]): Uma lista de inteiros que inclui o número do bloco e 32 bytes de dados a serem escritos.
Retorna:
list: Uma lista com a resposta do sensor após a escrita.
None: Se a comunicação falhar ou nenhum dado válido for recebido.
WriteFullStroke(self, parameter: bool) -> list | None
Coloca o sensor em modo de verificação, onde ele envia um sinal de 100%. É crucial que nenhum torque seja aplicado ao sensor durante este modo para evitar informações falsas no sinal de 100%.
Parâmetros:
parameter (bool): True para ativar o modo (On), False para desativar (Off).
Retorna:
list: Uma lista com a resposta do sensor.
None: Se a comunicação falhar ou nenhum dado válido for recebido.
RestartDevice(self) -> list | None
Reinicia o dispositivo. O sensor responderá com uma mensagem 'hello', independentemente de essa função ser permitida na configuração.
Parâmetros: Nenhum.
Retorna:
list: Uma lista com a resposta do sensor.
None: Se a comunicação falhar ou nenhum dado válido for recebido.

Classe Methods
A classe Methods contém funções estáticas auxiliares para manipular telegramas de comunicação.
SendTelegram(SerialPort: object, tg: bytearray) -> None
Escreve o bytearray do telegrama na porta serial especificada.
Parâmetros:
SerialPort (object): O objeto da porta serial (ex: self.serialport da classe Torquimeter).
tg (bytearray): O telegrama a ser enviado.
Retorna: Nenhum.
ReadFrom(SerialPort: object) -> bytearray | None
Lê um telegrama da porta serial.
Parâmetros:
SerialPort (object): O objeto da porta serial.
Retorna:
bytearray: O telegrama lido, se houver dados.
None: Se nenhum dado for lido.
CleanTg(tg: bytearray) -> bytearray
Limpa caracteres especiais (como line-feed e carriage return) do final do telegrama e bytes STX do início.
Parâmetros:
tg (bytearray): O telegrama a ser limpo.
Retorna:
bytearray: O telegrama limpo.
ToHex(parameters: list[int]) -> list[str]
Converte uma lista de inteiros em uma lista de strings hexadecimais. Usada para concatenar dois bytes e formar o valor lido.
Parâmetros:
parameters (list[int]): Uma lista de inteiros.
Retorna:
list[str]: Uma lista de strings hexadecimais.
CalcChecksums(tg: list[int]) -> list[int, int]
Gera as somas de verificação (checksum e weighted checksum) para um telegrama.
Parâmetros:
tg (list[int]): Os dados do telegrama para calcular as somas de verificação.
Retorna:
list[int, int]: Uma lista contendo o checksum e o weighted checksum calculados.
CheckChecksums(tg: bytearray) -> bool
Verifica a igualdade entre as somas de verificação recebidas e as calculadas para garantir a integridade dos dados.
Parâmetros:
tg (bytearray): O bytearray recebido.
Retorna:
bool: True se as somas de verificação forem válidas, False caso contrário.
TransformData(RawData:list) -> list[list,bool]
Realiza as transformações das medições enviadas pelo sensor para seus respectivos números positivos ou negativos. Esta função é exclusiva para o comando ReadRaw.
Parâmetros:
RawData (list): Uma lista de inteiros brutos (0-65536) representando as medições.
Retorna:
list[list,bool]: Uma lista contendo [DadosÚteis, FlagDeSobrecarga].
GetRaw(command_para:list[int,list[int]]) -> list[int]
Extrai os dados brutos (medidas em bytes) de um telegrama recebido após um comando ReadRaw. A saída ainda precisa ser convertida para números positivos/negativos.
Parâmetros:
command_para (list[int,list[int]]): Uma lista contendo o comando recebido e a lista de parâmetros.
Retorna:
list[int]: Uma lista com as medições em formato decimal (0-65536): [MesurementChannel_0, MesurementChannel_1, CalibratedValCha_0, CalibratedValCha_1, FullstrokeFlag].
None: Se o comando não for SCMD_ReadRaw ou a entrada for inválida.
ReceiveTg(code_received:bytearray) -> list[int,list[int]]|str
Processa um telegrama de resposta recebido após um comando ter sido enviado e lido da porta serial.
Parâmetros:
code_received (bytearray): O bytearray lido da porta serial.
Retorna:
list[int,list[int]]: Uma lista contendo o comando e os parâmetros recebidos.
None: Se a verificação de checksum falhar.

Classe BytearrayCommands
A classe BytearrayCommands é responsável por gerar os bytearray dos comandos específicos a serem enviados para o torquímetro. Cada método retorna um bytearray pronto para ser enviado pela porta serial.
Hello() -> bytearray
Gera o telegrama para o comando SCMD_Hello.
Parâmetros: Nenhum.
Retorna: bytearray: O telegrama do comando 'Hello'.
ReadRaw() -> bytearray
Gera o telegrama para o comando SCMD_ReadRaw.
Parâmetros: Nenhum.
Retorna: bytearray: O telegrama do comando 'ReadRaw'.
ReadStatus() -> bytearray
Gera o telegrama para o comando SCMD_ReadStatus.
Parâmetros: Nenhum.
Retorna: bytearray: O telegrama do comando 'ReadStatus'.
ReadStatusShort() -> bytearray
Gera o telegrama para o comando SCMD_ReadStatusShort.
Parâmetros: Nenhum.
Retorna: bytearray: O telegrama do comando 'ReadStatusShort'.
ReadConfig(PARAMETER: int) -> bytearray
Gera o telegrama para o comando SCMD_ReadConfig.
Parâmetros:
PARAMETER (int): O número do bloco de configuração a ser lido.
Retorna: bytearray: O telegrama do comando 'ReadConfig'.
WriteConfig(PARAMETERS: list[int]=[]) -> bytearray
Gera o telegrama para o comando SCMD_WriteConfig.
Parâmetros:
PARAMETERS (list[int]): Uma lista contendo o número do bloco e os 32 bytes de dados de configuração.
Retorna: bytearray: O telegrama do comando 'WriteConfig'.
WriteFullStroke(PARAMETER: bool) -> bytearray
Gera o telegrama para o comando SCMD_WriteFullStroke.
Parâmetros:
PARAMETER (bool): True para ativar, False para desativar.
Retorna: bytearray: O telegrama do comando 'WriteFullStroke'.
RestartDevice() -> bytearray
Gera o telegrama para o comando SCMD_RestartDevice.
Parâmetros: Nenhum.
Retorna: bytearray: O telegrama do comando 'RestartDevice'.




