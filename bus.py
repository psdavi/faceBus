import face_recognition as reconhecedor
import colored
import secrets
import random
import simpy
import json

FOTOS_DAS_PESSOAS_NA_FILA = [
    "faces/fila_passageiros/personagens2.jpeg",
    "faces/fila_passageiros/passageiros_fila_2.jpg",
    "faces/fila_passageiros/passageiros_fila_3.jpg"
]

ARQUIVO_DE_CONFIGURACAO = "configuracao.json"

TEMPO_MEDIO_ENTRE_DETECCOES_DE_PASSAGEIROS = 100
TEMPO_MEDIO_ENTRE_DESEMBARQUE_DE_PASSAGEIROS = 80
PROBABILIDADE_DE_DESEMBARQUE = 30

PROBABILIDADE_DE_ESTAR_INDO_PRO_BAIRRO_B = 30
PROBABILIDADE_DE_ESTAR_INDO_PRO_BAIRRO_C = 30
PROBABILIDADE_DE_ESTAR_INDO_PRO_BAIRRO_D = 80
TEMPO_MEDIO_ENTRE_VERIFICACAO_BAIRROS = 50


PROBABILIDADE_DE_PAGAR_COM_CREDITO = 30
PROBABILIDADE_DE_PAGAR_COM_DEBITO = 30
PROBABILIDADE_DE_PAGAR_COM_PIX = 80
TEMPO_MEDIO_ENTRE_VERIFICACAO_DE_PAGAMENTOS = 99


onibus_ascii_art = """
    ___________________
   |,-----.,-----.,---.|
   ||     ||     ||    |
   |`-----'|-----||-----\`----.
   [       |    -||-   _|    (|
   [  ,--. |_____||___/.--.   |
   =-(( `))-----------(( `))-==
      `--'             `--'
"""

def preparar():
    preparado, configuracao, passageiros_reconhecidos = False, None, {}

    try:
        with open(ARQUIVO_DE_CONFIGURACAO, "r", encoding="utf-8") as arquivo:
            configuracao = json.load(arquivo)
            arquivo.close()
            preparado = True
    except Exception as e:
        print(f'erro lendo configuração: {str(e)}')

    return preparado, configuracao, passageiros_reconhecidos

def simular_fila():
    foto = random.choice(FOTOS_DAS_PESSOAS_NA_FILA)

    fila_de_pessoas = {
        "foto": foto,
        "passageiros": None
    }

    return fila_de_pessoas

def passageiro_reconhecido_anteriormente(passageiro, passageiros_reconhecidos):
    reconhecido = False
    for passageiro_reconhecido in passageiros_reconhecidos.values():
        if passageiro['codigo'] == passageiro_reconhecido['codigo']:
            reconhecido = True
            break
    return reconhecido

def reconhecer_passageiros(fila_de_pessoas, configuracao, passageiros_reconhecidos):
    print("realizando reconhecimento de passageiros...")

    foto_fila_de_pessoas = reconhecedor.load_image_file(fila_de_pessoas['foto'])
    caracteristicas_das_pessoas = reconhecedor.face_encodings(foto_fila_de_pessoas)

    passageiros = []
    for passageiro in configuracao['passageiros']:
        if passageiro_reconhecido_anteriormente(passageiro, passageiros_reconhecidos):
            print(colored.fg('white'), colored.bg('blue'), f"Passageiro: {passageiro['nome']} ainda está dentro do ônibus", colored.attr('reset'))
        else:
            fotos = passageiro['fotos']
            total_de_reconhecimentos = 0

            for foto in fotos:
                foto = reconhecedor.load_image_file(foto)
                caracteristicas = reconhecedor.face_encodings(foto)[0]

                reconhecimentos = reconhecedor.compare_faces(
                    caracteristicas_das_pessoas, caracteristicas)
                if True in reconhecimentos:
                    total_de_reconhecimentos += 1

            if total_de_reconhecimentos/len(fotos) >= 0.6:
                passageiros.append(passageiro)

    return (len(passageiros) > 0), passageiros

def imprimir_dados_do_passageiro(passageiro):
    print(colored.fg('green'),"-------------------------------------------- ACONTECEU UM EMBARQUE" + onibus_ascii_art)
    print(colored.fg('green'), "PASSAGEIRO RECONHECIDO - Realizando Embarque:", colored.attr('reset'))
    print(colored.fg('green'), f"nome: {passageiro['nome']}", colored.attr('reset'))
    print(colored.fg('green'), f"idade: {passageiro['idade']}", colored.attr('reset'))
    print(colored.fg('green'), f"tipo da passagem: {passageiro['tipo']}", colored.attr('reset'))
    print("")
    print(colored.fg('green'), "--------------------------------------------", colored.attr('reset'))

