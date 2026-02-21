export type Sesion = {
  idSesion: string;
  numTokensEntrada: number;
  numTokensSalida: number;
  coste: number;
  valoracion: number;
  comentarios: string;
  numMuestrasInteres: number;
  fechaInicio: Date;
  fechaFin: Date;
  duracion: number;
  centro: string;
  gestor: string;
  conversacion: string;
};

export type FilterOptions = {
  campo: string;
  valor: string;
};

export type SesionSortAndFilterOptions = {
  pagina: number | null;
  tamano: number | null;
  campoOrden: string | null;
  direccionOrden: string | null;
  filtros: FilterOptions[];
};
