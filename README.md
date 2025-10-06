# RainTrack TCC

Este Trabalho de Conclusão de Curso (TCC) propõe o desenvolvimento do sistema 'RainTrack', focado no monitoramento meteorológico em tempo real. O sistema visa coletar e processar dados ambientais, facilitando a análise das condições climáticas e auxiliando na segurança pública e no planejamento urbano.

# Índice
* [Objetivo do Projeto](#objetivo-do-projeto)
* [Equipe](#Equipe)
* [Backlog do produto](#Product-Backlog)
* [Competências desenvolvidas](#competências-desenvolvidas)
* [Registro das Sprints](#Registro-das-Sprints)


### Trabalho de Conclusão de Curso

O RainTrack é um sistema de monitoramento meteorológico em tempo real desenvolvido para ajudar a prever e entender melhor as condições climáticas. Utilizando o microcontrolador ESP32 e o protocolo MQTT, o sistema coleta dados ambientais, como temperatura, umidade e precipitação, e os envia para uma plataforma de visualização.

A ideia por trás do RainTrack é proporcionar uma maneira simples e eficiente de acompanhar o clima, com um dashboard interativo que exibe os dados de forma visual e fácil de entender. Isso pode ser útil para diversas áreas, como segurança pública, planejamento urbano e até para antecipar desastres naturais causados por chuvas intensas.

Com esse projeto, buscamos otimizar o monitoramento do clima, tornando as informações mais acessíveis e ajudando na tomada de decisões para mitigar os impactos de eventos climáticos extremos.

# Equipe
|    Função     | Nome                                  |                                                                                                                                                      LinkedIn & GitHub                                                                                                                                                      |
| :-----------: | :------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| Team Member   | Bruno Oliveira | [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/bruno-oliveira-063911265/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/BrunoOliveira06) |
| Team Member   | Gustavo Gomes  | [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/gustavo-gomes-6a9a22320/) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](https://github.com/GustavoCostaGomes) |
| Team Member   | Igor Côrrea    | [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](LINKEDINIGOR) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)](GITHUBIGOR) |
| Team Member   | Thais Píres    | [![Linkedin Badge](https://img.shields.io/badge/Linkedin-blue?style=flat-square&logo=Linkedin&logoColor=white)](LINKEDINTHAIS) [![GitHub Badge](https://img.shields.io/badge/GitHub-111217?style=flat-square&logo=github&logoColor=white)]((https://github.com/ThaisPiresDosSantos)) |

# Objetivo do Projeto
O objetivo geral desse trabalho é desenvolver um sistema de monitoramento meteorológico automatizado, visando:
* Implementar um servidor Flask conectado a um banco de dados MySQL;
* Criar uma comunicação entre a estação meteorológica e o ESP32, utilizando o protocolo MQTT; 
* Desenvolver um dashboard interativo que apresente as informações meteorológicas; 
* Garantir a integridade e confiabilidade dos dados coletados, minimizando perdas.

## Tecnologias Utilizadas

* Git e GitHub
* Visual Studio Code
* Trello
* MySQL
* XAMPP
* Python
* Flask
* CSS
* JavaScript
* Highcharts
* ESP32
* MQTT
* Eclipse Mosquitto



# Product Backlog

| Rank | Prioridade | User Story                                                                                                                                              | Estimativa | Sprint |
|------|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|------------|--------|
| 1    | Alta       | Como sistema, quero receber dados via MQTT e armazenar no banco MySQL, para integrar as estações físicas ao sistema                                                     | 13          | 1      |
| 2    | Alta       | Como admin, quero cadastrar usuários com diferentes permissões, para controlar o acesso ao sistema                                                                     | 8          | 1      |
| 3    | Alta       | Como admin, quero visualizar minhas informações no perfil, para acompanhar meus dados cadastrados                                                | 5          | 1      |
| 4    | Alta       | Como admin, quero visualizar os gráficos de dados meteorológicos, para acompanhar as medições                                                 | 13          | 2      |
| 5    | Alta       | Como admin, quero cadastrar e editar estações meteorológicas, para gerenciar as fontes de dados                                                | 8          | 2      |
| 6    | Alta       | Como admin, quero cadastrar e editar parâmetros de medição (umidade, temperatura, pluviosidade etc.), para definir os dados que serão coletados                                                | 8          | 2      |
| 7    | Média       | Como admin, quero me registrar e fazer login, para acessar o sistema de forma segura                                                | 5          | 3      |
| 8    | Média       | Como admin, quero acessar a página inicial com informações resumidas, para ter visão geral do sistema                                                | 5          | 3      |
| 9   | Baixa      | Como admin, quero acessar a página “Sobre”, para entender o objetivo do sistema.     | 2          | 3      |
| 10   | Baixa      | Como admin, quero acessar o sistema em dispositivos móveis com interface responsiva para usabilidade melhor.      | 8          | 4      |
