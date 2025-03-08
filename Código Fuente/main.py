from rotary import Rotary
from machine import Pin, SoftI2C,ADC
from machine import PWM
from rotary_irq_esp import RotaryIRQ
import ssd1306, onewire,ds18x20
import _thread, time
from time import sleep




#Asignacion pines para encoder rotativo
DT = Pin(5, Pin.IN, Pin.PULL_UP)
CLK = Pin(2, Pin.IN, Pin.PULL_UP)
SW = Pin(32, Pin.IN, Pin.PULL_UP)
valor_anterior = True
switch_presionado = False
valor_temporizacion = 0.1
ancho=128
alto=64
linea = 0
valor_previo= False
arriba = True
abajo = True
boton = True
valor_anterior= DT.value()
menu = [":)","Nivel Agua","Humedad","Hora", "Temperatura"]
#Asignacion pin para bomba de agua

motor = PWM(Pin(19), freq=100, duty=0)
#Asignacion Sensor humedad
    
# crear un objeto ADC actuando sobre un pin
moisture = ADC(Pin(39, Pin.IN))
moisture2 = ADC(Pin(36, Pin.IN))

# Configurar la atenuación del ADC a 11dB para el rango completo
moisture.atten(moisture.ATTN_11DB)
moisture.width(ADC.WIDTH_9BIT) 
moisture2.atten(moisture2.ATTN_11DB)
moisture2.width(ADC.WIDTH_9BIT) 

# ESP32 Pin assignment 
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
ds_pin = Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

roms = ds_sensor.scan()
print('Found DS devices: ', roms)


# ESP8266 Pin assignment
#i2c = SoftI2C(scl=Pin(5), sda=Pin(4))
screen="Medidor de temperatura"
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

#Asignacion coneccion inalambrica con app inventor y funcion_________________________________________________________________________________

import clock
import _thread
from time import sleep
list_in=[]
Dias_semana = ['Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo']
seg = 0
def thread_en_bom(a, b, c, dia_re, dia2_re, hora_reg, min_reg):
    if (a==dia_re and b==hora_reg and c==min_reg) or (a==dia2_re and b==hora_reg and c==min_reg) :
        intentos += 1
        motor.duty(50)
        print("Encendido")
        sleep(5)
        motor.duty(0)
        print("apagado")
        if intentos > 1 and min_reg==c:
            return()

def fecha_a(dia, hora, mint):
    global seg
    sleep(1)
    seg += 1
    if seg>=60:
        seg=0
        mint += 1
    if mint >= 60:
        seg=0
        mint=0
        hora+=1
    if hora>=24:
        seg=0
        mint=0
        hora=0
        dia+=1
    if dia>=6:
        seg=0
        mint=0
        hora=0
        dia=0
    print(dia,"", hora,"", mint,"", seg)
    return(dia, hora, mint)
#Algoritmo coneccion inalambrica con app inventor

import socket

# Agregar nport de donde está el servidor TCP, en el ejemplo: 3000
serverAddressPort = socket.getaddrinfo('0.0.0.0', 3000)[0][-1]
# Cantidad de bytes a recibir
bufferSize  = 128

# Descomentar si el esp32 será una estación
# from wifiSTA import connectSTA as connect

# Descomentar si el esp32 estará en modo de acceso AP
from wifiAP import apConfig as connect

# poner acá el nombre de red ssid y password para conectarse
connect("miRed", "87654321")


sk = socket.socket()
sk.bind(serverAddressPort)
sk.listen(1)
print("Listening on: ", serverAddressPort)

#Convertir cadena de texto a lista 

def convertir_a_lista(cadena):
    # Eliminar posibles espacios en blanco y comillas
    elementos = cadena.replace('"', '').split(',')
    # Retornar la lista
    return elementos

#

def bomba_act_t():
    while True:
        conn, addr = sk.accept()
        list_in_o = conn.recv(bufferSize)
        list_in_o = list_in_o.decode('utf-8')
        list_in= convertir_a_lista(list_in_o)
        print(list_in)

        if list_in:
            diar = list_in[0]
            dia = Dias_semana.index(diar)
            hora = int(list_in[1])
            mint = int(list_in[2])
            seg = 0
            dia_reg = list_in[3]
            dia_re = Dias_semana.index(dia_reg)
            dia2_reg = list_in[6]
            dia2_re = Dias_semana.index(dia2_reg)
            hora_reg = int(list_in[4])
            min_reg = int(list_in[5])
        
        while True:
            a, b, c = fecha_a(dia, hora, mint)
            dia, hora, mint = fecha_a(a, b, c)
        
            _thread.start_new_thread(thread_en_bom, (dia, hora, mint, dia_re,dia2_re, hora_reg, min_reg))


