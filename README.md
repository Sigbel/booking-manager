<p align="center">
 <img width="300px" src="https://res.cloudinary.com/sigbel/image/upload/v1663174185/projects/booking_simulator/Entrada_.png" align="center" alt="Entrada" />
 <h2 align="center">Booking Manager</h2>
 <p align="center">Faça um controle preciso das reservas do seu hotel!</p>
</p>
  <p align="center">
    <a href="https://github.com/Sigbel/Booking_Manager/issues">
      <img alt="Issues" src="https://img.shields.io/github/issues/sigbel/Booking_Manager?color=0088ff" />
    </a>
    <a href="https://github.com/anuraghazra/github-readme-stats/pulls">
      <img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/sigbel/Booking_Manager?color=0088ff" />
    </a>

  </p>
  <p align="center">
    <a href="#demonstração">Ver demonstração</a>
    ·
    <a href="https://github.com/sigbel/Booking_Manager/issues/new/choose">Reportar erros</a>
    ·
    <a href="https://github.com/sigbel/Booking_Manager/issues/new/choose">Solicitar recursos</a>
  </p>

# Tópicos

- [Cuidados Iniciais](#cuidados-iniciais)
- [Funcionalidades](#funcionalidades)
- [Demonstrativo](#demonstrativo)

# Cuidados Iniciais

Instale o MySql para prosseguir com os próximos passos, todos os downloads da versão comunitária estão presentes em [MySQL Community Downloads](https://dev.mysql.com/downloads/). Caso necessite de outras versões pode adquiri-las em [MySQL Downloads](https://www.mysql.com/downloads/).

Crie um usuário de sua escolha.

Para as configurações iniciais, acesse o arquivo **"utils"**.

- Por padrão o usuário é **"root"**. Ao criar um usuário diferente, altere o campo `user=` para o usuário criado. Caso tenha alterado a senha padrão de **"root"** ou criado um novo usuário, altere o campo `_password=`
- Caso necessite, altere o nome do banco de dados para um de sua escolha, por padrão o banco é definido como **"booking_manager"**.

Bibliotecas utilizadas (instalar antes de iniciar):
- `MySQLdb`, `pycep_correios`, `PyQt5`, `pandas`

_Nota: Somente estes parâmetros são costumizáveis, alterar qualquer outra propriedade resultará em erros na inicialização._

### Interfaces
- ##### Login
  - Interface inicial com login, dispondo de verificação de usuário e senha.

- ##### Interface Principal
  - Cadastro de Hóspedes
    - Cadastro de informações prioritárias para cada hóspede, contado com informações gerais, endereço e dados para contato.
  - Visualizar de Clientes
    - Visualização dos dados de cada cliente do hotel, contato com pesquisa por nome, id do cliente ou cpf.
  - Quartos
    - Visualização dos quartos, mediante entradas e saídas de hóspedes. Sendo possível averigar o hóspede presente no quarto, assim como suas informações.
  - Criar Reserva
    - Criação de reservas com base nos hóspedes cadastrados.
  - Visualizar Reservas
    - Visualização de todas as reservas registradas.
  - Check-in 
    - Entrada para o hóspede com reserva feita previamente.
  - Check-out
    - Saída para o hóspede com reserva e check-in realizados.
  - Visualizar Checks
    - Visualização de todos os check-ins e check-outs, assim como as reservas com data de entrada e saída no dia em questão.
  - Gerais
    - Contadores de reservas, quartos dispoíveis e quartos ocupados;
    - Barras de busca de reserva e hóspedes.

### Funcionalidades

- Checagem de CPF e endereços válidos no cadastro de hóspedes;
- Verificação e atribuição automática de quartos disponíveis para as datas estipuladas no ato da reserva;
- Verificações para Check-ins e Check-outs realizados fora das datas previstas de entrada e saída, respectivamente;
- Invalidação automática da reserva, caso o check-in não seja feito dentro da data entrada estipulada;

### Demonstrativo



<p align="right">
  <em> Figura 1 - Cadastro de Hóspedes </em>
  <img src="https://res.cloudinary.com/sigbel/image/upload/v1663195040/projects/booking_simulator/cadastro_h_i8ckvf.png" alt="Logo" title="Logo title">
</p>
<p align="right">
  <em> Figura 2 - Consulta de Clientes </em>
  <img src="https://res.cloudinary.com/sigbel/image/upload/v1663195041/projects/booking_simulator/consulta_clientes_ipvx7e.png" alt="Logo" title="Logo title">
</p>
<p align="right">
  <em> Figura 3 - Quartos </em>
  <img src="https://res.cloudinary.com/sigbel/image/upload/v1663195041/projects/booking_simulator/quartos_p956zo.png" alt="Logo" title="Logo title">
</p>
<p align="right">
  <em> Figura 4 - Criar Reserva </em>
  <img src="https://res.cloudinary.com/sigbel/image/upload/v1663195041/projects/booking_simulator/c_reserva_u7g5ir.png" alt="Logo" title="Logo title">
</p>
<p align="right">
  <em> Figura 5 - Visualizar Reservas </em>
  <img src="https://res.cloudinary.com/sigbel/image/upload/v1663195041/projects/booking_simulator/visu_reserva_htc2ub.png" alt="Logo" title="Logo title">
</p>
<p align="right">
  <em> Figura 6 - Check-IN </em>
  <img src="https://res.cloudinary.com/sigbel/image/upload/v1663195041/projects/booking_simulator/check_in_tpegqs.png" alt="Logo" title="Logo title">
</p>
<p align="right">
  <em> Figura 7 - Check-OUT </em>
  <img src="https://res.cloudinary.com/sigbel/image/upload/v1663195040/projects/booking_simulator/check_out_gxbnx3.png" alt="Logo" title="Logo title">
</p>
<p align="right">
  <em> Figura 8 - Visualizar Checks </em>
  <img src="https://res.cloudinary.com/sigbel/image/upload/v1663195041/projects/booking_simulator/visu_checks_v6ayly.png" alt="Logo" title="Logo title">
</p>

_Nota: Todas os dados contidos nas imagens são **fictícios**, sendo meramente representados com a finalidade de ilustrar o funcionamento do aplicativo._


