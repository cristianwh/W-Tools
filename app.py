import streamlit as st
import fitz  # PyMuPDF

# Motor de similaridade leve
def text_similarity(text1, text2):
    set1 = set(text1.lower().split())
    set2 = set(text2.lower().split())
    if not set1 or not set2:
        return 0.0
    intersecao = set1.intersection(set2)
    uniao = set1.union(set2)
    return len(intersecao) / len(uniao)

st.set_page_config(page_title="Otimizador de PDFs", page_icon="📄")
st.title("Faxineiro de Processos e Inquéritos")
st.write("Faça o upload do PDF bruto. O sistema vai analisar, remover as páginas repetidas e devolver um PDF enxuto.")

uploaded_file = st.file_uploader("Arraste ou selecione o PDF aqui", type="pdf")

if uploaded_file is not None:
    if st.button("Limpar PDF"):
        with st.spinner("Modo de baixo consumo de memória ativado. Analisando páginas..."):
            try:
                # Abre o PDF uma única vez (economiza muita memória)
                pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                total_paginas = len(pdf_document)
                
                textos_unicos = []
                paginas_para_manter = [] # Guardamos APENAS os números das páginas, não as páginas inteiras
                
                progress_bar = st.progress(0)

                # Varredura
                for page_num in range(total_paginas):
                    page = pdf_document.load_page(page_num)
                    texto_atual = page.get_text("text")
                    
                    is_duplicate = False
                    
                    for texto_guardado in textos_unicos:
                        if text_similarity(texto_atual, texto_guardado) > 0.95:
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        textos_unicos.append(texto_atual)
                        paginas_para_manter.append(page_num)
                        
                    progress_bar.progress((page_num + 1) / total_paginas)

                # A MÁGICA: Em vez de copiar e colar, ele apenas "filtra" o documento original
                pdf_document.select(paginas_para_manter)
                
                # Salva o resultado
                pdf_bytes = pdf_document.tobytes()
                pdf_document.close()

                # Conta final
                paginas_mantidas = len(paginas_para_manter)
                paginas_removidas = total_paginas - paginas_mantidas

                st.success("Análise concluída com sucesso!")
                st.info(f"📊 Resumo: PDF original tinha {total_paginas} páginas. Mantivemos {paginas_mantidas} e removemos {paginas_removidas} repetições.")

                st.download_button(
                    label="Baixar PDF Otimizado",
                    data=pdf_bytes,
                    file_name="Processo_Otimizado.pdf",
                    mime="application/pdf"
                )
            
            except Exception as e:
                st.error(f"Erro na execução. Detalhes: {e}")
