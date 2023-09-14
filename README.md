<div align="center">
  <h1>
      Relatório do problema 1: Supermercado inteligente
  </h1>

  <h3>
    João Pedro da Silva Bastos
  </h3>

  <p>
    Engenharia de Computação – Universidade Estadual de Feira de Santana (UEFS)
    Av. Transnordestina, s/n, Novo Horizonte
    Feira de Santana – BA, Brasil – 44036-900
  </p>

  <center>joaopedro.silvabastos.splash@gmail.com</center>

</div>

# 1. Introdução

A evolução junto a tecnologia vem crescendo de forma exponencial em todas as áreas da sociedade. Técnicas e alternativas para reduzir custos e aumentar a produtividade tem surgido a todo momento. Isso também se aplica para os supermercados, que buscam maneiras de diminuir suas filas em caixas e melhorar a escolha dos seus produtos.

Um supermercado em Feira de Santana vem incorporando a infraestrutura de IoT para reduzir custos e aumentar a eficiência de suas operações, optando pelo uso da tecnologia Radio Frequency Identification (RFID) que dá suporte a leitura simultânea de diversos produtos.

Para a sua solução, foi utilizada a linguagem python e foi feito o uso de algumas de suas bibliotecas internas, como http.server, socket e treading, assim como o uso da biblioteca requests para realizar as requisições.

O programa foi feito em arquitetura de rede TCP/IP e além de ser testado em outros computadores, o programa que foi feito baseado em API REST também foi e pode ser testado pelo aplicativo Postman.

# 2. Metodologia

A implementação do projeto resultou em uma arquitetura final baseada em quatro blocos, O Caixa, que faz as solicitações para o servidor intermediário e para o leitor RFID, o Leitor RFID que faz a leitura das Tags e envia para os caixas, o controller, que é um servidor intermediário que é responsável por controlar as solicitações dos caixas para o servidor, realizando as requisições, e o servidor, que contém o "banco de dados", o carrinho de compras de cada cliente, o histórico geral de compras, e todas as funções referentes ao armazenamento manutenção de dados. Segue uma simples ilustração para tentar abstrair a arquitetura de uma forma mais linear.

