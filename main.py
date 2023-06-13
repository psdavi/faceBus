import cv2
import face_recognition
import json


def exibir_menu():
    print("Menu:")
    print("1. Iniciar Programa")
    print("2. Sair")


def reconhece_faces():
    FILAS_PASSAGEIROS = [
        "fila_passageiros/fila1.jpg",
        "fila_passageiros/fila2.jpg",
        "fila_passageiros/fila3.jpg",
        "fila_passageiros/fila4.jpg",
        "fila_passageiros/fila5.png",

    ]
    ARQUIVO_DE_CONFIGURACAO = "dados_passageiros.json"

    # Carregar o arquivo de configuração JSON
    with open(ARQUIVO_DE_CONFIGURACAO, 'r') as arquivo:
        configuracao = json.load(arquivo)

    # Criar uma lista para armazenar os passageiros reconhecidos
    passageiros_reconhecidos = []

    # Carregar as fotos dos passageiros do arquivo de configuração
    for passageiro in configuracao['passageiros']:
        for foto in passageiro['fotos']:
            imagem = face_recognition.load_image_file(foto)
            encodings = face_recognition.face_encodings(imagem)
            if len(encodings) > 0:
                encoding = encodings[0]
                passageiros_reconhecidos.append({'encoding': encoding, 'dados': passageiro})
            else:
                pass
                # print(f"Nenhum rosto detectado na imagem: {foto}")

    # Realizar o reconhecimento facial das fotos dos passageiros
    for foto_passageiro in FILAS_PASSAGEIROS:
        print(
            "***************************************************************************************************************************")
        print(f" ---------- Processando imagem: {foto_passageiro} ----------")
        imagem_passageiro = face_recognition.load_image_file(foto_passageiro)
        face_locations = face_recognition.face_locations(imagem_passageiro)
        encodings_passageiro = face_recognition.face_encodings(imagem_passageiro, face_locations)

        for encoding_passageiro in encodings_passageiro:
            # Comparar o encoding do passageiro com os encodings dos passageiros conhecidos
            matches = face_recognition.compare_faces(
                [passageiro['encoding'] for passageiro in passageiros_reconhecidos], encoding_passageiro)

            # Verificar se houve correspondência
            if True in matches:
                index = matches.index(True)
                passageiro_reconhecido = passageiros_reconhecidos[index]['dados']
                print(f"(OK) Passageiro reconhecido:")
                print("######## FUNÇÃO 1: Reconhecendo face ##")
                print(f"----------------Nome: {passageiro_reconhecido['nome']}")
                print(f"----------------Idade: {passageiro_reconhecido['idade']}")
                print(f"----------------Documento: {passageiro_reconhecido['documento']}")
                print(f"----------------Tipo de Passagem: {passageiro_reconhecido['tipo_passagem']}")
                print(f"----------------Validade: {passageiro_reconhecido['validade_cadastro']}")
                print(f"----------------Endereço: {passageiro_reconhecido['endereco']}")

                tipo_cobranca = passageiro_reconhecido['tipo_passagem']
                identificar_tipo_passageiro(tipo_cobranca)

                # Imprima outros dados do passageiro conforme necessário
            else:
                print("(  ) Passageiro não reconhecido")
        print("---------- Leitura da Fila Encerrada ----------")
        print("")
        print(
            "***************************************************************************************************************************")



def identificar_tipo_passageiro(tipo_cobranca):
    print("############ FUNÇÃO 2: Identificando o tipo da passagem ##")
    if tipo_cobranca == "COMUM":
        print("-------------------------- Identificando tipo da passagem... "+tipo_cobranca)
        realizar_cobranca_comum()
    elif tipo_cobranca == "INFANTIL":
        print("-------------------------- Identificando tipo da passagem... " + tipo_cobranca)
        realizar_cobranca_infantil()
    elif tipo_cobranca == "ESTUDANTE":
        print("-------------------------- Identificando tipo da passagem... " + tipo_cobranca)
        realizar_cobranca_estudante()
    elif tipo_cobranca == "IDOSO":
        print("-------------------------- Identificando tipo da passagem... " + tipo_cobranca)
        print("-------------------------------------Entrada Gratuita")
    elif tipo_cobranca == "CADEIRANTE":
        print("-------------------------- Identificando tipo da passagem... " + tipo_cobranca)
        print("------------------------------------ Entrada Gratuita")
    elif tipo_cobranca == "ESPECIAL":
        print("--------------------------Identificando tipo da passagem... " + tipo_cobranca)
        print("--------------------------------------Entrada Gratuita")
    else:
        print("Erro no sistema")

def realizar_cobranca_comum():
    print("################ FUNÇÃO 3: Efetuando a cobrança da passagem ##")
    print("-------------------------- Valor da Passagem R$5,00 ")
    print("#################### FUNÇÃO 4: Liberando a entrada ##")
    print("-------------------------- Entrada Liberada")

def realizar_cobranca_infantil():
    print("################ FUNÇÃO 3: Efetuando a cobrança da passagem ##")
    print("-------------------------- Valor da Passagem R$3,00 ")
    print("#################### FUNÇÃO 4: Liberando a entrada ##")
    print("-------------------------- Entrada Liberada")

def realizar_cobranca_estudante():
    print("################ FUNÇÃO 3: Efetuando a cobrança da passagem ##")
    print("-------------------------- Valor da Passagem R$2,00 ")
    print("#################### FUNÇÃO 4: Liberando a entrada ##")
    print("-------------------------- Entrada Liberada")



while True:
    exibir_menu()
    escolha = input("Digite o número da opção desejada: ")

    if escolha == "1":
        reconhece_faces()

    elif escolha == "2":
        print("Saindo do programa...")
        break
    else:
        print("Opção inválida. Por favor, escolha uma opção válida.")