def reconhecer_face_pessoa_na_fila(ambiente_de_simulacao, configuracao, passageiros_reconhecidos):
    while True:
        print(f"reconhecendo passageiros em {ambiente_de_simulacao.now}")

        fila_de_pessoas = simular_fila()
        ocorreu_reconhecimento, passageiros = reconhecer_passageiros(fila_de_pessoas, configuracao, passageiros_reconhecidos)
        if ocorreu_reconhecimento:
            passageiros_embarcados = []
            for passageiro in passageiros:
                if not passageiro_reconhecido_anteriormente(passageiro, passageiros_reconhecidos):
                    passageiro['embarcou'] = True
                    id_passagem = secrets.token_hex(nbytes=16).upper()
                    passageiros_reconhecidos[id_passagem] = passageiro
                    passageiros_embarcados.append(passageiro)
                    imprimir_dados_do_passageiro(passageiro)

            # Remover passageiros embarcados da fila
            for passageiro_embarcado in passageiros_embarcados:
                passageiros.remove(passageiro_embarcado)

        yield ambiente_de_simulacao.timeout(TEMPO_MEDIO_ENTRE_DETECCOES_DE_PASSAGEIROS)

def processa_pagamento(ambiente_de_simulacao, passageiros_reconhecidos):
    while True:
        print(f"Processando pagamento em {ambiente_de_simulacao.now}")

        if len(passageiros_reconhecidos):
            for _, passageiro in list(passageiros_reconhecidos.items()):
                if passageiro["embarcou"]:
                    if not ('pagamento_credito' in passageiro or 'pagamento_debito' in passageiro or 'pagamento_pix' in passageiro):

                        if random.randint(1, 100) <= PROBABILIDADE_DE_PAGAR_COM_CREDITO:
                            passageiro['pagamento_credito'] = True
                            print(colored.fg('red'), colored.bg('white'),
                                  f"{passageiro['nome']} pagou a passagem com crédito", colored.attr('reset'))
                        elif random.randint(1, 100) <= PROBABILIDADE_DE_PAGAR_COM_DEBITO:
                            passageiro['pagamento_debito'] = True
                            print(colored.fg('red'), colored.bg('white'),
                                  f"{passageiro['nome']} pagou a passagem com débito", colored.attr('reset'))
                        elif random.randint(1, 100) <= PROBABILIDADE_DE_PAGAR_COM_PIX:
                            passageiro['pagamento_pix'] = True
                            print(colored.fg('red'), colored.bg('white'),
                                  f"{passageiro['nome']} pagou a passagem com pix", colored.attr('reset'))
                        else:
                            passageiro['passagem_premiada'] = True
                            print(colored.fg('white'), colored.bg('red'),
                                  f"{passageiro['nome']} ganhou a passagem premiada !!!!!!!!", colored.attr('reset'))

        yield ambiente_de_simulacao.timeout(TEMPO_MEDIO_ENTRE_VERIFICACAO_DE_PAGAMENTOS)

def verifica_viagem_bairros(ambiente_de_simulacao, passageiros_reconhecidos):
    while True:
        print(f"Verificação de Bairros {ambiente_de_simulacao.now}")

        if len(passageiros_reconhecidos):
            for _, passageiro in list(passageiros_reconhecidos.items()):
                if passageiro["embarcou"]:
                    if not ('indo_pro_bairro_b' in passageiro or 'indo_pro_bairro_c' in passageiro or 'indo_pro_bairro_d' in passageiro):
                        if random.randint(1, 100) <= PROBABILIDADE_DE_ESTAR_INDO_PRO_BAIRRO_B:
                            passageiro['indo_pro_bairro_b'] = True
                            print(colored.fg('red'), colored.bg('yellow'),
                                  f"{passageiro['nome']} está indo pro bairro B", colored.attr('reset'))
                        elif random.randint(1, 100) <= PROBABILIDADE_DE_ESTAR_INDO_PRO_BAIRRO_C:
                            passageiro['indo_pro_bairro_c'] = True
                            print(colored.fg('red'), colored.bg('yellow'),
                                  f"{passageiro['nome']} está indo pro bairro C", colored.attr('reset'))
                        elif random.randint(1, 100) <= PROBABILIDADE_DE_ESTAR_INDO_PRO_BAIRRO_D:
                            passageiro['indo_pro_bairro_d'] = True
                            print(colored.fg('red'), colored.bg('yellow'),
                                  f"{passageiro['nome']} está indo pro bairro D", colored.attr('reset'))
        yield ambiente_de_simulacao.timeout(TEMPO_MEDIO_ENTRE_VERIFICACAO_BAIRROS)