![imagem de exemplo](https://github.com/JPBast0z/PBL-Redes/raw/main/ExemploSimplificadoArquitetura.png)

Para tentar explicar o funcionamento do programa em uma forma mais linear, vamos partir da sequência presente na imagem, que se inicia quando um leitor RFID faz a leitura das tags pela raspberry pi e envia para o caixa em questão com uma comunicação feita via socket. Antes de serem enviadas para o caixa, as tags são agrupadas em uma lista e enviadas em formato de string.

Partindo para o caixa, ele pode realizar algumas funções, como ler as tags RFID, Finalizar uma compra e visualizar os itens no carrinho. O caixa além de se comunicar com o leitor RFID também faz uma conexão via socket com o controller, evitando assim uma conexão direta com o servidor, evitando uma sobrecarga do mesmo em uma situação onde existam vários caixas acessando o servidor simultaneamente.
O envio das tags para o controller para que seja feita uma verificação no “banco de dados” é feita de forma individual, evitando que os envios ultrapassem os 1024 bytes em uma conexão socket. Sempre que uma tag é enviada é feita uma verificação para checar se a mesma corresponde a algum item presente no estoque, e sendo adicionadas ao carrinho caso esteja.

Partindo para o servidor intermediário (controller), ele mantém uma conexão via socket fixa com cada caixa, e em prol de evitar problemas de concorrência visto que vários caixas podem realizar requisições ao mesmo tempo, foi criada duas camadas de threads, uma principal associada a uma função chamada “create_thread” e a camada secundária, que fica dentro desta função e é responsável por criar um thread exclusiva para cada novo caixa que se conectar com o servidor intermediário.

Dentro do servidor estão presentes os dicionários responsáveis por armazenar as informações dos caixas e do “banco de dados”, e também as funções da API que serão requisitadas pelo controller.
Esse “Banco de dados” consiste em dicionários que guardam informações de maneira organizada de fácil acesso para as requisições. Existem 3 dicionários principais, um responsável por armazenar as tags, seus produtos associados e suas características, tais como preço e quantidade presente no estoque. Outro armazena o carrinho de compras atual de cada caixa, e o outro guarda as informações de todas as compras já realizadas.

Para buscar e atualizar os dados, foram utilizadas requisições HTTP com base  nas funcionalidades GET e POST, respectivamente. Para fazer uso delas foram criadas rotas específicas diferentes a cada função desejada, segue as rotas e para que são utilizadas no programa.
Rotas GET:

- http://localhost:3003/id/[CÓDIGO DO PRODUTO]: Verifica se o produto está presente no estoque, caso esteja ele é colocado no carrinho.
- http://localhost:3003/visualizar_carrinho/[HOST DO CAIXA]: Retorna os itens presentes no carrinho de um caixa específico naquele momento, salientando que os carrinhos são atualizados em tempo real.
- http://localhost:3003/historico_geral: Retorna o histórico de todas as compras já feitas.

Rotas POST:
- http://localhost:3003/carrinho: Adiciona um produto específico ao carrinho de compras de um caixa.
- http://localhost:3003/compra: Verifica se existem itens suficientes para realizar uma compra, caso existam, a compra é registrada no histórico geral e o carrinho é limpo.
- http://localhost:3003/acesso_caixa: É responsável por bloquear e liberar o acesso dos caixas ao servidor. Caso um caixa esteja bloqueado, ao acessar esta função ele será liberado, e vice-versa.
- http://localhost:3003/verifica_caixa: Esta função é responsável por verificar o acesso dos caixas, permitindo que eles realizem suas solicitações apenas se estiverem liberados.

As rotas podem ser testadas tanto pelo próprio programa em si quanto pelo postman ou insomnia.

# 3. Resultados 

Para o funcionamento do programa, o Servidor deve ser iniciado primeiramente, em seguida o controller e o Leitor RFID e por último os caixas.
Partindo do ponto de vista do cliente, será mostrado um menu interativo simples, que conta com 4 opções: ler tags, finalizar a compra e ver carrinho e inserir o produto manualmente. Caso o cliente tente finalizar uma compra sem que tenha algum item no carrinho, será retornada uma mensagem informando que o carrinho está vazio, o mesmo vale para a opção de visualizar o carrinho de compras.
A partir do momento que o cliente solicita a leitura das tags ou insere manualmente, o pedido é feito para o leitor RFID, que envia as tags para o caixa e em seguidas são enviadas uma a uma para o controller para que seja feita a verificação se o item está presente no estoque. Caso o item esteja presente no estoque o produto é adicionado ao carrinho de compras, e a partir deste momento é possível visualizar os itens contidos no carrinho ou finalizar uma compra.
Ao finalizar uma compra é verificado se existem quantidades suficientes no estoque para que a venda possa ocorrer, em caso de sucesso, a venda é finalizada e o carrinho é limpo.

O administrador tem acesso às suas funções pelo programa postman, onde pode utilizar a rota desejada e realizar o que seja necessário. Tendo acesso ao bloqueio e liberação dos caixas, histórico de compras, compras em tempo real e todas as demais funcionalidades.

Graças a arquitetura implementada é possível que exista o acesso de múltiplos caixas simultaneamente, contando também com uma interface simples e de fácil entendimento para os usuários.

# 4. Conclusão

Portanto, é possível concluir que a maioria dos objetivos propostos pelo problema foram alcançados, empregando conceitos tanto de concorrência quanto de conectividade. Vale ressaltar o aprendizado adquirido sobre os conceitos utilizados e tecnologias específicas, como a utilização de docker, http.server e das requisições.
É importante também ressaltar a falta de cumprimento em uma dos objetivos, que foi a utilização do docker, devido a alguns problemas enfrentados na tentativa de sua utilização.
Isso pode ser proposto como possível melhoria para o sistema, possibilitando que ele rode com mais facilidade em mais computadores. Uma melhoria que também pode ser implementada é o uso de diferentes leitores RIFD para cada caixa, evitando problemas com concorrência e leituras incorretas. Também pode ser implementada uma interface exclusiva para o administrador, facilitando o seu acesso às funcionalidades.

# 4. Referencias