#________________________________________________________________________________________________________________________________________

def temperatura(roms):
    global screen
    oled.fill(0)
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        print(rom)
        oled.text('Temperatura: ', 0,30)
        tem=ds_sensor.read_temp(rom)
        ros=str(tem)
        oled.text(ros, 80, 40)
        oled.show()
        print(ros)
def mostrar_temp():
    
    global roms
    oled.text('Temperatura!',16,1)
    oled.show()
    for x in range (0,3):
        temperatura(roms)
        time.sleep(1)
        
#mostrar_temp()
def calcularPorcentajeHumedad(val_adc):
    return -0.370*val_adc + 139.49
def calcularPorcentajeNivel(val_adc):
    return 0.357*val_adc - 0
def mostrar_humedad():
    global roms
    oled.fill(0)
    # leer un valor analógico crudo en el rango de 0-4095
    value = moisture.read()
    por_hu=calcularPorcentajeHumedad(value)
    ros=str(por_hu)
    print(ros)
    oled.text('Humedad: ', 0,30)
    oled.text(ros, 80, 40)
    oled.show
    time.sleep(3)
def hu():
    
    oled.text('Humedad',16,1)
    oled.show()
    mostrar_humedad()
def nivel_agua():
    oled.fill(0)
    # leer un valor analógico crudo en el rango de 0-4095
    value = moisture2.read()
    por_hu=calcularPorcentajeNivel(value)
    ros=str(por_hu)
    print(ros)
    oled.text('Nivel de agua: ', 0,30)
    oled.text(ros, 80, 40)
    oled.show
    time.sleep(2)
def ni():
    
    oled.text('Nivel de agua',16,1)
    oled.show()
    nivel_agua()


#Menu  display OLED

def mostrar_menu():
    global linea
    linea_alto = 12
    oled.fill(0)
    
    for conta in range(5):
        if conta==linea:
            #oled.fill_rect(0,(conta*linea_alto)-1, ancho, linea_alto, 1 )
            oled.text(">",0,(conta*linea_alto)+1, 1)
            
            oled.text(menu[conta], 10, (conta*linea_alto)+1, 1)
            oled.show()
        else:
            oled.text(menu[conta], 10, conta*linea_alto, 1)
            oled.show()

def mostrar_switch():
    global linea
    linea_alto=12
    oled.fill(0)
    
    if (linea+1) == 2:
        ni()
    if (linea+1) == 3:
        hu()
    if (linea+1) == 5:
        mostrar_temp()
    oled.fill(0)
    texto = "fila:" + str(linea+1)
    
    oled.text("switch pulsado", 10, 10, 1)
    #oled.fill_rect(0, 24, 128, linea_alto, 1)
    oled.text (texto, 10, 26, 1)
    oled.show()
    sleep(3)
    mostrar_menu()
mostrar_menu()
def detecta_movimiento():
    global arriba, abajo, boton, valor_anterior, switch_presionado
    
    if valor_anterior != DT.value():
        if DT.value() == False:
            if CLK.value() == False:
                abajo=False
                print("horario 1")
                sleep(valor_temporizacion)
            else:
                arriba = False
                print("antihorario 1")
                sleep(valor_temporizacion)
        if DT.value() == True:
            if CLK.value()== False:
                #arriba = False
                #print("antihorario 2")
                sleep(valor_temporizacion)
            else:
                abajo = False
                print("horario 2")
                sleep(valor_temporizacion)
        valor_anterior=DT.value()
    elif valor_anterior == DT.value:
        if DT.value() == False:
            if CLK.value() == False:
                abajo=False
                print("horario 1")
                sleep(valor_temporizacion)
    else:
        arriba=True
        abajo=True
    if SW.value() == False and not switch_presionado:
        print("switch presionado")
        switch_presionado= True
        mostrar_switch()
        boton=False
    if SW.value() == True and switch_presionado:
        switch_presionado= False

def main_t():
    while True:
        global linea
        detecta_movimiento()
        if abajo== False:
            print("abajo")
        
            if linea > 3:
                linea=0
            else:
                linea+=1
                mostrar_menu()
      
      
        if arriba==False:
            print("arriba")
        
            if linea<1:
                linea=4
            else:
                linea-=1
                mostrar_menu()
while True:
    
    _thread.start_new_thread(bomba_act_t, ())
    main_t()

  