def liberar_passageiros(ambiente_de_simulacao, passageiros_reconhecidos):
    while True:
        print(f"liberando passageiro em {ambiente_de_simulacao.now}")

        if len(passageiros_reconhecidos):
            for id_passagem, passageiro in list(passageiros_reconhecidos.items()):
                if ('embarcou' in passageiro and 'indo_pro_bairro_b' in passageiro):
                    if random.randint(1, 100) <= PROBABILIDADE_DE_DESEMBARQUE:
                        if ('pagamento_credito' in passageiro or 'pagamento_debito' in passageiro or 'pagamento_pix' in passageiro or 'passagem_premiada' in passageiro):
                            passageiros_reconhecidos.pop(id_passagem)
                            print(colored.fg('red'), "------------------------------------------------------ ACONTECEU UM DESEMBARQUE")
                            print(colored.fg('red'), f"O passageiro {passageiro['nome']} desembarcou no bairro B...", colored.attr('reset'))
                            passageiro.pop('indo_pro_bairro_b', None)
                            passageiro.pop('pagamento_pix', None)
                            passageiro.pop('pagamento_debito', None)
                            passageiro.pop('pagamento_credito', None)
                            print(colored.fg('red'), "--------------------------------------------------------------------------------", colored.attr('reset'))
                if ('embarcou' in passageiro and 'indo_pro_bairro_c' in passageiro):
                    if random.randint(1, 100) <= PROBABILIDADE_DE_DESEMBARQUE:
                        if ('pagamento_credito' in passageiro or 'pagamento_debito' in passageiro or 'pagamento_pix' in passageiro or 'passagem_premiada' in passageiro):
                            passageiros_reconhecidos.pop(id_passagem)
                            print(colored.fg('red'), "------------------------------------------------------ ACONTECEU UM DESEMBARQUE")
                            print(colored.fg('red'), f"O passageiro {passageiro['nome']} desembarcou no bairro C...", colored.attr('reset'))
                            passageiro.pop('indo_pro_bairro_c', None)
                            passageiro.pop('pagamento_pix', None)
                            passageiro.pop('pagamento_debito', None)
                            passageiro.pop('pagamento_credito', None)
                            print(colored.fg('red'), "--------------------------------------------------------------------------------", colored.attr('reset'))
                if ('embarcou' in passageiro and 'indo_pro_bairro_d' in passageiro):
                    if random.randint(1, 100) <= PROBABILIDADE_DE_DESEMBARQUE:
                        if ('pagamento_credito' in passageiro or 'pagamento_debito' in passageiro or 'pagamento_pix' in passageiro or 'passagem_premiada' in passageiro):
                            passageiros_reconhecidos.pop(id_passagem)
                            print(colored.fg('red'), "------------------------------------------------------ ACONTECEU UM DESEMBARQUE")
                            print(colored.fg('red'), f"O passageiro {passageiro['nome']} desembarcou no bairro D...", colored.attr('reset'))
                            passageiro.pop('indo_pro_bairro_d', None)
                            passageiro.pop('pagamento_pix', None)
                            passageiro.pop('pagamento_debito', None)
                            passageiro.pop('pagamento_credito', None)
                            print(colored.fg('red'), "--------------------------------------------------------------------------------", colored.attr('reset'))

        yield ambiente_de_simulacao.timeout(TEMPO_MEDIO_ENTRE_DESEMBARQUE_DE_PASSAGEIROS)


if __name__ == "__main__":
    preparado, configuracao, passageiros_reconhecidos = preparar()
    if preparado:
        ambiente_de_simulacao = simpy.Environment()
        ambiente_de_simulacao.process(reconhecer_face_pessoa_na_fila(ambiente_de_simulacao, configuracao, passageiros_reconhecidos))
        ambiente_de_simulacao.process(verifica_viagem_bairros(ambiente_de_simulacao, passageiros_reconhecidos))
        ambiente_de_simulacao.process(processa_pagamento(ambiente_de_simulacao, passageiros_reconhecidos))
        ambiente_de_simulacao.process(liberar_passageiros(ambiente_de_simulacao, passageiros_reconhecidos))
        ambiente_de_simulacao.run(until=10_000)

