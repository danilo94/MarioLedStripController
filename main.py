import asyncio
from bleak import BleakClient
from time import sleep
from gerenciadorDeMemoria import *
from Enderecos import *
address = ""
SERVICO_CONTROLE_LEDS = ""


ligar = bytearray(b'\xcc\x23\x33')
desligar = bytearray(b'\xcc\x24\x33')
preto = bytearray(b'\x56\x00\x00\x00\x00\xF0\xAA')

async def enviarCor(payloadCor,client):
    await client.write_gatt_char(SERVICO_CONTROLE_LEDS, payloadCor)

def definirCor(red, green,blue):
    payloadCor = bytearray()
    payloadCor.append(0x56)
    payloadCor.append(red) # Vermelho
    payloadCor.append(green) # Verde
    payloadCor.append(blue) # Azul
    payloadCor.append(0x00)
    payloadCor.append(0xF0)
    payloadCor.append(0xAA)
    return payloadCor


def definirStatusMario(status,statusMontadoYoshi):
    if (statusMontadoYoshi == 1):
        return 0x00,0xff,0x00
    if (status == MARIO_PEQUENO):
        return 0x00,0x00,0x00
    if (status == MARIO_GRANDE):
        return 0xff,0x00,0x00
    if (status == MARIO_FLOR_DE_FOGO):
        return 0xff,0x45,0x00
    if (status == MARIO_PENINHA):
        return 0xff,0xff,0xff
    else:
        return 0x00,0x00,0x00

async def blinkYellow(client):
    await  client.write_gatt_char(SERVICO_CONTROLE_LEDS,preto)
    sleep(0.05)
    cor = definirCor(0xff,0xff,0x00)
    await client.write_gatt_char(SERVICO_CONTROLE_LEDS, cor)
    sleep(0.13)
    cor = definirCor(0x00,0x00,0x00)
    await client.write_gatt_char(SERVICO_CONTROLE_LEDS, cor)

async def blinkGreen(client):
    await  client.write_gatt_char(SERVICO_CONTROLE_LEDS,preto)
    sleep(0.05)
    cor = definirCor(0x00,0xff,0x00)
    await client.write_gatt_char(SERVICO_CONTROLE_LEDS, cor)
    sleep(0.13)
    cor = definirCor(0x00,0x00,0x00)
    await client.write_gatt_char(SERVICO_CONTROLE_LEDS, cor)

async def run(address, loop):
    async with BleakClient(address, loop=loop) as client:
        processo = "zsnesw.exe"
        await client.write_gatt_char(SERVICO_CONTROLE_LEDS, ligar)

        manager = gerenciadorDeMemoria(processo)
        quantidadeAnterior = 0
        statusAntigo = 0
        statusMontadoAntigo = 0
        quantidadeVidasAnterior = 0
        alterado= False
        while True:
            quantidadeAtual = manager.lerByte(MOEDAS)
            statusMario = manager.lerByte(STATUSMARIO)
            statusMontadoYoshi = manager.lerByte(MONTADO_YOSHI)
            quantidadeVidasAtual = manager.lerByte(VIDAS)

            if (statusAntigo != statusMario or alterado or statusMontadoAntigo != statusMontadoYoshi):
                print(quantidadeVidasAtual)
                statusAntigo = statusMario
                statusMontadoAntigo = statusMontadoYoshi
                r,g,b = definirStatusMario(statusAntigo,statusMontadoYoshi)
                payloadCor = definirCor(r,g,b)
                await enviarCor(payloadCor,client)
                alterado = False

            if (quantidadeAtual > quantidadeAnterior):
                alterado = True
                quantidadeAnterior = quantidadeAtual
                await blinkYellow(client)

            if (quantidadeVidasAtual > quantidadeVidasAnterior):
                alterado = True
                quantidadeVidasAnterior = quantidadeVidasAtual
                await blinkGreen(client)

            sleep(0.1)

loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, loop))
