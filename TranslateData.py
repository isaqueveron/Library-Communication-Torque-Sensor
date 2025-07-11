from LCTSfunctions import *

def TranslateData(command_para:list[int,list[int]]) -> None: 
        command = command_para[0]
        parameter = command_para[1][0]
        errors_dict = {
        0:"ERROR_OK", # not an error
        1:"ERROR_GENERIC",
        2:"ERROR_WATCHDOG",
        3:"ERROR_ROTOR_GENERIC",
        4:"ERROR_ROTOR_WRONG_SPEED",
        5:"ERROR_ROTOR_TOO_SLOW",
        6:"ERROR_ROTOR_TOO_FAST",
        7:"ERROR_ROTOR_NOT_COMPATIBLE",
        8:"ERROR_ROTOR_GOT_RESET",
        9:"ERROR_ROTOR_NOT_FOUND",
        10:"ERROR_ROTOR_UNSTABLE",
        11:"ERROR_ROTOR_TIMEOUT",
        12:"ERROR_ROTOR_GOT_NACK",
        13:"ERROR_ROTOR_BAD_CMD_ECHO",
        14:"ERROR_ROTOR_BAD_EE_WRITE",
        15:"ERROR_BAD_ROTOR_COMUNICATION"
        }
        
        if command == SCMD_ACK:
            print("ACK")
        elif command == SCMD_NACK:
            print("NOT ACK")
            print(errors_dict[parameter])
        elif command == SCMD_Hello:
            print("SCMD_Hello")
            print(errors_dict[parameter])
        elif command == SCMD_ReadStatus:
            print("SCMD_ReadStatus")
            print(parameter)
        elif command == SCMD_ReadStatusShort:
            print("SCMD_ReadStatusShort")
            print(errors_dict[parameter])
        elif command == SCMD_ReadConfig:
            print("SCMD_ReadConfig")
            print(parameter)