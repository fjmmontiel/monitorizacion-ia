<h1>iagmvps-front-atencion-cliente</h1>

- [Introducción](#introducción)
- [Documentación](#documentación)
  - [Nueva Arquitectura](#nueva-arquitectura)
    - [Storybook](#storybook)
- [Requisitos Previos](#requisitos-previos)
  - [Node 16+](#node-16)
  - [NPM 8+](#npm-8)
- [Instalación](#instalación)
  - [Repositorio](#repositorio)
- [Utilización](#utilización)
  - [Uso con mocks locales](#uso-con-mocks-locales)
  - [Uso con entronos de desarrollo](#uso-con-entornos-de-desarrollo)
- [Principales librerías y herramientas utilizadas](#principales-librerías-y-herramientas-utilizadas)
  - [React](#react)
  - [TypeScript](#typescript)
  - [styled-components](#styled-components)
  - [Jest](#jest)
  - [React Testing Library](#react-testing-library)

# Introducción

El proyecto ha sido creado con una arquitectura de [Monorepo](https://monorepo.tools/), utilizando [NPM Workspaces](https://docs.npmjs.com/cli/v8/using-npm/workspaces) y [Lerna](https://lerna.js.org/) para gestión de dependencias entre los módulos del monorepo.

# Documentación

La documentación para saber más acerca de la estructura de la aplicación leer la documentación en el [Portal del Desarrollador](https://storybookarq.unicajabanco.es/). En ella se provee la documentación actualmente de la librería de componententes de la nueva arquitectura de Unicaja, de la cual se sustenta esta aplicación.

## Nueva Arquitectura

La documentación de la librería de componententes de la nueva arquitectura de Unicaja, puede ser consultada [Portal del Desarrollador](https://storybookarq.unicajabanco.es/). Sus componentes son las principales herramientas para la configuración de las funcionalidades de esta aplicación. Para ello es preciso visualizar el storybook del proyecto de nueva arquitectura para su idoneidad respecto al diseño del proyecto.

### [Storybook](https://storybook.js.org/)

Entorno de desarrollo para componentes de interfaz de usuario. Le permite explorar una biblioteca de componentes, ver los diferentes estados de cada componente y desarrollar y probar componentes de forma interactiva. [Storybook de la Nueva Arquitectura](https://storybookarq.unicajabanco.es/)

# Requisitos Previos

Para la correcta utilización de la aplicación es necesario tener instaladas las siguientes herramientas:

## [Node 18+](https://nodejs.org/)

Un entorno de ejecución multiplataforma de código abierto para la capa del servidor basado en el lenguaje de programación JavaScript, asíncrono, con E/S de datos en una arquitectura dirigida por eventos y basado en el motor V8 de Node.js.

## [NPM 8+](https://docs.npmjs.com/)

Package manager para la plataforma Node JavaScript.

# Instalación

## Repositorio

Es preciso estar registrado al repositorio de la arquitectura de componentes https://central.unicaja.es/artifactory/webapp/#/home y obtener a traves de npm-repository
la información que acceso de nuestro usuario para ser seteada en el archivo .npmrc de nuestro equipo. Para ello es preciso seguir la guía de descarga de dependencias: https://devops.unicaja.es/confluence/pages/viewpage.action?spaceKey=DO&title=%5BNPM%5D+Descarga+de+dependencias

# Utilización

```sh
> npm install
```

```sh
> npm run build
```

## Uso con mocks locales

Para el uso de mocks locales es preciso tener instalado [Mockoon](https://mockoon.com/) para simular la gestión de las peticiones API. Sobre esta aplicación se debe incluir el archivo provisto en el repositorio de Nueva Arquitectura llamado `mockoon.json` o iniciar Mockoon en linea de comando:

```sh
> npm run start:mockoon
```

```sh
> sudo vim /etc/hosts
127.0.0.1      localhost
#127.0.0.1 featurepru20.unicajabanco.es
> npm run start
```

## Uso con entronos de desarrollo

```sh
> sudo vim /etc/hosts
127.0.0.1 localhost
127.0.0.1 featurepru20.unicajabanco.es
> npm run start
```

# Principales librerías y herramientas utilizadas

## [React](https://reactjs.org/)

Una biblioteca de JavaScript para crear interfaces de usuario.

## [TypeScript](https://www.typescriptlang.org/)

La librería fue escrita utilizando TypeScript, pero Typescript no es un prerrequisito para la utilización del la librería pues esa se publica como modules Javascript.

## [styled-components](https://styled-components.com/)

Un framework CSS-in-JS que permite escribir CSS dentro de JavaScript.

## [Jest](https://jestjs.io/)

JavaScript Testing Framework.

## [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)

Solución ligera para probar componentes React.

## [Mockoon](https://mockoon.com/)

Gestión de test y mocks para APIs
