import streamlit as st
import fitz  # PyMuPDF
import difflib

# Função que calcula a porcentagem de semelhança entre dois textos
def text_similarity(text1, text2):
    return difflib.SequenceMatcher(None, text1, text2).ratio()

# Configuração da página do App
st.set_page_config(page_title="Otimizador de PDFs", page_icon="📄")
st.title("Faxineiro de Processos e Inquéritos")
st.write("Faça o upload do PDF bruto. O sistema vai analisar, remover as páginas repetidas (com mais de 95% de semelhança) e devolver um PDF otimizado.")

# Área de Upload
uploaded_file = st.file_uploader("Arraste ou selecione o PDF aqui", type="pdf")

if uploaded_file is not None:
    if st.button("Limpar PDF"):
        with st.spinner("Lendo e comparando páginas. Isso pode levar alguns segundos..."):
            
            # Abre o PDF original e cria um novo vazio
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            pdf_novo = fitz.open()
            
            textos_unicos = []
            paginas_mantidas = 0
            paginas_removidas = 0
            total_paginas = len(pdf_document)
            
            # Barra de progresso visual
            progress_bar = st.progress(0)

            # Varredura página por página
            for page_num in range(total_paginas):
                page = pdf_document.load_page(page_num)
                texto_atual = page.get_text("text")
                
                is_duplicate = False
                
                # Compara a página atual com as que já foram salvas
                for texto_guardado in textos_unicos:
                    similaridade = text_similarity(texto_atual, texto_guardado)
                    if similaridade > 0.95:  # Acima de 95% é considerada cópia
                        is_duplicate = True
                        break
                
                # Se for inédita, guarda no novo PDF
                if not is_duplicate:
                    textos_unicos.append(texto_atual)
                    pdf_novo.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
                    paginas_mantidas += 1
                else:
                    paginas_removidas += 1
                    
                # Atualiza a barra de progresso
                progress_bar.progress((page_num + 1) / total_paginas)

            # Salva o resultado (LINHA CORRIGIDA AQUI)
            pdf_bytes = pdf_novo.tobytes()
            pdf_document.close()
            pdf_novo.close()

        # Mostra o resultado final
        st.success("Análise concluída com sucesso!")
        st.info(f"📊 Resumo: PDF original tinha {total_paginas} páginas. Mantivemos {paginas_mantidas} e removemos {paginas_removidas} repetições.")

        # Botão para baixar o arquivo limpo
        st.download_button(
            label="Baixar PDF Otimizado",
            data=pdf_bytes,
            file_name="Processo_Otimizado.pdf",
            mime="application/pdf"
        )
