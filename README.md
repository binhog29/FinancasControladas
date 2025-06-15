# FinançasControladas

## Visão Geral do Projeto

O FinançasControladas é uma aplicação web intuitiva e eficiente, projetada para ajudar indivíduos a gerenciar suas finanças pessoais de forma simples e organizada. Nosso objetivo é fornecer as ferramentas essenciais para que os usuários possam acompanhar suas receitas, despesas e ter uma visão clara de seu saldo total, promovendo uma melhor saúde financeira.

## Status do Projeto

Este é um projeto em fase inicial de desenvolvimento. Estamos focados em construir um Produto Mínimo Viável (MVP) robusto e funcional nos próximos 1-2 meses.

## Funcionalidades do MVP (Produto Mínimo Viável)

A primeira versão do FinançasControladas terá as seguintes funcionalidades principais:

* **Cadastro e Autenticação de Usuários:** Permite que os usuários criem suas contas e acessem a plataforma de forma segura.
* **Registro de Receitas:** Adicione facilmente suas fontes de renda.
* **Registro de Despesas:** Registre todos os seus gastos.
* **Visualização de Saldo Total:** Tenha uma visão clara do seu dinheiro disponível.
* **Categorização Simples:** Organize suas transações em categorias básicas para uma melhor análise.

## Tecnologias Utilizadas

Este projeto está sendo desenvolvido utilizando uma pilha de tecnologias modernas e eficientes, escolhidas para otimizar o desenvolvimento mesmo com recursos de hardware limitados no início:

* **Backend:** Python com o framework [Flask](https://flask.palletsprojects.com/en/latest/).
* **Banco de Dados:** [SQLite](https://www.sqlite.org/index.html) para desenvolvimento e prototipagem.
* **Frontend:** HTML, CSS e JavaScript para uma interface de usuário responsiva e interativa.

## Como Rodar o Projeto Localmente (Instruções para Desenvolvimento)

Para configurar e rodar o FinançasControladas em sua máquina local, siga os passos abaixo:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO_GITHUB/FinancasControladas.git](https://github.com/SEU_USUARIO_GITHUB/FinancasControladas.git)
    cd FinancasControladas
    ```
    *(**Substitua `SEU_USUARIO_GITHUB` pelo seu nome de usuário do GitHub.**)*

2.  **Crie e ative o ambiente virtual:**
    ```bash
    # Para Windows:
    python -m venv venv
    .\venv\Scripts\activate

    # Para Linux/macOS:
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install Flask
    # Outras dependências serão adicionadas aqui conforme o projeto avança
    ```

4.  **Rode a aplicação Flask:**
    ```bash
    flask run
    ```
    *(Você verá uma mensagem indicando o endereço local, geralmente `http://127.0.0.1:5000/`)*

5.  **Acesse no navegador:**
    Abra seu navegador e vá para o endereço fornecido.

## Contribuição

Contribuições são bem-vindas! Se você faz parte da equipe ou deseja contribuir, por favor, siga as boas práticas de Git/GitHub:

1.  Faça um `fork` do repositório (se for um colaborador externo).
2.  Crie uma nova `branch` para sua funcionalidade ou correção (`git checkout -b feature/nome-da-feature`).
3.  Faça suas alterações e `commit` as mudanças (`git commit -m "feat: Adiciona nova funcionalidade X"`).
4.  Envie para sua `branch` (`git push origin feature/nome-da-feature`).
5.  Abra um `Pull Request` detalhando suas alterações.

## Equipe

* **[Fabio Borges/binhog29]** - Líder de Projeto & Backend
* **[NomBruno Borges/GitHub User do seu Colega]** - Frontend & UI/UX

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. *(Você pode criar este arquivo LICENSE depois, se quiser)*