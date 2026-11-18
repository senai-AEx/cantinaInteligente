# Documentação

## Entregas da AV05 e da AV06

| Documento | Para que serve |
| --- | --- |
| [**Como rodar o projeto**](como-rodar.md) | Passo a passo para iniciantes: instalação no Windows, primeira execução, roteiro de 5 minutos e problemas comuns. |
| [**Documento do Sistema**](documento-do-sistema.md) | Versão final, completa, para copiar ao template e gerar o PDF da AV05. Começa com o bloco "Como usar este arquivo" e a lista de itens a confirmar. |
| [Diagramas](diagramas/README.md) | Um arquivo `.mmd` por diagrama (MER, UML e topologia) e as instruções para exportar em PNG. |
| [Roteiro de testes manuais](testes-manuais.md) | Casos numerados do sistema completo: cadastro e login, produtos, carteira, compra, histórico, painel, relatórios, segurança e layout. |
| [Roteiro do vídeo de demonstração](roteiro-video-demonstracao.md) | Vídeo sem áudio, de 6 a 8 minutos, cena a cena, com a fala do narrador e o critério de avaliação de cada cena. |
| [Apresentação para a banca](apresentacao-banca.md) | Esqueleto dos slides, divisão das falas entre os cinco integrantes e perguntas prováveis com respostas. |
| [Plano de execução — AV05 e AV06](plano-de-execucao.md) | O que a demanda pede, fases, cronograma e divisão do trabalho até a banca. |

## Referência técnica

| Documento | Para que serve |
| --- | --- |
| [Arquitetura e pastas](arquitetura.md) | Organização do repositório, módulos, camadas, sessão, transações e telas. |
| [Decisões](decisoes.md) | Stack escolhida, decisões D1 a D9, regras de negócio e a numeração final dos requisitos. |
| [Contrato da API](contrato-api.md) | Login, carteira, compras e administração: rotas, corpos JSON e erros. |
| [API de produtos](contrato-api-produtos.md) | Rotas, corpo JSON e erros do cadastro de produtos. |
| [Modelo de produto](modelo-produto.md) | Campos, regras e mudanças em relação à AV04. |

## Acompanhamento

| Documento | Para que serve |
| --- | --- |
| [Estado atual e próximas entregas](estado-atual-e-proximas-entregas.md) | Onde o projeto está, devolutivas da professora e prazos. |
| [Checklist de acessibilidade (NBR 17225)](checklist-acessibilidade-nbr17225.md) | Auditoria das telas contra o checklist da norma, as correções feitas e o que o grupo ainda precisa testar no navegador. |
| [Histórico da AV04](historico/av04/) | Requisitos, roteiro e checklist apresentados em 15/10/2026 (modelo antigo de produto). |

O checklist da ABNT NBR 17225:2025, pedido na AV06, está em `docs/checklist-acessibilidade-nbr17225.md` (auditoria por leitura de código; os testes no navegador ficam para o grupo preencher).

Para executar o projeto, veja o [README principal](../README.md). Para o fluxo de branches e commits, veja o [CONTRIBUTING](../CONTRIBUTING.md).
