from LCTS.Functions import *

while True:
    print('________________________')
    print('choose a command:       | I')
    print('(1) -> ReadStatus       | S C')#ok
    print('(2) -> ReadStatusShort  | A O')#ok
    print('(3) -> ReadConfig       | Q D')#bad_parameter
    print('(4) -> WriteConfig      | U E')#bad_parameter
    print('(5) -> WriteFullStroke  | E)')#bad_parameter
    print('(6) -> RestartDevice    |  ')#ok
    print('________________________')
    isReceiving = True
    selection = input('write command: ')
    if selection == '1':
        Tools.SendTelegram(Commands.ReadStatus())
    elif selection == '2':
        Tools.SendTelegram(Commands.ReadStatusShort())
    elif selection == '3':
        Tools.SendTelegram(Commands.ReadConfig())
    elif selection == '4':
        Tools.SendTelegram(Commands.WriteConfig())
    elif selection == '5':
        Tools.SendTelegram(Commands.WriteFullStroke())
    elif selection == '6':
        Tools.SendTelegram(Commands.RestartDevice())
    else:
        print('!invalid command!')  
        print('________________________')
        isReceiving = False  

    isReceiving = True
    while isReceiving: #loop for receiving
        try:code_received=Receive.read_from()
        except: code_received = None
        if code_received != None:
            data = Receive.GetRaw(Receive.ReceiveTg(code_received))
            if data == None: pass
            else: print(data)
        else:
            break
