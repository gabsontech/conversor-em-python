import os
import subprocess
import zipfile
import imageio_ffmpeg
from gooey import Gooey, GooeyParser
from pypdf import PdfReader, PdfWriter

@Gooey(
    program_name="super conversor de arquivos leve e multimidia",
    language="english",
    theme="dark",
    clear_before_run=True
)
def main():
    parser = GooeyParser(description="ferramentas nativas e motor ffmpeg para audio, video e documentos")
    
    parser.add_argument(
        "arquivo_origem",
        metavar="selecionar arquivo",
        help="escolha um arquivo de video, audio ou documento do seu computador",
        widget="FileChooser"
    )
    
    parser.add_argument(
        "formato_destino",
        metavar="converter ou processar para:",
        help="escolha a acao ou formato final desejado",
        choices=[
            "mp3", "wav", "m4a", "mp4", "avi", "mkv", "webm",
            "video_remover_som", "video_reduzir_para_720p",
            "txt", "markdown", "zip_compactar", 
            "pdf_extrair_texto", "pdf_rotacionar_90", "pdf_proteger_com_senha"
        ]
    )

    args = parser.parse_args()
    
    if not os.path.exists(args.arquivo_origem):
        print(f"[erro] o arquivo '{args.arquivo_origem}' nao foi encontrado.")
        return

    pasta_origem, nome_completo = os.path.split(args.arquivo_origem)
    nome_puro, extensao_original = os.path.splitext(nome_completo)
    extensao_original = extensao_original.lower().replace(".", "")
    
    formato_ext = args.formato_destino.lower()
    caminho_saida = os.path.join(pasta_origem, f"{nome_puro}_convertido.{formato_ext}")

    # pega o caminho do binario do ffmpeg que instalamos no passo 1
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    print(f"[status] iniciando o processamento do arquivo: {nome_completo}")

    try:
        formatos_midia = ["mp3", "wav", "m4a", "mp4", "avi", "mkv", "webm", "mov", "flv"]

        # --- 1. conversao de audio, video e ferramentas multimidia via ffmpeg ---
        if extensao_original in formatos_midia and formato_ext in ["mp3", "wav", "m4a", "mp4", "avi", "mkv", "webm"]:
            print(f"[status] chamando o motor ffmpeg para processar a midia...")
            # comando universal do ffmpeg para converter preservando o maximo de qualidade (-y sobrescreve se ja existir)
            comando = [ffmpeg_exe, "-y", "-i", args.arquivo_origem, caminho_saida]
            subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print(f"[sucesso] midia convertida com sucesso pelo ffmpeg!")
            print(f"[salvo em] {caminho_saida}")

        elif extensao_original in formatos_midia and args.formato_destino == "video_remover_som":
            caminho_sem_som = os.path.join(pasta_origem, f"{nome_puro}_sem_som.{extensao_original}")
            comando = [ffmpeg_exe, "-y", "-i", args.arquivo_origem, "-an", caminho_sem_som]
            subprocess.run(comando, check=True)
            print(f"[sucesso] o audio do video foi removido com sucesso!")
            print(f"[salvo em] {caminho_sem_som}")

        elif extensao_original in formatos_midia and args.formato_destino == "video_reduzir_para_720p":
            caminho_720p = os.path.join(pasta_origem, f"{nome_puro}_720p.{extensao_original}")
            comando = [ffmpeg_exe, "-y", "-i", args.arquivo_origem, "-vf", "scale=-1:720", caminho_720p]
            subprocess.run(comando, check=True)
            print(f"[sucesso] video redimensionado para resolucao hd (720p)!")
            print(f"[salvo em] {caminho_720p}")

        # --- 2. compactar para zip ---
        elif args.formato_destino == "zip_compactar":
            caminho_zip = os.path.join(pasta_origem, f"{nome_puro}.zip")
            with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zip_arq:
                zip_arq.write(args.arquivo_origem, nome_completo)
            print(f"[sucesso] arquivo compactado!")
            print(f"[salvo em] {caminho_zip}")

        # --- 3. extrair textos legiveis de arquivos pdf ---
        elif extensao_original == "pdf" and args.formato_destino == "pdf_extrair_texto":
            caminho_txt = os.path.join(pasta_origem, f"{nome_puro}_texto_extraido.txt")
            leitor = PdfReader(args.arquivo_origem)
            texto_completo = ""
            for pagina in leitor.pages:
                texto_completo += pagina.extract_text() + "\n"
            with open(caminho_txt, "w", encoding="utf-8") as f:
                f.write(texto_completo)
            print(f"[sucesso] texto extraido!")
            print(f"[salvo em] {caminho_txt}")

        # --- 4. rotacionar paginas de pdf ---
        elif extensao_original == "pdf" and args.formato_destino == "pdf_rotacionar_90":
            caminho_rotacionado = os.path.join(pasta_origem, f"{nome_puro}_rotacionado.pdf")
            leitor = PdfReader(args.arquivo_origem)
            escritor = PdfWriter()
            for pagina in leitor.pages:
                pagina.rotate(90)
                escritor.add_page(pagina)
            with open(caminho_rotacionado, "wb") as f:
                escritor.write(f)
            print(f"[sucesso] pdf rotacionado!")
            print(f"[salvo em] {caminho_rotacionado}")

        # --- 5. colocar senha de protecao em um pdf ---
        elif extensao_original == "pdf" and args.formato_destino == "pdf_proteger_com_senha":
            caminho_protegido = os.path.join(pasta_origem, f"{nome_puro}_protegido.pdf")
            leitor = PdfReader(args.arquivo_origem)
            escritor = PdfWriter()
            for pagina in leitor.pages:
                escritor.add_page(pagina)
            escritor.encrypt("12345")
            with open(caminho_protegido, "wb") as f:
                escritor.write(f)
            print(f"[sucesso] pdf bloqueado com sucesso! a senha padrao e: 12345")
            print(f"[salvo em] {caminho_protegido}")

        # --- 6. salvar estruturas como texto simples ---
        elif args.formato_destino in ["txt", "markdown"]:
            caminho_txt_geral = os.path.join(pasta_origem, f"{nome_puro}_convertido.{args.formato_destino}")
            with open(args.arquivo_origem, "r", encoding="utf-8", errors="ignore") as f_in:
                dados_brutos = f_in.read()
            with open(caminho_txt_geral, "w", encoding="utf-8") as f_out:
                f_out.write(dados_brutos)
            print(f"[sucesso] arquivo gravado!")
            print(f"[salvo em] {caminho_txt_geral}")

        else:
            print(f"[erro] acao incompativel ou formato nao suportado.")

    except Exception as erro:
        print(f"[falha] erro durante a execucao: {erro}")

if __name__ == "__main__":
    main()
