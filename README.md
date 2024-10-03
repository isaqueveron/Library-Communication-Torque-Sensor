Code for communicating with a torque sensor from LORENZ MESSTECHNIK GmbH

this model: DR-3000

For reading data: 
 - Configure the port in "Config.py" Mac or Linux, (its just like that for my personal use)
 - Then u run reading and it'll print the transformed data maybe in N.m

References:
 - https://github.com/Duckle29/LorenzTelegram/tree/main
http://www.shintron.com.tw/proimages/a3-2/Protocol.pdf
https://www.mb-naklo.si/files/catalogs/avtomatizacija/lorenz-messtechnik/senzorji-momenta-in-sile-lorenz.pdf
https://www.sensor.com.tw/upload/files/lorenz/operation%20manual/090302i_DR_3000_VS.pdf
https://www.sensor.com.tw/upload/files/lorenz/operation%20manual/090231e_DR-2112_2212_2412_2512.pdf
https://forum.dewesoft.com/software-discussions/dewesoft-software/reading-torque-data-from-lorenz-dr-3000-in-dewesoft-using-serial-com-plugin

Kw: lorenz, communication, serial port, pyserial, torque sensor, software

Updates:
 - update 0 24/set/24: early code, it lacks of testing, when I get a sucessifull try, i'll write it here.
 - update 1 26/set/24: it workedddddd! I send the command and it respond some of the commands.
 - update 2 o3/out/24: now the communication are really fast, and we got the readigns already in N.m probably.
