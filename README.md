# Spotify Queuer

Projeto para enfileirar músicas utilizando um usuário específico

----------------------------

1. [Requerimentos](Requerimentos)
2. [Instalar](Instalar)
3. [Iniciar](Iniciar)

## Requerimentos

#### Geral

- [Docker](https://docs.docker.com/get-docker/)

#### Windows

- [WSL](https://docs.microsoft.com/pt-br/windows/wsl/install)
- [Ubuntu 20.04](https://www.microsoft.com/en-us/p/ubuntu-2004-lts/9n6svws3rx71#activetab=pivot:overviewtab)

## Instalar

#### Linux
* Instale o docker

#### Windows
* Ative o recurso WSL do Windows
* Inicie o docker
* Configure WSL no docker

#### Ambos

* Crie um arquivo .env com as seguintes variáveis:

  ```
  SPOTIPY_CLIENT_ID= seu-id-do-spotify
  SPOTIPY_CLIENT_SECRET= seu-secret-do-spotify
  SPOTIPY_REDIRECT_URI= http://localhost:5000/callback (Precisa definir isso no seu dashboard do Spotify)
  API_BASE=https://accounts.spotify.com/pt-BR/
  ```
* Rode o comando abaixo no terminal WSL ou no terminal da sua distribuição do linux:

  ```
  docker-compose up --build
  ```
  
## Iniciar

  Com o container instalado, apenas execute:
  
  ```
  docker-compose up 
  ```
  
